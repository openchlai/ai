import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'

// Role constants
const ROLES = {
  COUNSELLOR: 'counsellor',
  SUPERVISOR: 'supervisor',
  CASE_MANAGER: 'case_manager',
  CASE_WORKER: 'case_worker',
  PARTNER: 'partner',
  MEDIA_ACCOUNT: 'media_account',
  ADMINISTRATOR: 'administrator'
}

const ROLE_ID_MAP = {
  1: ROLES.COUNSELLOR,
  2: ROLES.SUPERVISOR,
  3: ROLES.CASE_MANAGER,
  4: ROLES.CASE_WORKER,
  5: ROLES.PARTNER,
  6: ROLES.MEDIA_ACCOUNT,
  99: ROLES.ADMINISTRATOR
}

const ROLE_DISPLAY_NAMES = {
  1: "Counsellor",
  2: "Supervisor",
  3: "Case Manager",
  4: "Case Worker",
  5: "Partner",
  6: "Media Account",
  99: "Administrator"
}

const ROLE_PERMISSIONS = {
  [ROLES.COUNSELLOR]: ['dashboard', 'cases', 'calls', 'messages', 'wallboard', 'faqs'],
  [ROLES.SUPERVISOR]: ['dashboard', 'cases', 'calls', 'messages', 'wallboard', 'qa', 'reports', 'faqs'],
  [ROLES.CASE_MANAGER]: ['dashboard', 'cases', 'calls', 'messages', 'wallboard', 'qa', 'reports', 'faqs'],
  [ROLES.CASE_WORKER]: ['dashboard', 'cases', 'faqs'],
  [ROLES.PARTNER]: ['dashboard'],
  [ROLES.MEDIA_ACCOUNT]: ['dashboard'],
  [ROLES.ADMINISTRATOR]: ['dashboard', 'cases', 'calls', 'messages', 'wallboard', 'activities', 'qa', 'users', 'reports', 'categories', 'faqs']
}

const DEFAULT_PERMISSIONS = ['dashboard', 'cases', 'calls', 'faqs']

export const useAuthStore = defineStore('auth', {
  state: () => ({
    sessionId: null,
    userId: null,
    username: null,
    userRole: null,
    profile: null,
    loading: false,
    error: null,
  }),

  getters: {
    // CRITICAL: User is only authenticated if ALL required data exists
    isAuthenticated: (state) => {
      return !!(state.sessionId && state.userId && state.username && state.userRole)
    },

    roleName: (state) => {
      if (!state.userRole) return null
      return ROLE_ID_MAP[state.userRole] || null
    },

    roleDisplayName: (state) => {
      if (!state.userRole) return 'User'
      return ROLE_DISPLAY_NAMES[state.userRole] || 'User'
    },

    roleTitle: (state) => {
      if (!state.userRole) return 'User'
      return ROLE_DISPLAY_NAMES[state.userRole] || 'User'
    },

    isCounsellor: (state) => state.userRole === 1 || state.userRole === '1',
    isSupervisor: (state) => [2, 3, 99].includes(state.userRole) || [2, 3, 99].includes(parseInt(state.userRole)),
    isCaseManager: (state) => state.userRole === 3 || state.userRole === '3',
    isCaseWorker: (state) => state.userRole === 4 || state.userRole === '4',
    isPartner: (state) => state.userRole === 5 || state.userRole === '5',
    isMediaAccount: (state) => state.userRole === 6 || state.userRole === '6',
    isAdministrator: (state) => state.userRole === 99 || state.userRole === '99',

    // Permission check for UI elements
    canExport: (state) => [2, 3, 99].includes(state.userRole) || [2, 3, 99].includes(parseInt(state.userRole)),
    canDelete: (state) => [99].includes(state.userRole) || [99].includes(parseInt(state.userRole)),
    canManageUsers: (state) => [3, 99].includes(state.userRole) || [3, 99].includes(parseInt(state.userRole)),
    isAgent: (state) => [1, 4].includes(state.userRole) || [1, 4].includes(parseInt(state.userRole)),

    isMainRole: (state) => {
      const mainRoles = [1, 2, 3, 4, 99, '1', '2', '3', '4', '99']
      return mainRoles.includes(state.userRole)
    },

    userDisplayName: (state) => state.username || state.profile?.username || 'User',

    userInitials: (state) => {
      const name = state.username || state.profile?.username || 'U'
      return name.charAt(0).toUpperCase()
    },

    permissions: (state) => {
      const role = ROLE_ID_MAP[state.userRole]
      return role ? ROLE_PERMISSIONS[role] || DEFAULT_PERMISSIONS : DEFAULT_PERMISSIONS
    }
  },

  actions: {
    hasPermission(page) {
      return this.permissions.includes(page)
    },

    async login(username, password) {
      this.loading = true
      this.error = null

      try {
        console.log('🔐 Attempting login...')

        const credentials = btoa(`${username}:${password}`)

        // Use POST request with Basic Auth (matching control UI)
        const response = await axiosInstance.post('api/', '', {
          headers: {
            'Authorization': `Basic ${credentials}`,
            'Content-Type': 'text/plain',
          },
        })

        console.log('✅ Login response:', response.data)

        const sessionData = response.data?.ss?.[0]
        if (!sessionData || !sessionData[0]) {
          console.error('❌ No session data in response:', response.data)
          throw new Error('No session data returned from server')
        }

        // Extract ALL required data
        this.sessionId = sessionData[0]
        this.userId = sessionData[1]
        this.username = sessionData[2]
        this.userRole = sessionData[3]
        // Create profile object from auth array/object
        const rawAuth = response.data.auth

        // Handle array-based auth response if applicable
        if (Array.isArray(rawAuth) && rawAuth.length > 0) {
          const authRow = rawAuth[0]
          // Create a mapped profile if keys are known, otherwise store raw
          // Assuming keys might be in response.data.auth_k (keys)
          const keys = response.data.auth_k || {}

          // Map keys to values
          if (keys) {
            const mappedProfile = {}
            Object.keys(keys).forEach(key => {
              const idx = keys[key][0] // Indicies are usually arrays like [0]
              mappedProfile[key] = authRow[idx]
            })
            this.profile = mappedProfile
          } else {
            this.profile = authRow
          }
        } else {
          this.profile = rawAuth?.[0] || null
        }

        // VALIDATE: All required fields must exist
        if (!this.sessionId || !this.userId || !this.username || !this.userRole) {
          console.error('❌ Incomplete authentication data')
          throw new Error('Incomplete authentication data from server')
        }

        // Store ALL data in localStorage
        localStorage.setItem('session-id', this.sessionId)
        localStorage.setItem('user-id', this.userId)
        localStorage.setItem('username', this.username)
        localStorage.setItem('user-role', this.userRole)
        if (this.profile) {
          localStorage.setItem('user-profile', JSON.stringify(this.profile))
        }

        axiosInstance.defaults.headers.common['Session-Id'] = this.sessionId

        console.log('✅ Login successful!')
        return true

      } catch (err) {
        console.error('❌ Login failed:', err)
        this.clearAuthData()
        this.error = err.response?.data?.message || 'Invalid username or password'
        return false
      } finally {
        this.loading = false
      }
    },

    logout() {
      console.log('🚪 Logging out...')
      this.clearAuthData()
    },

    // Clear all auth data from state and localStorage
    clearAuthData() {
      this.sessionId = null
      this.userId = null
      this.username = null
      this.userRole = null
      this.profile = null

      localStorage.removeItem('session-id')
      localStorage.removeItem('user-id')
      localStorage.removeItem('username')
      localStorage.removeItem('user-role')
      localStorage.removeItem('user-profile')

      // Clear Telephony state
      localStorage.removeItem('sipEnabled')
      localStorage.removeItem('sipConnected')
      localStorage.removeItem('queueStatus')

      delete axiosInstance.defaults.headers.common['Session-Id']
    },

    // Initialize auth state
    initializeAuth() {
      const sessionId = localStorage.getItem('session-id')
      const userId = localStorage.getItem('user-id')
      const username = localStorage.getItem('username')
      const userRole = localStorage.getItem('user-role')
      const userProfile = localStorage.getItem('user-profile')

      if (!sessionId || !userId || !username || !userRole) {
        this.clearAuthData()
        return
      }

      this.sessionId = sessionId
      this.userId = userId
      this.username = username
      this.userRole = parseInt(userRole)

      if (userProfile) {
        try {
          this.profile = JSON.parse(userProfile)
        } catch (e) {
          console.error('Failed to parse user profile from storage', e)
        }
      }

      axiosInstance.defaults.headers.common['Session-Id'] = sessionId
    }
  }
})
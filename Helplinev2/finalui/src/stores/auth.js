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

    isCounsellor: (state) => state.userRole === 1 || state.userRole === '1',
    isSupervisor: (state) => state.userRole === 2 || state.userRole === '2',
    isCaseManager: (state) => state.userRole === 3 || state.userRole === '3',
    isCaseWorker: (state) => state.userRole === 4 || state.userRole === '4',
    isPartner: (state) => state.userRole === 5 || state.userRole === '5',
    isMediaAccount: (state) => state.userRole === 6 || state.userRole === '6',
    isAdministrator: (state) => state.userRole === 99 || state.userRole === '99',

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
      return role ? ROLE_PERMISSIONS[role] || [] : []
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

        const response = await axiosInstance.get('/api/', {
          headers: {
            'Authorization': `Basic ${credentials}`,
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
        this.profile = response.data.auth?.[0] || null

        // VALIDATE: All required fields must exist
        if (!this.sessionId || !this.userId || !this.username || !this.userRole) {
          console.error('❌ Incomplete authentication data')
          console.error('SessionId:', this.sessionId)
          console.error('UserId:', this.userId)
          console.error('Username:', this.username)
          console.error('UserRole:', this.userRole)
          throw new Error('Incomplete authentication data from server')
        }

        console.log('🎫 Session ID:', this.sessionId)
        console.log('👤 User ID:', this.userId)
        console.log('📛 Username:', this.username)
        console.log('🔑 User Role:', this.userRole)
        console.log('👔 Role Display:', this.roleDisplayName)

        // Store ALL data in localStorage
        localStorage.setItem('session-id', this.sessionId)
        localStorage.setItem('user-id', this.userId)
        localStorage.setItem('username', this.username)
        localStorage.setItem('user-role', this.userRole)

        axiosInstance.defaults.headers.common['Session-Id'] = this.sessionId

        console.log('✅ Login successful!')
        return true

      } catch (err) {
        console.error('❌ Login failed:', err)
        console.error('❌ Error response:', err.response)

        // Clear any partial data
        this.clearAuthData()

        if (err.response) {
          const errorMsg = err.response.data?.errors?.[0]?.[1] ||
            err.response.data?.message ||
            err.response.data?.error ||
            'Invalid username or password'

          this.error = errorMsg
          console.error('❌ Server error:', errorMsg)
        } else if (err.request) {
          this.error = 'Unable to connect to server. Please try again.'
          console.error('❌ No response received')
        } else {
          this.error = err.message || 'Login failed. Please try again.'
          console.error('❌ Error:', err.message)
        }

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

      delete axiosInstance.defaults.headers.common['Session-Id']
    },

    // Initialize auth state - STRICT validation
    initializeAuth() {
      const sessionId = localStorage.getItem('session-id')
      const userId = localStorage.getItem('user-id')
      const username = localStorage.getItem('username')
      const userRole = localStorage.getItem('user-role')

      console.log('🔄 Initializing auth from localStorage...')
      console.log('Session ID:', sessionId)
      console.log('User ID:', userId)
      console.log('Username:', username)
      console.log('User Role:', userRole)

      // CRITICAL: ALL fields must exist, or authentication is invalid
      if (!sessionId || !userId || !username || !userRole) {
        console.warn('⚠️ Incomplete auth data in localStorage - clearing all data')
        this.clearAuthData()
        return
      }

      // Restore state
      this.sessionId = sessionId
      this.userId = userId
      this.username = username
      this.userRole = parseInt(userRole) // Convert back to number

      axiosInstance.defaults.headers.common['Session-Id'] = sessionId

      console.log('✅ Auth initialized successfully')
      console.log('👤 User ID:', this.userId)
      console.log('📛 Username:', this.username)
      console.log('🔑 User Role:', this.userRole)
      console.log('👔 Role Display:', this.roleDisplayName)
      console.log('🛡️ Permissions:', this.permissions)
    },
  },
})
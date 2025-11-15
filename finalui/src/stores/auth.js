import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    sessionId: localStorage.getItem('session-id') || null,
    profile: null,
    loading: false,
    error: null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.sessionId,
  },

  actions: {
    async login(username = 'test', password = 'p@ssw0rd') {
      this.loading = true
      this.error = null

      try {
        // ✅ Encode credentials (Base64)
        const credentials = btoa(`${username}:${password}`)

        // ✅ Send login request exactly how the backend expects
        const response = await axiosInstance.post('/api/', {
          headers: {
            Authorization: `Basic ${credentials}`,
          },
        })

        console.log('✅ Login response:', response.data)

        const sessionId = response.data?.ss?.[0]?.[0]
        if (!sessionId) throw new Error('No session ID returned')

        this.sessionId = sessionId
        this.profile = response.data.Profile || null

        localStorage.setItem('session-id', sessionId)
        return true
      } catch (err) {
        console.error('❌ Login failed:', err)
        this.error =
          err.response?.data?.errors?.[0]?.[1] ||
          err.message ||
          'Login failed'
        return false
      } finally {
        this.loading = false
      }
    },

    logout() {
      this.sessionId = null
      this.profile = null
      localStorage.removeItem('session-id')
    },
  },
})

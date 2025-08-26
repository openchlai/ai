
// will get back to this later
import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios';// uses the updated axios with session handling

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
    async login(username, password) {
      this.loading = true
      this.error = null

      try {
        const credentials = btoa(`${username}:${password}`) // Base64 encode

        // Send login request - do NOT send Bearer token here
        const response = await axiosInstance.post('/', {}, {
          headers: {
            'XAuthorization': `Basic ${credentials}`
          }
        })

        const sessionId = response.data.ss?.[0]?.[0]
        if (!sessionId) throw new Error('No session ID returned')

        this.sessionId = sessionId
        this.profile = response.data.Profile || null

        localStorage.setItem('session-id', sessionId)
        return true
      } catch (err) {
        this.error = err.response?.data?.errors?.[0]?.[1] || 'Login failed'
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

    async fetchProfile() {
      if (!this.sessionId) throw new Error('Not authenticated')
      const response = await axiosInstance.get('/eproc/users/profile')
      this.profile = response.data
    }
  }
})

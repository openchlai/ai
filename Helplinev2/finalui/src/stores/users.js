// src/stores/users.js
import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'
import { useAuthStore } from './auth'

export const useUserStore = defineStore('userStore', {
  state: () => ({
    users: [],
    users_k: {},
    users_ctx: [],
    raw: {},
    loading: false,
    error: null,
    userCount: 0,
  }),

  actions: {
    // Helper to get auth headers
    getAuthHeaders() {
      const authStore = useAuthStore()
      return {
        'Session-Id': authStore.sessionId
      }
    },

    // 1. List Users
    async listUsers(params = {}) {
      this.loading = true
      this.error = null

      try {
        const { data } = await axiosInstance.get('api/users/', {
          params,
          headers: this.getAuthHeaders()
        })

        console.log('Fetched users:', data)
        this.raw = data
        this.users = data.users || []
        this.users_k = data.users_k || {}
        this.users_ctx = data.users_ctx || []
        this.userCount = this.users.length
      } catch (err) {
        this.error = err.message || 'Failed to fetch users'
      } finally {
        this.loading = false
      }
    },

    // 2. View User
    async viewUser(userId) {
      try {
        const { data } = await axiosInstance.get(`api/users/${userId}`, {
          headers: this.getAuthHeaders()
        })
        return data
      } catch (err) {
        throw new Error(err.message || 'Failed to fetch user details')
      }
    },

    // 3. Create User
    async createUser(payload) {
      try {
        const { data } = await axiosInstance.post('api/users', payload, {
          headers: {
            ...this.getAuthHeaders(),
            'Content-Type': 'application/json'
          }
        })
        return data
      } catch (err) {
        throw new Error(err.message || 'Failed to create user')
      }
    },

    // 4. Edit User
    async editUser(userId, payload) {
      try {
        const { data } = await axiosInstance.post(`api/users/${userId}`, payload, {
          headers: {
            ...this.getAuthHeaders(),
            'Content-Type': 'application/json'
          }
        })
        return data
      } catch (err) {
        throw new Error(err.message || 'Failed to edit user')
      }
    },

    // 5. Reset Password
    async resetPassword(userId) {
      try {
        this.loading = true
        this.error = null

        console.log('🔄 Resetting password for user:', userId)

        const { data, status } = await axiosInstance.post(
          `api/resetAuth/${userId}`,
          { '.id': userId },
          {
            headers: {
              ...this.getAuthHeaders(),
              'Content-Type': 'application/json'
            }
          }
        )

        console.log('✅ Password reset response:', data, 'Status:', status)
        return { data, status }
      } catch (err) {
        console.error('❌ Error resetting password:', err)
        this.error = err.message || 'Failed to reset password'
        throw new Error(err.message || 'Failed to reset password')
      } finally {
        this.loading = false
      }
    },

    // 6. CSV Download
    async downloadCSV(params = {}) {
      try {
        const response = await axiosInstance.get('api/users/', {
          params: { ...params, csv: 1 },
          headers: this.getAuthHeaders(),
          responseType: 'blob'
        })
        return response.data
      } catch (err) {
        throw new Error(err.message || 'Failed to download CSV')
      }
    },

    // 7. Pivot Reports
    async getPivotReport(params = {}) {
      try {
        const { data } = await axiosInstance.get('api/users/rpt', {
          params,
          headers: this.getAuthHeaders()
        })
        return data
      } catch (err) {
        throw new Error(err.message || 'Failed to fetch pivot report')
      }
    }
  }
})
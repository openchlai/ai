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
    // Pagination state
    pagination: {
      offset: 0,
      limit: 20,
      currentPage: 1,
      totalRecords: 0,
      rangeStart: 1,
      rangeEnd: 20
    }
  }),

  getters: {
    // Pagination getters
    totalRecords: (state) => state.pagination.totalRecords,
    currentPage: (state) => state.pagination.currentPage,
    pageSize: (state) => state.pagination.limit,
    totalPages: (state) => Math.ceil(state.pagination.totalRecords / state.pagination.limit) || 1,
    hasNextPage: (state) => state.pagination.rangeEnd < state.pagination.totalRecords,
    hasPrevPage: (state) => state.pagination.currentPage > 1,
    paginationInfo: (state) => ({
      rangeStart: state.pagination.rangeStart,
      rangeEnd: state.pagination.rangeEnd,
      total: state.pagination.totalRecords,
      currentPage: state.pagination.currentPage,
      totalPages: Math.ceil(state.pagination.totalRecords / state.pagination.limit) || 1
    })
  },

  actions: {
    // Helper to get auth headers
    getAuthHeaders() {
      const authStore = useAuthStore()
      return {
        'Session-Id': authStore.sessionId
      }
    },

    // Parse users_ctx to update pagination state
    parsePaginationContext(ctx) {
      if (ctx && ctx[0] && Array.isArray(ctx[0])) {
        const [offset, limit, rangeStart, rangeEnd, total] = ctx[0]
        this.pagination.offset = parseInt(offset) || 0
        this.pagination.limit = parseInt(limit) || 20
        this.pagination.rangeStart = parseInt(rangeStart) || 1
        this.pagination.rangeEnd = parseInt(rangeEnd) || 20
        this.pagination.totalRecords = parseInt(total) || 0
        this.pagination.currentPage = Math.floor(this.pagination.offset / this.pagination.limit) + 1
      }
    },

    // 1. List Users with pagination support
    async listUsers(params = {}) {
      this.loading = true
      this.error = null

      try {
        // Build pagination params
        const paginationParams = {
          _c: params._c || this.pagination.limit,
          _o: params._o !== undefined ? params._o : this.pagination.offset,
          _a: 0,
          ...params
        }
        delete paginationParams.page

        const { data } = await axiosInstance.get('api/users/', {
          params: paginationParams,
          headers: this.getAuthHeaders()
        })

        console.log('Fetched users:', data)
        this.raw = data
        this.users = data.users || []
        this.users_k = data.users_k || {}
        this.users_ctx = data.users_ctx || []
        this.userCount = this.pagination.totalRecords || this.users.length

        // Parse pagination context
        this.parsePaginationContext(data.users_ctx)
      } catch (err) {
        this.error = err.message || 'Failed to fetch users'
      } finally {
        this.loading = false
      }
    },

    // Go to next page
    async nextPage(filters = {}) {
      if (!this.hasNextPage) return
      const newOffset = this.pagination.offset + this.pagination.limit
      await this.listUsers({ ...filters, _o: newOffset, _c: this.pagination.limit })
    },

    // Go to previous page
    async prevPage(filters = {}) {
      if (!this.hasPrevPage) return
      const newOffset = Math.max(0, this.pagination.offset - this.pagination.limit)
      await this.listUsers({ ...filters, _o: newOffset, _c: this.pagination.limit })
    },

    // Go to specific page
    async goToPage(page, filters = {}) {
      const newOffset = (page - 1) * this.pagination.limit
      await this.listUsers({ ...filters, _o: newOffset, _c: this.pagination.limit })
    },

    // Change page size
    async setPageSize(size, filters = {}) {
      this.pagination.limit = size
      this.pagination.offset = 0
      await this.listUsers({ ...filters, _o: 0, _c: size })
    },

    // Reset pagination to first page
    resetPagination() {
      this.pagination.offset = 0
      this.pagination.currentPage = 1
      this.pagination.rangeStart = 1
      this.pagination.rangeEnd = this.pagination.limit
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
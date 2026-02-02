// src/stores/qa.js
import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'
import { useAuthStore } from './auth'

export const useQAStore = defineStore('qa', {
  state: () => ({
    qas: [],
    qas_k: {},
    qas_ctx: [],
    qaCount: 0,
    loading: false,
    error: null,
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

    // Parse qas_ctx to update pagination state
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

    async listQA(params = {}) {
      try {
        this.loading = true

        // Build pagination params
        const paginationParams = {
          _c: params._c || this.pagination.limit,
          _o: params._o !== undefined ? params._o : this.pagination.offset,
          _a: 0,
          ...params
        }
        delete paginationParams.page

        const { data } = await axiosInstance.get('api/qas/', {
          params: paginationParams,
          headers: this.getAuthHeaders()
        })

        // Store QA data and key mappings
        this.qas = data.qas || data.qa || []
        this.qas_k = data.qas_k || data.qa_k || {}
        this.qas_ctx = data.qas_ctx || data.qa_ctx || []
        this.qaCount = data.qa_nb ? data.qa_nb[0][1] : this.pagination.totalRecords || this.qas.length

        // Parse pagination context
        this.parsePaginationContext(this.qas_ctx)
      } catch (err) {
        this.error = err.message || 'Failed to fetch QA list'
        throw err
      } finally {
        this.loading = false
      }
    },

    // Go to next page
    async nextPage(filters = {}) {
      if (!this.hasNextPage) return
      const newOffset = this.pagination.offset + this.pagination.limit
      await this.listQA({ ...filters, _o: newOffset, _c: this.pagination.limit })
    },

    // Go to previous page
    async prevPage(filters = {}) {
      if (!this.hasPrevPage) return
      const newOffset = Math.max(0, this.pagination.offset - this.pagination.limit)
      await this.listQA({ ...filters, _o: newOffset, _c: this.pagination.limit })
    },

    // Go to specific page
    async goToPage(page, filters = {}) {
      const newOffset = (page - 1) * this.pagination.limit
      await this.listQA({ ...filters, _o: newOffset, _c: this.pagination.limit })
    },

    // Change page size
    async setPageSize(size, filters = {}) {
      this.pagination.limit = size
      this.pagination.offset = 0
      await this.listQA({ ...filters, _o: 0, _c: size })
    },

    // Reset pagination to first page
    resetPagination() {
      this.pagination.offset = 0
      this.pagination.currentPage = 1
      this.pagination.rangeStart = 1
      this.pagination.rangeEnd = this.pagination.limit
    },

    async createQA(payload) {
      try {
        this.loading = true
        this.error = null
        
        const { data } = await axiosInstance.post('api/qas', payload, {
          headers: {
            ...this.getAuthHeaders(),
            'Content-Type': 'application/json'
          }
        })
        
        return data
      } catch (err) {
        this.error = err.message || 'Failed to create QA'
        throw err
      } finally {
        this.loading = false
      }
    },
  },
})
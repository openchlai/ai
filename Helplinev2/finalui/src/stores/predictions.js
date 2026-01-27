// stores/predictions.js
import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'
import { useAuthStore } from './auth'

export const usePredictionsStore = defineStore('predictions', {
    state: () => ({
        predictions: [],
        predictions_k: {},
        predictions_ctx: [],
        loading: false,
        error: null,
        // Pagination state
        pagination: {
            offset: 0,
            limit: 20,
            rangeStart: 1,
            rangeEnd: 20,
            totalRecords: 0,
            currentPage: 1
        }
    }),

    getters: {
        paginationInfo: (state) => ({
            rangeStart: state.pagination.rangeStart,
            rangeEnd: state.pagination.rangeEnd,
            total: state.pagination.totalRecords,
            currentPage: state.pagination.currentPage,
            totalPages: Math.ceil(state.pagination.totalRecords / state.pagination.limit) || 1
        }),
        hasNextPage: (state) => state.pagination.rangeEnd < state.pagination.totalRecords,
        hasPrevPage: (state) => state.pagination.currentPage > 1
    },

    actions: {
        getAuthHeaders() {
            const authStore = useAuthStore()
            return { 'Session-Id': authStore.sessionId }
        },

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

        async listPredictions(params = {}) {
            this.loading = true
            this.error = null
            try {
                const queryParams = {
                    src: 'aii',
                    _c: params._c || this.pagination.limit,
                    _o: params._o !== undefined ? params._o : this.pagination.offset,
                    ...params
                }

                const { data } = await axiosInstance.get('api/pmessages/', {
                    params: queryParams,
                    headers: this.getAuthHeaders()
                })

                this.predictions = data.pmessages || []
                this.predictions_k = data.pmessages_k || {}
                this.predictions_ctx = data.pmessages_ctx || []
                this.parsePaginationContext(data.pmessages_ctx)

                return data
            } catch (err) {
                this.error = err.message
                throw err
            } finally {
                this.loading = false
            }
        },

        async nextPage(filters = {}) {
            if (!this.hasNextPage) return
            const newOffset = this.pagination.offset + this.pagination.limit
            await this.listPredictions({ ...filters, _o: newOffset })
        },

        async prevPage(filters = {}) {
            if (!this.hasPrevPage) return
            const newOffset = Math.max(0, this.pagination.offset - this.pagination.limit)
            await this.listPredictions({ ...filters, _o: newOffset })
        },

        async goToPage(page, filters = {}) {
            const newOffset = (page - 1) * this.pagination.limit
            await this.listPredictions({ ...filters, _o: newOffset })
        },

        async setPageSize(size, filters = {}) {
            this.pagination.limit = size
            this.pagination.offset = 0
            await this.listPredictions({ ...filters, _o: 0, _c: size })
        },

        resetPagination() {
            this.pagination.offset = 0
            this.pagination.currentPage = 1
            this.pagination.rangeStart = 1
            this.pagination.rangeEnd = this.pagination.limit
        }
    }
})

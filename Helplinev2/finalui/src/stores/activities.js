// src/stores/activitiesStore.js
import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'
import { useAuthStore } from './auth'

export const useActivitiesStore = defineStore('activitiesStore', {
  state: () => ({
    activities: [],      // array of activities (raw array format)
    activities_k: {},    // metadata keys
    activities_ctx: [],  // context (pagination etc.)
    raw: {},             // full API response
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
    activityCount: (state) => state.activities?.length ?? 0,

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
    }),

    // Get activity by ID
    getActivityById: (state) => (id) => {
      const index = parseInt(state.activities_k?.id?.[0] ?? 0)
      return state.activities.find(activity => activity[index] === id) || null
    },

    // Get activities by case ID
    getActivitiesByCaseId: (state) => (caseId) => {
      const caseIdIndex = parseInt(state.activities_k?.case_id?.[0] ?? -1)
      if (caseIdIndex === -1) return []
      return state.activities.filter(activity => activity[caseIdIndex] === caseId)
    },

    // Get activities by action type
    getActivitiesByAction: (state) => (action) => {
      const actionIndex = parseInt(state.activities_k?.action?.[0] ?? -1)
      if (actionIndex === -1) return []
      return state.activities.filter(activity => activity[actionIndex] === action)
    },

    // Getter to return activities with formatted timestamps
    formattedActivities: (state) => {
      const createdOnIndex = parseInt(state.activities_k?.created_on?.[0] ?? -1)
      if (createdOnIndex === -1) return []

      return state.activities.map(activity => {
        const timestamp = activity[createdOnIndex]
        let readableDate = ''
        if (timestamp) {
          const dateObj = new Date(Number(timestamp) * 1000)
          readableDate = dateObj.toLocaleString()
        }
        return {
          ...activity,
          readableDate
        }
      })
    },

    // Helper to map single activity array to object
    mapActivityToObject: (state) => (activityArray) => {
      const obj = {}
      for (const [fieldName, fieldInfo] of Object.entries(state.activities_k)) {
        const index = fieldInfo[0]
        obj[fieldName] = activityArray[index] || ''
      }
      return obj
    },

    // Get all activities as objects
    activitiesAsObjects: (state) => {
      return state.activities.map(activityArray => {
        const obj = {}
        for (const [fieldName, fieldInfo] of Object.entries(state.activities_k)) {
          const index = fieldInfo[0]
          obj[fieldName] = activityArray[index] || ''
        }
        return obj
      })
    }
  },

  actions: {
    // Helper to get auth headers
    getAuthHeaders() {
      const authStore = useAuthStore()
      return {
        'Session-Id': authStore.sessionId
      }
    },

    // Parse activities_ctx to update pagination state
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

    // 1. List Activities with pagination support
    async listActivities(params = {}) {
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

        const { data } = await axiosInstance.get('api/activities/', {
          params: paginationParams,
          headers: this.getAuthHeaders()
        })

        // console.log('API Response:', data)
        this.raw = data
        this.activities = data.activities || []
        this.activities_k = data.activities_k || {}
        this.activities_ctx = data.activities_ctx || []

        // Parse pagination context
        this.parsePaginationContext(data.activities_ctx)

      } catch (err) {
        this.error = err.message || 'Request failed'
      } finally {
        this.loading = false
      }
    },

    // Go to next page
    async nextPage(filters = {}) {
      if (!this.hasNextPage) return
      const newOffset = this.pagination.offset + this.pagination.limit
      await this.listActivities({ ...filters, _o: newOffset, _c: this.pagination.limit })
    },

    // Go to previous page
    async prevPage(filters = {}) {
      if (!this.hasPrevPage) return
      const newOffset = Math.max(0, this.pagination.offset - this.pagination.limit)
      await this.listActivities({ ...filters, _o: newOffset, _c: this.pagination.limit })
    },

    // Go to specific page
    async goToPage(page, filters = {}) {
      const newOffset = (page - 1) * this.pagination.limit
      await this.listActivities({ ...filters, _o: newOffset, _c: this.pagination.limit })
    },

    // Change page size
    async setPageSize(size, filters = {}) {
      this.pagination.limit = size
      this.pagination.offset = 0
      await this.listActivities({ ...filters, _o: 0, _c: size })
    },

    // Reset pagination to first page
    resetPagination() {
      this.pagination.offset = 0
      this.pagination.currentPage = 1
      this.pagination.rangeStart = 1
      this.pagination.rangeEnd = this.pagination.limit
    },

    // 2. View Activity
    async viewActivity(id) {
      try {
        const { data } = await axiosInstance.get(`api/activities/${id}`, {
          headers: this.getAuthHeaders()
        })
        return data
      } catch (err) {
        throw new Error(err.message || 'Failed to view activity')
      }
    },

    // 3. CSV Download
    async downloadCSV(params = {}) {
      try {
        const response = await axiosInstance.get('api/activities/', {
          params: { ...params, csv: 1 },
          headers: this.getAuthHeaders(),
          responseType: 'blob'
        })
        return response.data
      } catch (err) {
        throw new Error(err.message || 'Failed to download CSV')
      }
    },

    // 4. Pivot Reports
    async getPivotReport(params = {}) {
      try {
        const { data } = await axiosInstance.get('api/activities/rpt', {
          params,
          headers: this.getAuthHeaders()
        })
        return data
      } catch (err) {
        throw new Error(err.message || 'Failed to fetch pivot report')
      }
    },

    // Reset store
    resetStore() {
      this.activities = []
      this.activities_k = {}
      this.activities_ctx = []
      this.raw = {}
      this.loading = false
      this.error = null
    }
  }
})
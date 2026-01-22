// src/stores/reporters.js
import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'
import { useAuthStore } from './auth'

export const useReporterStore = defineStore('reporterStore', {
  state: () => ({
    reporters: [],
    reporters_k: {},
    reporters_ctx: [],
    raw: {},
    loading: false,
    error: null,
  }),

  actions: {
    // Helper to get auth headers
    getAuthHeaders() {
      const authStore = useAuthStore()
      return {
        'Session-Id': authStore.sessionId
      }
    },

    // 1. List Reporters
    async listReporters(params = {}) {
      this.loading = true
      this.error = null

      try {
        const { data } = await axiosInstance.get('api/reporters/', {
          params,
          headers: this.getAuthHeaders()
        })

        console.log('Fetched reporters:', data)
        this.raw = data
        this.reporters = data.reporters || []
        this.reporters_k = data.reporters_k || {}
        this.reporters_ctx = data.reporters_ctx || []
      } catch (err) {
        this.error = err.message || 'Failed to fetch reporters'
      } finally {
        this.loading = false
      }
    },

    // 2. View Reporter
    async viewReporter(reporterId) {
      try {
        const { data } = await axiosInstance.get(`api/reporters/${reporterId}`, {
          headers: this.getAuthHeaders()
        })
        return data
      } catch (err) {
        throw new Error(err.message || 'Failed to fetch reporter details')
      }
    },

    // 3. Create Reporter
    async createReporter(payload) {
      try {
        const { data } = await axiosInstance.post('api/reporters', payload, {
          headers: {
            ...this.getAuthHeaders(),
            'Content-Type': 'application/json'
          }
        })
        return data
      } catch (err) {
        throw new Error(err.message || 'Failed to create reporter')
      }
    },

    // 4. Edit Reporter
    async editReporter(reporterId, payload) {
      try {
        const { data } = await axiosInstance.post(`api/reporters/${reporterId}`, payload, {
          headers: {
            ...this.getAuthHeaders(),
            'Content-Type': 'application/json'
          }
        })
        return data
      } catch (err) {
        throw new Error(err.message || 'Failed to edit reporter')
      }
    },

    // 5. CSV Download
    async downloadCSV(params = {}) {
      try {
        const response = await axiosInstance.get('api/reporters/', {
          params: { ...params, csv: 1 },
          headers: this.getAuthHeaders(),
          responseType: 'blob'
        })
        return response.data
      } catch (err) {
        throw new Error(err.message || 'Failed to download CSV')
      }
    },

    // 6. Pivot Reports
    async getPivotReport(params = {}) {
      try {
        const { data } = await axiosInstance.get('api/reporters/rpt', {
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
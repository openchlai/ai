// src/stores/perpetrators.js
import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'
import { useAuthStore } from './auth'

export const usePerpetratorStore = defineStore('perpetratorStore', {
  state: () => ({
    perpetrators: [],
    perpetrators_k: {},
    perpetrators_ctx: [],
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

    // 1. List Perpetrators
    async listPerpetrators(params = {}) {
      this.loading = true
      this.error = null

      try {
        const { data } = await axiosInstance.get('api/perpetrators/', {
          params,
          headers: this.getAuthHeaders()
        })

        console.log('Fetched perpetrators:', data)
        this.raw = data
        this.perpetrators = data.perpetrators || []
        this.perpetrators_k = data.perpetrators_k || {}
        this.perpetrators_ctx = data.perpetrators_ctx || []
        return data
      } catch (err) {
        this.error = err.message || 'Failed to fetch perpetrators'
        throw err
      } finally {
        this.loading = false
      }
    },

    // 2. View Perpetrator
    async viewPerpetrator(perpetratorId) {
      try {
        const { data } = await axiosInstance.get(`api/perpetrators/${perpetratorId}`, {
          headers: this.getAuthHeaders()
        })
        return data
      } catch (err) {
        throw new Error(err.message || 'Failed to fetch perpetrator details')
      }
    },

    // 3. Create Perpetrator
    async createPerpetrator(payload) {
      try {
        console.log('Creating perpetrator with payload:', payload)
        
        const { data } = await axiosInstance.post('api/perpetrators', payload, {
          headers: {
            ...this.getAuthHeaders(),
            'Content-Type': 'application/json'
          }
        })

        console.log('Perpetrator creation response:', data)

        // Extract the perpetrator ID from the response
        // The ID is at index 0 of the first perpetrator record
        let perpetratorId = null
        if (data.perpetrators && data.perpetrators.length > 0) {
          const perpetratorRecord = data.perpetrators[0]
          if (Array.isArray(perpetratorRecord) && perpetratorRecord.length > 0) {
            perpetratorId = perpetratorRecord[0] // ID is at index 0
          }
        }

        if (!perpetratorId) {
          throw new Error('No perpetrator ID returned from server')
        }

        console.log('Created perpetrator ID:', perpetratorId)

        // Return both the full response and extracted ID
        return {
          id: perpetratorId,
          response: data,
          perpetrator_record: data.perpetrators[0]
        }
      } catch (err) {
        console.error('Error creating perpetrator:', err)
        throw new Error(err.message || 'Failed to create perpetrator')
      }
    },

    // 4. Edit Perpetrator
    async editPerpetrator(perpetratorId, payload) {
      try {
        const { data } = await axiosInstance.post(`api/perpetrators/${perpetratorId}`, payload, {
          headers: {
            ...this.getAuthHeaders(),
            'Content-Type': 'application/json'
          }
        })
        return data
      } catch (err) {
        throw new Error(err.message || 'Failed to edit perpetrator')
      }
    },

    // 5. CSV Download
    async downloadCSV(params = {}) {
      try {
        const response = await axiosInstance.get('api/perpetrators/', {
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
        const { data } = await axiosInstance.get('api/perpetrators/rpt', {
          params,
          headers: this.getAuthHeaders()
        })
        return data
      } catch (err) {
        throw new Error(err.message || 'Failed to fetch pivot report')
      }
    },

    // Helper method to get field value using perpetrators_k mapping
    getFieldValue(perpetratorRecord, fieldName) {
      if (!this.perpetrators_k[fieldName] || !Array.isArray(perpetratorRecord)) {
        return ''
      }
      const fieldIndex = this.perpetrators_k[fieldName][0]
      return perpetratorRecord[fieldIndex] || ''
    }
  }
})
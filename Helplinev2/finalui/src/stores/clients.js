// src/stores/clients.js
import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'
import { useAuthStore } from './auth'

export const useClientStore = defineStore('clientStore', {
  state: () => ({
    clients: [],
    clients_k: {},
    clients_ctx: [],
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

    // 1. List Clients
    async listClients(params = {}) {
      this.loading = true
      this.error = null

      try {
        const { data } = await axiosInstance.get('api/clients/', {
          params,
          headers: this.getAuthHeaders()
        })

        console.log('Fetched clients:', data)
        this.raw = data
        this.clients = data.clients || []
        this.clients_k = data.clients_k || {}
        this.clients_ctx = data.clients_ctx || []
        return data
      } catch (err) {
        this.error = err.message || 'Failed to fetch clients'
        throw err
      } finally {
        this.loading = false
      }
    },

    // 2. View Client
    async viewClient(clientId) {
      try {
        const { data } = await axiosInstance.get(`api/clients/${clientId}`, {
          headers: this.getAuthHeaders()
        })
        return data
      } catch (err) {
        throw new Error(err.message || 'Failed to fetch client details')
      }
    },

    // 3. Create Client
    async createClient(payload) {
      try {
        console.log('Creating client with payload:', payload)
        
        const { data } = await axiosInstance.post('api/clients', payload, {
          headers: {
            ...this.getAuthHeaders(),
            'Content-Type': 'application/json'
          }
        })

        console.log('Client creation response:', data)

        // Extract the client ID from the response
        // The ID is at index 0 of the first client record
        let clientId = null
        if (data.clients && data.clients.length > 0) {
          const clientRecord = data.clients[0]
          if (Array.isArray(clientRecord) && clientRecord.length > 0) {
            clientId = clientRecord[0] // ID is at index 0
          }
        }

        if (!clientId) {
          throw new Error('No client ID returned from server')
        }

        console.log('Created client ID:', clientId)

        // Return both the full response and extracted ID
        return {
          id: clientId,
          response: data,
          client_record: data.clients[0]
        }
      } catch (err) {
        console.error('Error creating client:', err)
        throw new Error(err.message || 'Failed to create client')
      }
    },

    // 4. Edit Client
    async editClient(clientId, payload) {
      try {
        const { data } = await axiosInstance.post(`api/clients/${clientId}`, payload, {
          headers: {
            ...this.getAuthHeaders(),
            'Content-Type': 'application/json'
          }
        })
        return data
      } catch (err) {
        throw new Error(err.message || 'Failed to edit client')
      }
    },

    // 5. CSV Download
    async downloadCSV(params = {}) {
      try {
        const response = await axiosInstance.get('api/clients/', {
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
        const { data } = await axiosInstance.get('api/clients/rpt', {
          params,
          headers: this.getAuthHeaders()
        })
        return data
      } catch (err) {
        throw new Error(err.message || 'Failed to fetch pivot report')
      }
    },

    // Helper method to get field value using clients_k mapping
    getFieldValue(clientRecord, fieldName) {
      if (!this.clients_k[fieldName] || !Array.isArray(clientRecord)) {
        return ''
      }
      const fieldIndex = this.clients_k[fieldName][0]
      return clientRecord[fieldIndex] || ''
    }
  }
})
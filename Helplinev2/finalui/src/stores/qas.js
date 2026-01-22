// src/stores/qa.js
import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'
import { useAuthStore } from './auth'

export const useQAStore = defineStore('qa', {
  state: () => ({
    qas: [],
    qas_k: {},
    qaCount: 0,
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

    async listQA(params = {}) {
      try {
        this.loading = true

        const { data } = await axiosInstance.get('api/qas/', {
          params,
          headers: this.getAuthHeaders()
        })

        // Store QA data and key mappings
        this.qas = data.qas || data.qa || []
        this.qas_k = data.qas_k || data.qa_k || {}
        this.qaCount = data.qa_nb ? data.qa_nb[0][1] : this.qas.length
      } catch (err) {
        this.error = err.message || 'Failed to fetch QA list'
        throw err
      } finally {
        this.loading = false
      }
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
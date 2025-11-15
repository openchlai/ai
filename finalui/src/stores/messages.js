// stores/messages.js
import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios';

export const useMessagesStore = defineStore('messages', {
  state: () => ({
    pmessages: [],
    pmessages_k: {},
    pmessages_ctx: [],
    loading: false,
    error: null
  }),

  actions: {
    async fetchAllMessages(params = {}) {
      this.loading = true
      this.error = null
      try {
        const { data } = await axiosInstance.get('api/pmessages/', { params })
        console.log('[ALL] Messages:', data)
        this.pmessages = data.pmessages || []
        this.pmessages_k = data.pmessages_k || {}
        this.pmessages_ctx = data.pmessages_ctx || []
        return data
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    },

    async fetchMessagesBySource(src) {
      this.loading = true
      this.error = null
      try {
        const { data } = await axiosInstance.get('api/pmessages/', {
          params: { src }
        })
        console.log(`[${src.toUpperCase()}] Messages:`, data)
        this.pmessages = data.pmessages || []
        this.pmessages_k = data.pmessages_k || {}
        this.pmessages_ctx = data.pmessages_ctx || []
        return data
      } catch (err) {
        this.error = err.message
        throw err
      } finally {
        this.loading = false
      }
    }
  }
})

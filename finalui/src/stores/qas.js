// src/stores/qa.js
import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios';

export const useQAStore = defineStore('qa', {
  state: () => ({
    qas: [],
    qas_k: {},
    qaCount: 0,
    loading: false,
    error: null,
  }),

  actions: {
    async listQA(params = {}) {
      try {
        this.loading = true

        const { data } = await axiosInstance.get('api/qas/', {
          params,
          headers: { 'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe' },
        })

        // Store QA data and key mappings
        this.qas = data.qas || data.qa || []
        this.qas_k = data.qas_k || data.qa_k || {}
        this.qaCount = data.qa_nb ? data.qa_nb[0][1] : this.qas.length
      } catch (err) {
        this.error = err.message || 'Failed to fetch QA list'
      } finally {
        this.loading = false
      }
    },
  },
})

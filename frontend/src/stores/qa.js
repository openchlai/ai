import { defineStore } from 'pinia';
import axiosInstance from '@/utils/axios'

export const useQAStore = defineStore('qa', {
  state: () => ({
    qaList: [],
    qaCount: 0,
    loading: false,
    error: null,
  }),

  actions: {
    // 1. Create QA
    async createQA(payload) {
      try {
        this.loading = true;
        const { data } = await axiosInstance.post('api/qa', payload, {
          headers: { 'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe' }
        });
        return data;
      } catch (err) {
        this.error = err.message || 'Failed to create QA';
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 2. View QA
    async viewQA(id) {
      try {
        this.loading = true;
        const { data } = await axiosInstance.get(`api/qa/${id}`, {
          headers: { 'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe' }
        });
        return data;
      } catch (err) {
        this.error = err.message || 'Failed to fetch QA';
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 3. List QA
    async listQA(params = {}) {
      try {
        this.loading = true;
        const { data } = await axiosInstance.get('api/qa/', {
          params,
          headers: { 'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe' }
        });
        this.qaList = data.qa || [];
        this.qaCount = data.qa_nb ? data.qa_nb[0][1] : this.qaList.length;
      } catch (err) {
        this.error = err.message || 'Failed to fetch QA list';
      } finally {
        this.loading = false;
      }
    },

    // 4. CSV Download
    async downloadCSV(params = {}) {
      try {
        const response = await axiosInstance.get('api/qa/', {
          params: { ...params, csv: 1 },
          headers: { 'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe' },
          responseType: 'blob'
        });
        return response.data;
      } catch (err) {
        throw new Error(err.message || 'Failed to download QA CSV');
      }
    },

    // 5. Pivot Reports
    async getPivotReport(params = {}) {
      try {
        const { data } = await axiosInstance.get('api/qa/rpt', {
          params,
          headers: { 'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe' }
        });
        return data;
      } catch (err) {
        throw new Error(err.message || 'Failed to fetch QA pivot report');
      }
    }
  }
});


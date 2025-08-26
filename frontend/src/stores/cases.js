import { defineStore } from 'pinia';
import axiosInstance from '@/utils/axios';

export const useCaseStore = defineStore('cases', {
  state: () => ({
    cases: [],
    cases_k: {},
    caseCount: 0,
    loading: false,
    error: null,
  }),

  actions: {
    // 1. Create Case
    async createCase(payload) {
      try {
        this.loading = true;
        const { data } = await axiosInstance.post('api/cases', payload, {
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe',
            'Content-Type': 'application/json'
          }
        });
        return data;
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 2. Update Case
    async updateCase(id, payload) {
      try {
        this.loading = true;
        const { data } = await axiosInstance.post(`api/cases/${id}`, payload, {
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe'
          }
        });
        return data;
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 3. View Case
    async viewCase(id) {
      try {
        this.loading = true;
        const { data } = await axiosInstance.get(`api/cases/${id}`, {
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe'
          }
        });
        return data;
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 4. List Cases
    async listCases(params = {}) {
      try {
        this.loading = true;
        const { data } = await axiosInstance.get('api/cases/', {
          params,
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe'
          }
        });
        console.log('Cases data:', data);
        this.cases = data.cases || [];
        this.cases_k = data.cases_k || {};
        this.caseCount = data.cases_nb?.[0]?.[1] || this.cases.length;
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 5. CSV Download
    async downloadCSV(params = {}) {
      try {
        const response = await axiosInstance.get('api/cases/', {
          params: { ...params, csv: 1 },
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe'
          },
          responseType: 'blob'
        });
        return response.data;
      } catch (err) {
        throw new Error(err.message || 'Failed to download CSV');
      }
    },

    // 6. Pivot Reports
    async getPivotReport(params = {}) {
      try {
        const { data } = await axiosInstance.get('api/cases/rpt', {
          params,
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe'
          }
        });
        return data;
      } catch (err) {
        throw new Error(err.message || 'Failed to fetch pivot report');
      }
    }
  }
});

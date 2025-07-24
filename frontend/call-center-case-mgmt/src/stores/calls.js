// src/stores/callStore.js
import { defineStore } from 'pinia';
import axiosInstance from '@/utils/axios';

export const useCallStore = defineStore('callStore', {
  state: () => ({
    calls: [],         // array of calls
    calls_k: {},       // metadata keys
    calls_ctx: [],     // context (pagination etc.)
    raw: {},           // full API response
    loading: false,
    error: null
  }),

  getters: {
    callCount: (state) => state.calls?.length ?? 0,

    // Get call by uniqueid
    getCallById: (state) => (uniqueid) => {
      const index = parseInt(state.calls_k?.uniqueid?.[0] ?? 0);
      return state.calls.find(call => call[index] === uniqueid) || null;
    }
  },

  actions: {
    // 1. List Calls
    async listCalls(params = {}) {
      this.loading = true;
      this.error = null;

      try {
        const { data } = await axiosInstance.get('api/calls/', {
          params,
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe'
          }
        });
        console.log('API Response:', data);
        this.raw = data;
        this.calls = data.calls || [];
        this.calls_k = data.calls_k || {};
        this.calls_ctx = data.calls_ctx || [];
      } catch (err) {
        this.error = err.message || 'Request failed';
      } finally {
        this.loading = false;
      }
    },

    // 2. View Call
    async viewCall(uniqueid) {
      try {
        const { data } = await axiosInstance.get(`api/calls/${uniqueid}`, {
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe'
          }
        });
        return data;
      } catch (err) {
        throw new Error(err.message || 'Failed to view call');
      }
    },

    // 3. Download Call Recording
   async downloadCallRecording(uniqueid, format = 'wav') {
  try {
    const url = `api/calls/${uniqueid}`;
    console.log('Downloading recording from:', url);

    const response = await axiosInstance.get(url, {
      params: { file: format },
      headers: {
        'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe'
      },
      responseType: 'blob'
    });

    return response.data;
  } catch (err) {
    throw new Error(err.message || 'Failed to download recording');
  }
},


    // 4. CSV Download
    async downloadCSV(params = {}) {
      try {
        const response = await axiosInstance.get('api/calls/', {
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

    // 5. Pivot Reports
    async getPivotReport(params = {}) {
      try {
        const { data } = await axiosInstance.get('api/calls/rpt', {
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

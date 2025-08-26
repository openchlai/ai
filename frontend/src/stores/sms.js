// src/stores/sms.js
import { defineStore } from 'pinia';
import axiosInstance from '@/utils/axios'

export const useSMSStore = defineStore('sms', {
  state: () => ({
    sms: [],
    sms_k: [],
    smsCount: 0,
    loading: false,
    error: null,
  }),

  actions: {
    // 1. Create SMS
    async createSMS(payload) {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await axiosInstance.post('api/sms/', payload, {
          headers: { 'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe' },
        });
        return data.sms?.[0];
      } catch (err) {
        this.error = err.message || 'Failed to create SMS';
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 2. View SMS
    async viewSMS(id) {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await axiosInstance.get(`api/sms/${id}`, {
          headers: { 'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe' },
        });
        return data.sms?.[0];
      } catch (err) {
        this.error = err.message || 'Failed to fetch SMS';
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 3. List SMSes
    async listSMS(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await axiosInstance.get('api/sms/', {
          params,
          headers: { 'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe' },
        });
        this.sms = data.sms || [];
        this.sms_k = data.sms_k || [];
        this.smsCount = data.sms_nb?.[0]?.[1] || this.sms.length;
      } catch (err) {
        this.error = err.message || 'Failed to fetch SMS list';
      } finally {
        this.loading = false;
      }
    },

    // 4. CSV Download
    async downloadCSV(params = {}) {
      try {
        const response = await axiosInstance.get('api/sms/', {
          params: { ...params, csv: 1 },
          headers: { 'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe' },
          responseType: 'blob',
        });
        return response.data;
      } catch (err) {
        throw new Error(err.message || 'Failed to download CSV');
      }
    },

    // 5. Pivot Reports
    async getPivotReport(params = {}) {
      try {
        const { data } = await axiosInstance.get('api/sms/rpt', {
          params,
          headers: { 'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe' },
        });
        return data;
      } catch (err) {
        throw new Error(err.message || 'Failed to fetch pivot report');
      }
    },
  },
});

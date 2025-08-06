// src/stores/emails.js
import { defineStore } from 'pinia';
import axiosInstance from '@/utils/axios'

export const useEmailStore = defineStore('emails', {
  state: () => ({
    emails: [],
    emails_k: [],
    emailCount: 0,
    loading: false,
    error: null,
  }),

  actions: {
    // Create Email
    async createEmail(payload) {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await axiosInstance.post('api/emails/', payload, {
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe',
            'Content-Type': 'application/json'
          }
        });
        return data;
      } catch (err) {
        this.error = err.response?.data?.errors || err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // View Email
    async viewEmail(id) {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await axiosInstance.get(`api/emails/${id}`, {
          headers: { 'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe' }
        });
        return data;
      } catch (err) {
        this.error = err.response?.data?.errors || err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // View Email Body (plain or HTML)
    async viewEmailBody(id, type = 'plain') {
      try {
        const { data } = await axiosInstance.get(`api/emails/${id}`, {
          params: { file: type },
          headers: { 'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe' }
        });
        return data;
      } catch (err) {
        throw err;
      }
    },

    // View Email Attachment
    async viewEmailAttachment(fileId) {
      try {
        const response = await axiosInstance.get(`api/files/${fileId}`, {
          params: { file: '1l' },
          headers: { 'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe' },
          responseType: 'blob'
        });
        return response.data;
      } catch (err) {
        throw err;
      }
    },

    // List Emails
    async listEmails(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await axiosInstance.get('api/emails/', {
          params,
          headers: { 'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe' }
        });
        this.emails = data?.emails || [];
        this.emails_k = data?.emails_k || [];
        this.emailCount = data?.emails_nb || 0;
      } catch (err) {
        this.error = err.response?.data?.errors || err.message;
      } finally {
        this.loading = false;
      }
    },

    // CSV Download
    async downloadCSV(params = {}) {
      try {
        const response = await axiosInstance.get('api/emails/', {
          params: { ...params, csv: 1 },
          headers: { 'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe' },
          responseType: 'blob'
        });
        return response.data;
      } catch (err) {
        throw err;
      }
    },

    // Pivot Reports
    async getPivotReport(params = {}) {
      try {
        const { data } = await axiosInstance.get('api/emails/rpt', {
          params,
          headers: { 'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe' }
        });
        return data;
      } catch (err) {
        throw err;
      }
    }
  }
});

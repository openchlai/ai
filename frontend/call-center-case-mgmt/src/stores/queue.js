// src/stores/queue.js
import { defineStore } from 'pinia';
import axiosInstance from '@/axiosInstance';

export const useQueueStore = defineStore('queue', {
  state: () => ({
    status: null,
    message: '',
    lastPoll: null,
    error: null,
    loading: false,
  }),

  actions: {
    async joinQueue() {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await axiosInstance.post('api/joinq', null, {
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe'
          }
        });
        this.status = data.status;
        this.message = data.message;
        return data;
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async leaveQueue() {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await axiosInstance.post('api/leaveq', null, {
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe'
          }
        });
        this.status = data.status;
        this.message = data.message;
        return data;
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async pollQueueStatus() {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await axiosInstance.get('api/queuestatus', {
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe'
          }
        });
        this.lastPoll = new Date();
        if (data.profile && data.profile.length > 0) {
          const profile = data.profile[0];
          this.status = profile.status;
          this.message = profile.message;
        }
        return data.profile || [];
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    }
  }
});

// src/stores/stats.js
import { defineStore } from 'pinia';
import axiosInstance from '@/axiosInstance';

export const useStatsStore = defineStore('stats', {
  state: () => ({
    loading: false,
    error: null,
    stats: null,
  }),
  actions: {
    async fetchStats() {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await axiosInstance.get('api/stats/0', {
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe'
          }
        });
        this.stats = data;
      } catch (err) {
        this.error = err.message || 'Failed to fetch stats';
        throw err;
      } finally {
        this.loading = false;
      }
    }
  }
});

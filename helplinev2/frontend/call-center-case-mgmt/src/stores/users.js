// src/stores/users.js
import { defineStore } from 'pinia';
import axiosInstance from '@/utils/axios';

export const useUserStore = defineStore('userStore', {
  state: () => ({
    users: [],
    users_k: {},
    users_ctx: [],
    raw: {},
    loading: false,
    error: null,
  }),

  actions: {
    // 1. List Users
    async listUsers(params = {}) {
      this.loading = true;
      this.error = null;

      try {
        const { data } = await axiosInstance.get('api/users/', {
          params,
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe'
          }
        });

        console.log('Fetched users:', data);
        this.raw = data;
        this.users = data.users || [];
        this.users_k = data.users_k || {};
        this.users_ctx = data.users_ctx || [];
      } catch (err) {
        this.error = err.message || 'Failed to fetch users';
      } finally {
        this.loading = false;
      }
    },

    // 2. View User
    async viewUser(userId) {
      try {
        const { data } = await axiosInstance.get(`api/users/${userId}`, {
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe'
          }
        });
        return data;
      } catch (err) {
        throw new Error(err.message || 'Failed to fetch user details');
      }
    },

    // 3. Create User
    async createUser(payload) {
      try {
        const { data } = await axiosInstance.post('api/users', payload, {
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe',
            'Content-Type': 'application/json'
          }
        });
        return data;
      } catch (err) {
        throw new Error(err.message || 'Failed to create user');
      }
    },

    // 4. Edit User
    async editUser(userId, payload) {
      try {
        const { data } = await axiosInstance.post(`api/users/${userId}`, payload, {
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe',
            'Content-Type': 'application/json'
          }
        });
        return data;
      } catch (err) {
        throw new Error(err.message || 'Failed to edit user');
      }
    },

    // 5. CSV Download
    async downloadCSV(params = {}) {
      try {
        const response = await axiosInstance.get('api/users/', {
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
        const { data } = await axiosInstance.get('api/users/rpt', {
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

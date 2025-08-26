// src/stores/files.js
import { defineStore } from 'pinia';
import axiosInstance from '@/axiosInstance';

export const useFilesStore = defineStore('files', {
  state: () => ({
    loading: false,
    error: null,
  }),
  actions: {
    async uploadFile(file) {
      this.loading = true;
      this.error = null;
      try {
        const formData = new FormData();
        formData.append('file[]', file);

        const { data } = await axiosInstance.post('api/files/', formData, {
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe',
            'Content-Type': 'multipart/form-data'
          }
        });

        return data;
      } catch (err) {
        this.error = err.message || 'Failed to upload file';
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async downloadFile(fileId) {
      this.loading = true;
      this.error = null;
      try {
        const response = await axiosInstance.get(`api/files/${fileId}`, {
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe'
          },
          params: { file: 1 },
          responseType: 'blob'
        });

        return response.data;
      } catch (err) {
        this.error = err.message || 'Failed to download file';
        throw err;
      } finally {
        this.loading = false;
      }
    }
  }
});

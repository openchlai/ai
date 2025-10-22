// src/stores/files.js
import { defineStore } from 'pinia';
import axiosInstance from '@/utils/axios';

export const useFilesStore = defineStore('files', {
  state: () => ({
    loading: false,
    error: null,
    attachments: [],
    attachments_k: {},
  }),
  actions: {
    // Existing uploadFile method (this works and uploads to /api/files/)
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



    // Combined method: Upload file then get attachment ID
    async uploadFileAndGetAttachmentId(file) {
      this.loading = true;
      this.error = null;
      
      try {
        console.log('Step 1: Uploading file to /api/files/', file.name);
        
        // Step 1: Upload file to /api/files/ (we don't need the response)
        await this.uploadFile(file);
        console.log('File uploaded successfully to /api/files/');

        // Step 2: Get attachment record from /api/attachments/
        console.log('Step 2: Getting attachment record from /api/attachments/');
        const { data } = await axiosInstance.get('api/attachments/', {
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe'
          }
        });

        console.log('Attachments response:', data);

        // Store the response data
        this.attachments = data.attachments || [];
        this.attachments_k = data.attachments_k || {};

        // Step 3: Extract attachment ID using attachments_k mapping
        let attachmentId = null;
        if (data.attachments && data.attachments.length > 0) {
          // Get the most recent attachment (last in array)
          const attachmentRecord = data.attachments[data.attachments.length - 1];
          
          if (Array.isArray(attachmentRecord) && attachmentRecord.length > 0) {
            // Use attachments_k to find the ID index (should be 0)
            const idIndex = data.attachments_k?.id?.[0] || 0;
            attachmentId = attachmentRecord[idIndex];
          }
        }

        if (!attachmentId) {
          throw new Error('No attachment ID found in response');
        }

        console.log('Attachment ID extracted:', attachmentId);

        return {
          id: attachmentId,
          attachmentResponse: data,
          file: file
        };
      } catch (err) {
        console.error('Error in upload and get attachment ID:', err);
        this.error = err.message || 'Failed to upload file and get attachment ID';
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
    },

    // Helper method to get field value using attachments_k mapping
    getAttachmentFieldValue(attachmentRecord, fieldName) {
      if (!this.attachments_k[fieldName] || !Array.isArray(attachmentRecord)) {
        return '';
      }
      const fieldIndex = this.attachments_k[fieldName][0];
      return attachmentRecord[fieldIndex] || '';
    }
  }
});
// src/stores/messages.js
import { defineStore } from 'pinia';
import axiosInstance from '@/utils/axios';

export const useMessagesStore = defineStore('messages', {
  state: () => ({
    allMessages: [],
    whatsappMessages: [],
    smsMessages: [],
    loading: false,
    error: null,
  }),

  actions: {
    async fetchAllMessages(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await axiosInstance.get('api/pmessages/', { params });
        console.log('Fetched all messages:', data);
        this.allMessages = data.pmessages || [];
        return data;
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async fetchWhatsappMessages(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await axiosInstance.get('api/pmessages/', {
          params: { ...params, src: 'whatsApp' }
        });
        console.log('Fetched WhatsApp messages:', data);    
        this.whatsappMessages = data.pmessages || [];
        return data;
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async fetchSmsMessages(params = {}) {
      this.loading = true;
      this.error = null;
      try {
        const { data } = await axiosInstance.get('api/pmessages/', {
          params: { ...params, src: 'sms' }
        });
        console.log('Fetched SMS messages:', data);
        this.smsMessages = data.pmessages || [];
        return data;
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    }
  }
});

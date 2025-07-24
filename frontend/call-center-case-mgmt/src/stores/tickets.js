import { defineStore } from 'pinia';
import axiosInstance from '@/utils/axios'

export const useTicketStore = defineStore('tickets', {
  state: () => ({
    tickets: [],
    tickets_k: {},
    ticketCount: 0,
    loading: false,
    error: null,
  }),

  actions: {
    // 1. Create Ticket
    async createTicket(payload) {
      try {
        this.loading = true;
        const { data } = await axiosInstance.post('api/tickets', payload, {
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

    // 2. Update Ticket
    async updateTicket(id, payload) {
      try {
        this.loading = true;
        const { data } = await axiosInstance.post(`api/tickets/${id}`, payload, {
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

    // 3. View Ticket
    async viewTicket(id) {
      try {
        this.loading = true;
        const { data } = await axiosInstance.get(`api/tickets/${id}`, {
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

    // 4. List Tickets
    async listTickets(params = {}) {
      try {
        this.loading = true;
        const { data } = await axiosInstance.get('api/tickets/', {
          params,
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe'
          }
        });
        console.log('Tickets data:', data);
        this.tickets = data.tickets || [];
        this.tickets_k = data.tickets_k || {};
        this.ticketCount = data.tickets_nb?.[0]?.[1] || this.tickets.length;
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
        const response = await axiosInstance.get('api/tickets/', {
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
        const { data } = await axiosInstance.get('api/tickets/rpt', {
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

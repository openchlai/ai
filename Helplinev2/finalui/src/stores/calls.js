// src/stores/callStore.js
import { defineStore } from 'pinia';
import axiosInstance from '@/utils/axios';
import { useAuthStore } from './auth';

export const useCallStore = defineStore('callStore', {
  state: () => ({
    calls: [],         // array of calls
    calls_k: {},       // metadata keys
    calls_ctx: [],     // context (pagination etc.)
    raw: {},           // full API response
    loading: false,
    error: null,
    // Pagination state
    pagination: {
      offset: 0,       // _o parameter - current offset
      limit: 20,       // _c parameter - items per page
      currentPage: 1,  // current page number
      totalRecords: 0, // total records from calls_ctx
      rangeStart: 1,   // display range start
      rangeEnd: 20     // display range end
    }
  }),

  getters: {
    callCount: (state) => state.calls?.length ?? 0,

    // Get call by uniqueid
    getCallById: (state) => (uniqueid) => {
      const index = parseInt(state.calls_k?.uniqueid?.[0] ?? 0);
      return state.calls.find(call => call[index] === uniqueid) || null;
    },

    // Getter to return calls with human-readable Date Hour
    formattedCalls: (state) => {
      const dthIndex = parseInt(state.calls_k?.dth?.[0] ?? -1); // index for Date Hour
      if (dthIndex === -1) return [];

      return state.calls.map(call => {
        const timestamp = call[dthIndex];
        let readableDate = '';
        if (timestamp) {
          const dateObj = new Date(Number(timestamp) * 1000); // convert seconds to ms
          readableDate = dateObj.toLocaleString(); // e.g., "7/21/2025, 14:20:00"
        }
        return {
          ...call,
          readableDate
        };
      });
    },

    // Pagination getters
    totalRecords: (state) => state.pagination.totalRecords,
    currentPage: (state) => state.pagination.currentPage,
    pageSize: (state) => state.pagination.limit,
    totalPages: (state) => Math.ceil(state.pagination.totalRecords / state.pagination.limit) || 1,
    hasNextPage: (state) => state.pagination.rangeEnd < state.pagination.totalRecords,
    hasPrevPage: (state) => state.pagination.currentPage > 1,
    paginationInfo: (state) => ({
      rangeStart: state.pagination.rangeStart,
      rangeEnd: state.pagination.rangeEnd,
      total: state.pagination.totalRecords,
      currentPage: state.pagination.currentPage,
      totalPages: Math.ceil(state.pagination.totalRecords / state.pagination.limit) || 1
    })
  },

  actions: {
    // Helper to get auth headers
    getAuthHeaders() {
      const authStore = useAuthStore();
      return {
        'Session-Id': authStore.sessionId
      };
    },

    // Parse calls_ctx to update pagination state
    // Format: [["offset", "limit", "rangeStart", "rangeEnd", "total", "", ""]]
    parsePaginationContext(ctx) {
      if (ctx && ctx[0] && Array.isArray(ctx[0])) {
        const [offset, limit, rangeStart, rangeEnd, total] = ctx[0];
        this.pagination.offset = parseInt(offset) || 0;
        this.pagination.limit = parseInt(limit) || 20;
        this.pagination.rangeStart = parseInt(rangeStart) || 1;
        this.pagination.rangeEnd = parseInt(rangeEnd) || 20;
        this.pagination.totalRecords = parseInt(total) || 0;
        this.pagination.currentPage = Math.floor(this.pagination.offset / this.pagination.limit) + 1;
      }
    },

    // 1. List Calls with pagination support
    async listCalls(params = {}) {
      this.loading = true;
      this.error = null;

      try {
        // Build pagination params matching control UI format
        const paginationParams = {
          _c: params._c || this.pagination.limit,  // count/limit
          _o: params._o !== undefined ? params._o : this.pagination.offset,  // offset
          _a: 0,  // flag used by control UI
          ...params
        };

        // Remove our internal pagination keys from params if they exist
        delete paginationParams.page;

        const { data } = await axiosInstance.get('api/calls/', {
          params: paginationParams,
          headers: this.getAuthHeaders()
        });
        console.log('API Response:', data);
        this.raw = data;
        this.calls = data.calls || [];
        this.calls_k = data.calls_k || {};
        this.calls_ctx = data.calls_ctx || [];

        // Parse pagination context from response
        this.parsePaginationContext(data.calls_ctx);
      } catch (err) {
        this.error = err.message || 'Request failed';
      } finally {
        this.loading = false;
      }
    },

    // Go to next page
    async nextPage(filters = {}) {
      if (!this.hasNextPage) return;
      const newOffset = this.pagination.offset + this.pagination.limit;
      await this.listCalls({ ...filters, _o: newOffset, _c: this.pagination.limit });
    },

    // Go to previous page
    async prevPage(filters = {}) {
      if (!this.hasPrevPage) return;
      const newOffset = Math.max(0, this.pagination.offset - this.pagination.limit);
      await this.listCalls({ ...filters, _o: newOffset, _c: this.pagination.limit });
    },

    // Go to specific page
    async goToPage(page, filters = {}) {
      const newOffset = (page - 1) * this.pagination.limit;
      await this.listCalls({ ...filters, _o: newOffset, _c: this.pagination.limit });
    },

    // Change page size
    async setPageSize(size, filters = {}) {
      this.pagination.limit = size;
      this.pagination.offset = 0;
      await this.listCalls({ ...filters, _o: 0, _c: size });
    },

    // Reset pagination to first page
    resetPagination() {
      this.pagination.offset = 0;
      this.pagination.currentPage = 1;
      this.pagination.rangeStart = 1;
      this.pagination.rangeEnd = this.pagination.limit;
    },

    // 2. View Call
    async viewCall(uniqueid) {
      try {
        const { data } = await axiosInstance.get(`/api-proxy/api/calls/${uniqueid}`, {
          headers: this.getAuthHeaders()
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
          headers: this.getAuthHeaders(),
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
          headers: this.getAuthHeaders(),
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
          headers: this.getAuthHeaders()
        });
        return data;
      } catch (err) {
        throw new Error(err.message || 'Failed to fetch pivot report');
      }
    }
  }
});
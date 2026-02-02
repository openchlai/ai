// src/stores/caseStore.js
import { defineStore } from 'pinia';
import axiosInstance from '@/utils/axios';
import { useAuthStore } from './auth';

export const useCaseStore = defineStore('cases', {
  state: () => ({
    cases: [],
    cases_k: {},
    cases_ctx: [],
    caseCount: 0,
    loading: false,
    error: null,
    // Pagination state
    pagination: {
      offset: 0,
      limit: 20,
      currentPage: 1,
      totalRecords: 0,
      rangeStart: 1,
      rangeEnd: 20
    }
  }),

  getters: {
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

    // Parse cases_ctx to update pagination state
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

    // 1. Create Case
    async createCase(payload) {
      try {
        this.loading = true;
        const { data } = await axiosInstance.post('api/cases', payload, {
          headers: {
            ...this.getAuthHeaders(),
            'Content-Type': 'application/json'
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

    // 2. Update Case
    async updateCase(id, payload) {
      try {
        this.loading = true;
        const { data } = await axiosInstance.post(`api/cases/${id}`, payload, {
          headers: this.getAuthHeaders()
        });
        return data;
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 3. View Case
    async viewCase(id) {
      try {
        this.loading = true;
        const { data } = await axiosInstance.get(`api/cases/${id}`, {
          headers: this.getAuthHeaders()
        });
        return data;
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // 4. List Cases with pagination support
    async listCases(params = {}) {
      try {
        this.loading = true;

        // Build pagination params matching control UI format
        const paginationParams = {
          _c: params._c || this.pagination.limit,
          _o: params._o !== undefined ? params._o : this.pagination.offset,
          _a: 0,
          ...params
        };

        // Remove internal pagination keys
        delete paginationParams.page;
        delete paginationParams.limit;

        const { data } = await axiosInstance.get('api/cases/', {
          params: paginationParams,
          headers: this.getAuthHeaders()
        });
        console.log('Cases data:', data);
        this.cases = data.cases || [];
        this.cases_k = data.cases_k || {};
        this.cases_ctx = data.cases_ctx || [];
        this.caseCount = data.cases_nb?.[0]?.[1] || this.pagination.totalRecords || this.cases.length;

        // Parse pagination context from response
        this.parsePaginationContext(data.cases_ctx);
      } catch (err) {
        this.error = err.message;
        throw err;
      } finally {
        this.loading = false;
      }
    },

    // Go to next page
    async nextPage(filters = {}) {
      if (!this.hasNextPage) return;
      const newOffset = this.pagination.offset + this.pagination.limit;
      await this.listCases({ ...filters, _o: newOffset, _c: this.pagination.limit });
    },

    // Go to previous page
    async prevPage(filters = {}) {
      if (!this.hasPrevPage) return;
      const newOffset = Math.max(0, this.pagination.offset - this.pagination.limit);
      await this.listCases({ ...filters, _o: newOffset, _c: this.pagination.limit });
    },

    // Go to specific page
    async goToPage(page, filters = {}) {
      const newOffset = (page - 1) * this.pagination.limit;
      await this.listCases({ ...filters, _o: newOffset, _c: this.pagination.limit });
    },

    // Change page size
    async setPageSize(size, filters = {}) {
      this.pagination.limit = size;
      this.pagination.offset = 0;
      await this.listCases({ ...filters, _o: 0, _c: size });
    },

    // Reset pagination to first page
    resetPagination() {
      this.pagination.offset = 0;
      this.pagination.currentPage = 1;
      this.pagination.rangeStart = 1;
      this.pagination.rangeEnd = this.pagination.limit;
    },

    // 5. CSV Download
    async downloadCSV(params = {}) {
      try {
        const response = await axiosInstance.get('api/cases/', {
          params: { ...params, csv: 1 },
          headers: this.getAuthHeaders(),
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
        const { data } = await axiosInstance.get('api/cases/rpt', {
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
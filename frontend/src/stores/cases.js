import { defineStore } from 'pinia';
import axiosInstance from '@/utils/axios';

export const useCaseStore = defineStore('cases', {
  state: () => ({
    cases: [],
    cases_k: {},
    caseCount: 0,
    loading: false,
    error: null,
  }),

  getters: {
    // Returns a function so we can pass the search query from components
    searchCases: (state) => (query) => {
      const list = Array.isArray(state.cases) ? state.cases : [];
      const text = (query || '').toString().trim().toLowerCase();
      if (!text) return list;

      const k = state.cases_k || {};

      const getByKey = (item, keyDef) => {
        if (!keyDef || !Array.isArray(keyDef) || keyDef.length === 0) return '';
        const key = keyDef[0];
        const value = item?.[key];
        return value == null ? '' : String(value);
      };

      return list.filter((c) => {
        const title = getByKey(c, k.cat_1);
        const assignedTo = getByKey(c, k.assigned_to);
        const createdBy = getByKey(c, k.created_by);
        const source = getByKey(c, k.source);
        const idValue = getByKey(c, k.id);

        return (
          title.toLowerCase().includes(text) ||
          assignedTo.toLowerCase().includes(text) ||
          createdBy.toLowerCase().includes(text) ||
          source.toLowerCase().includes(text) ||
          idValue.toLowerCase().includes(text)
        );
      });
    },
    // Search contacts (reporters) by name and phone using cases_k mappings
    searchContacts: (state) => (query) => {
      const list = Array.isArray(state.cases) ? state.cases : [];
      const text = (query || '').toString().trim().toLowerCase();
      if (!text) return [];

      const k = state.cases_k || {};
      const getByKey = (item, keyDef) => {
        if (!keyDef || !Array.isArray(keyDef) || keyDef.length === 0) return '';
        const key = keyDef[0];
        const value = item?.[key];
        return value == null ? '' : String(value);
      };

      const nameKey = k.reporter_fullname;
      const phoneKey = k.reporter_phone;
      const primaryMatches = list.filter((c) => {
        const name = getByKey(c, nameKey).toLowerCase();
        const phone = getByKey(c, phoneKey);
        return (name && name.includes(text)) || (phone && phone.includes(query));
      });

      if (primaryMatches.length > 0) return primaryMatches;

      // Fallback: generic scan across all string-ish fields on each item
      return list.filter((item) => {
        // Support both array-like rows and object rows
        const values = Array.isArray(item)
          ? item
          : Object.values(item ?? {});
        return values.some((val) => {
          if (val == null) return false;
          const s = String(val).toLowerCase();
          return s.includes(text);
        });
      });
    }
  },

  actions: {
    // 1. Create Case
    async createCase(payload) {
      try {
        this.loading = true;
        const { data } = await axiosInstance.post('api/cases', payload, {
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe',
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

    // 3. View Case
    async viewCase(id) {
      try {
        this.loading = true;
        const { data } = await axiosInstance.get(`api/cases/${id}`, {
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

    // 4. List Cases
    async listCases(params = {}) {
      try {
        this.loading = true;
        const { data } = await axiosInstance.get('api/cases/', {
          params,
          headers: {
            'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe'
          }
        });
        console.log('Cases data:', data);
        this.cases = data.cases || [];
        this.cases_k = data.cases_k || {};
        this.caseCount = data.cases_nb?.[0]?.[1] || this.cases.length;
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
        const response = await axiosInstance.get('api/cases/', {
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
        const { data } = await axiosInstance.get('api/cases/rpt', {
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

import { defineStore } from 'pinia';
import axiosInstance from '@/utils/axios';

export const useCategoryStore = defineStore('categories', {
  state: () => ({
    // MANDATORY pieces
    categories: [],
    categories_k: {},
    subcategories: [],
    subcategories_k: {},
    subcategories_ctx: [],

    // count for subcategories (replaces categories_count)
    subcategories_count: 0,

    loading: false,
    error: null,
  }),

  actions: {
    async listCategories(params = {}) {
      this.loading = true; this.error = null;
      try {
        const { data } = await axiosInstance.get('api/categories/', {
          params,
          headers: { 'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe' }
        });

        console.log('listCategories', data);
        this.categories        = data.categories || [];
        this.categories_k      = data.categories_k || {};
        this.subcategories     = data.subcategories || [];
        this.subcategories_k   = data.subcategories_k || {};
        this.subcategories_ctx = data.subcategories_ctx || [];
        this.subcategories_count =
          Array.isArray(this.subcategories) ? this.subcategories.length :
          (data.subcategories_nb?.[0]?.[1] ?? 0);

        return data;
      } catch (err) {
        this.error = err?.message || 'Failed to list categories';
        throw err;
      } finally {
        this.loading = false;
      }
    },

    async viewCategory(id, params = {}) {
      this.loading = true; this.error = null;
      try {
        const { data } = await axiosInstance.get(`api/categories/${id}`, {
          params,
          headers: { 'X-API-Key': '21mku1hhf5gg4om161jk5fdfbe' }
        });

        console.log('viewCategory', data);
        this.categories        = data.categories || [];
        this.categories_k      = data.categories_k || {};
        this.subcategories     = data.subcategories || [];
        this.subcategories_k   = data.subcategories_k || {};
        this.subcategories_ctx = data.subcategories_ctx || [];
        this.subcategories_count =
          Array.isArray(this.subcategories) ? this.subcategories.length :
          (data.subcategories_nb?.[0]?.[1] ?? 0);

        return data;
      } catch (err) {
        this.error = err?.message || 'Failed to view category';
        throw err;
      } finally {
        this.loading = false;
      }
    }
  }
});

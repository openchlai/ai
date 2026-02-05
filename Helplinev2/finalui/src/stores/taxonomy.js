import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'
import { ENVIRONMENT_REGISTRY, getEnvironmentConfig } from '@/config/taxonomyContract'
import { useAuthStore } from './auth'

export const useTaxonomyStore = defineStore('taxonomy', {
    state: () => {
        const defaultCountry = import.meta.env.VITE_DEFAULT_COUNTRY || 'TZ';
        const config = getEnvironmentConfig(defaultCountry);
        console.log(`[TaxonomyStore] Initializing with ${defaultCountry}`, config.ROOTS);

        return {
            categoriesCache: {}, // { parentId: { items, k, ctx } }
            subcategories: [],
            subcategories_k: {},
            subcategories_ctx: [],
            loading: false,
            error: null,
            countryCode: defaultCountry,
            endpoints: config.ENDPOINTS,
            voip: config.VOIP,
            roots: config.ROOTS,
            triggers: config.TRIGGERS,
            dispositions: config.DISPOSITIONS || {}
        };
    },

    actions: {
        /**
         * Dynamically switch taxonomy rooted IDs AND endpoints based on country.
         * Useful for multi-tenant deployments.
         */
        setCountry(countryCode) {
            const config = getEnvironmentConfig(countryCode);
            if (config) {
                this.countryCode = countryCode;
                this.endpoints = config.ENDPOINTS;
                this.voip = config.VOIP;
                this.roots = config.ROOTS;
                this.triggers = config.TRIGGERS;
                this.dispositions = config.DISPOSITIONS || {};
                this.categoriesCache = {}; // Flush cache as IDs/Endpoints might have changed

                // Update axios base if needed (be careful with circular refs)
                if (config.ENDPOINTS.API_BASE) {
                    axiosInstance.defaults.baseURL = config.ENDPOINTS.API_BASE;
                }
            }
        },

        /**
         * Future-proof: Fetch taxonomy mapping from the backend API.
         * This allows the backend to serve its own config.php values.
         */
        async fetchConfigFromBackend() {
            try {
                const { data } = await axiosInstance.get('api/config/taxonomy', {
                    headers: this.getAuthHeaders()
                });
                if (data && data.roots) {
                    this.roots = { ...this.roots, ...data.roots };
                    this.triggers = { ...this.triggers, ...data.triggers };
                }
            } catch (err) {
                console.warn('[TaxonomyStore] Could not fetch remote config, using local defaults.', err);
            }
        },
        getAuthHeaders() {
            const authStore = useAuthStore()
            return {
                'Session-Id': authStore.sessionId
            }
        },

        /**
         * Backward compatible name for BaseSelect
         */
        async viewCategory(parentId, forceRefresh = false) {
            const data = await this.getCategories(parentId, forceRefresh)
            if (data) {
                this.subcategories = data.items
                this.subcategories_k = data.keys
                this.subcategories_ctx = data.context
            }
            return data
        },

        /**
         * Fetch children categories for a given parent ID.
         * Uses caching to prevent redundant API calls.
         */
        async getCategories(parentId, forceRefresh = false) {
            if (!parentId || parentId == 0) return null

            if (!forceRefresh && this.categoriesCache[parentId]) {
                return this.categoriesCache[parentId]
            }

            this.loading = true
            this.error = null
            try {
                const { data } = await axiosInstance.get(`api/categories/${parentId}`, {
                    headers: this.getAuthHeaders()
                })

                const result = {
                    items: data.subcategories || [],
                    keys: data.subcategories_k || {},
                    context: data.subcategories_ctx || []
                }

                this.categoriesCache[parentId] = result
                return result
            } catch (err) {
                this.error = err?.message || `Failed to fetch categories for ${parentId}`
                console.error('[TaxonomyStore] Request Error:', err)
                throw err
            } finally {
                this.loading = false
            }
        },

        /**
         * Search subcategories across the tree (Compatibility method)
         */
        async searchSubcategories(params = {}) {
            this.loading = true
            try {
                const { data } = await axiosInstance.get('api/subcategories/', {
                    params,
                    headers: this.getAuthHeaders()
                })

                const result = {
                    items: data.subcategories || [],
                    keys: data.subcategories_k || {},
                    context: data.subcategories_ctx || []
                }

                this.subcategories = result.items
                this.subcategories_k = result.keys
                this.subcategories_ctx = result.context

                return result
            } catch (err) {
                this.error = err?.message || 'Search failed'
                throw err
            } finally {
                this.loading = false
            }
        },

        /**
         * Check if a category ID matches a specific workflow trigger
         */
        isTrigger(id, triggerKey) {
            return String(id) === String(this.triggers[triggerKey])
        }
    }
})

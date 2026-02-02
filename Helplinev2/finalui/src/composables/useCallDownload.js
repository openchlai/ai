import { computed } from 'vue';

/**
 * Composable to handle Call List XLSX downloads
 * Preserves legacy parity by using native browser navigation and GET parameters.
 */
export function useCallDownload() {

    /**
     * Generates the legacy-compatible download URL
     * @param {Object} activeFilters - Current filter state from the UI
     * @returns {string} Fully qualified or relative download URL
     */
    const getDownloadUrl = (activeFilters = {}) => {
        // 1. Base endpoint from legacy system (via our proxy for dev/prod consistency)
        // In production, this might be '/helpline/api/calls'
        // In dev, we use '/api-proxy/api/calls/' which maps to the same backend
        const baseUrl = '/api-proxy/api/calls/';

        // 2. Build Query Parameters
        const params = new URLSearchParams();

        // Add all active filters
        Object.entries(activeFilters).forEach(([key, value]) => {
            if (value !== undefined && value !== null && value !== '') {
                params.append(key, value);
            }
        });

        // 3. Append xlsx=1 unconditionally as per legacy requirement
        params.append('xlsx', '1');

        return `${baseUrl}?${params.toString()}`;
    };

    /**
     * Triggers the download using browser-native navigation
     * Reliance on backend response headers for file handling and session cookies for auth.
     * @param {Object} filters - Current active filters
     */
    const triggerDownload = (filters = {}) => {
        const url = getDownloadUrl(filters);

        console.log('🚀 Triggering legacy Excel download:', url);

        // Use native navigation to ensure browser handles the Content-Disposition header
        // and automatically includes session cookies.
        window.location.href = url;
    };

    return {
        triggerDownload,
        getDownloadUrl
    };
}

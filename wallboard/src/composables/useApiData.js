import { ref } from 'vue'
import { fetchCasesData as fetchFromApi, fetchCallsReportData } from "@/utils/axios.js"

export function useApiData(axiosInstance) {
  // API data state
  const apiData = ref(null)
  const apiError = ref(null)
  const apiLoading = ref(false)

  // Calls report data state
  const callsReportData = ref(null)
  const callsReportError = ref(null)
  const callsReportLoading = ref(false)

  const fetchCallsReportDataComposable = async () => {
    // Only show loading if we don't have data yet
    if (!callsReportData.value) {
      callsReportLoading.value = true
    }
    callsReportError.value = null

    try {
      const data = await fetchCallsReportData()

      if (data) {
        callsReportData.value = data
      } else {
        console.warn('API returned success but data was null/undefined')
      }
    } catch (error) {
      callsReportError.value = error.message
    } finally {
      callsReportLoading.value = false
    }
  }

  // Fetch cases data using the corrected function from axios.js
  const fetchCasesDataComposable = async () => {
    if (!apiData.value) {
      apiLoading.value = true
    }
    apiError.value = null

    try {
      const data = await fetchFromApi()

      // Validation: Check for presence of stats or reporting keys
      const hasStats = data && (data.stats || data.calls_fmt || data.calls)

      if (hasStats) {
        apiData.value = data
      } else if (data) {
        console.warn('API returned success but no case/stat metrics found:', data)
      }
    } catch (error) {
      apiError.value = error.message
    } finally {
      apiLoading.value = false
    }
  }

  return {
    // Cases data
    apiData,
    apiError,
    apiLoading,
    fetchCasesData: fetchCasesDataComposable,

    // Calls report data  
    callsReportData,
    callsReportError,
    callsReportLoading,
    fetchCallsReportData: fetchCallsReportDataComposable
  }
}
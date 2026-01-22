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

  // Fetch calls report data using the new function from axios.js
  const fetchCallsReportDataComposable = async () => {
    callsReportLoading.value = true
    callsReportError.value = null
    
    try {
      const data = await fetchCallsReportData()
      
      if (data) {
        callsReportData.value = data
      } else {
        throw new Error('No calls report data returned from API')
      }
    } catch (error) {
      callsReportError.value = error.message
    } finally {
      callsReportLoading.value = false
    }
  }

  // Fetch cases data using the corrected function from axios.js
  const fetchCasesDataComposable = async () => {
    apiLoading.value = true
    apiError.value = null
    
    try {
      const data = await fetchFromApi()
      
      console.log('Fetched cases data:', data) 
      if (data) {
        apiData.value = data
      } else {
        throw new Error('No data returned from API')
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
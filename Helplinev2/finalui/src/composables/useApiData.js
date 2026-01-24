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

      // console.log('Fetched cases data:', data) 
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

  // Full Wallboard data state
  const wallboardData = ref({ live: [], users: [], live_k: {}, users_k: {} })
  const liveAgentsLoading = ref(false)

  const fetchLiveAgents = async () => {
    liveAgentsLoading.value = true
    try {
      const { data } = await axiosInstance.get('api/wallonly/', {
        params: { _c: 50 }
      })
      if (data) {
        wallboardData.value = {
          live: data.live || [],
          users: data.users || [],
          live_k: data.live_k || {},
          users_k: data.users_k || {}
        }
      }
    } catch (error) {
      console.error('Failed to fetch live agents:', error)
    } finally {
      liveAgentsLoading.value = false
    }
  }

  return {
    // Cases data
    apiData,
    apiError,
    apiLoading,
    fetchCasesData: fetchCasesDataComposable,

    // Wallboard Data
    wallboardData,
    liveAgentsLoading,
    fetchLiveAgents,

    // Calls report data  
    callsReportData,
    callsReportError,
    callsReportLoading,
    fetchCallsReportData: fetchCallsReportDataComposable
  }
}
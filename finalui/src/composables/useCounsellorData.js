import { ref } from 'vue'

export function useCounsellorData(axiosInstance) {
  // Counsellor names state - using reactive refs for better reactivity
  const counsellorNames = ref({})
  const nameLoadingStates = ref({})
  
  // Counsellor stats state
  const counsellorStats = ref({})
  const statsLoadingStates = ref({})

  // Function to fetch counsellor stats by extension
  const fetchCounsellorStats = async (extension) => {
    if (!extension || extension === '--') {
      return
    }

    // Don't fetch if already loading
    if (statsLoadingStates.value[extension]) {
      return
    }
    
    // Don't fetch if already cached
    if (counsellorStats.value[extension]) {
      return
    }
    
    try {
      statsLoadingStates.value[extension] = true
      
      const response = await axiosInstance.get('api/wallonly/', {
        params: {
          exten: extension,
          stats: 1
        }
      })
      
      if (response.data && response.data.stats && response.data.stats.length > 0) {
        // Extract stats from response format: [["0","36","0"]]
        const statsData = response.data.stats[0]
        
        if (Array.isArray(statsData) && statsData.length >= 3) {
          const answered = statsData[0] || '0'
          const missed = statsData[1] || '0'
          const talkTime = statsData[2] || '0'
          
          const stats = {
            answered: answered,
            missed: missed,
            talkTime: talkTime
          }
          
          counsellorStats.value[extension] = stats
        } else {
          counsellorStats.value[extension] = { answered: '0', missed: '0', talkTime: '0' }
        }
      } else {
        counsellorStats.value[extension] = { answered: '0', missed: '0', talkTime: '0' }
      }
    } catch (error) {
      counsellorStats.value[extension] = { answered: '0', missed: '0', talkTime: '0' }
    } finally {
      statsLoadingStates.value[extension] = false
    }
  }

  // Function to fetch counsellor name by extension
  const fetchCounsellorName = async (extension) => {
    if (!extension || extension === '--') {
      return
    }

    // Don't fetch if already loading
    if (nameLoadingStates.value[extension]) {
      return
    }
    
    // Don't fetch if already cached
    if (counsellorNames.value[extension]) {
      return
    }
    
    try {
      nameLoadingStates.value[extension] = true
      
      const response = await axiosInstance.get('api/wallonly/', {
        params: {
          exten: extension,
          _c: 1
        }
      })
      
      if (response.data && response.data.users && response.data.users.length > 0) {
        // Extract name from response format: [["329","Natalie"]]
        const userData = response.data.users[0]
        
        if (Array.isArray(userData) && userData.length >= 2) {
          const extractedName = userData[1]
          const name = extractedName || 'Unknown'
          counsellorNames.value[extension] = name
        } else {
          counsellorNames.value[extension] = 'Unknown'
        }
      } else {
        counsellorNames.value[extension] = 'Unknown'
      }
    } catch (error) {
      counsellorNames.value[extension] = 'Unknown'
    } finally {
      nameLoadingStates.value[extension] = false
    }
  }

  return {
    counsellorNames,
    counsellorStats,
    nameLoadingStates,
    statsLoadingStates,
    fetchCounsellorName,
    fetchCounsellorStats
  }
}
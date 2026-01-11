import { reactive } from 'vue'

export function useCounsellorData(axiosInstance) {
  // Use reactive for better deep property tracking in Vue 3
  const counsellorNames = reactive({})
  const nameLoadingStates = reactive({})

  const counsellorStats = reactive({})
  const statsLoadingStates = reactive({})

  // Function to fetch counsellor stats by extension
  const fetchCounsellorStats = async (extension) => {
    if (!extension || extension === '--') return

    // Don't fetch if already loading
    if (statsLoadingStates[extension]) return

    try {
      statsLoadingStates[extension] = true

      const response = await axiosInstance.get('/rpt', {
        params: {
          exten: extension,
          stats: 1
        }
      })

      console.log(`Stats Response for ${extension}:`, response.data)

      if (response.data && response.data.stats && response.data.stats.length > 0) {
        const statsData = response.data.stats[0]

        if (Array.isArray(statsData) && statsData.length >= 3) {
          counsellorStats[extension] = {
            answered: statsData[0] || '0',
            missed: statsData[1] || '0',
            talkTime: statsData[2] || '0'
          }
        } else {
          counsellorStats[extension] = { answered: '0', missed: '0', talkTime: '0' }
        }
      } else {
        counsellorStats[extension] = { answered: '0', missed: '0', talkTime: '0' }
      }
    } catch (error) {
      console.error(`Error fetching stats for ${extension}:`, error)
      counsellorStats[extension] = { answered: '0', missed: '0', talkTime: '0' }
    } finally {
      statsLoadingStates[extension] = false
    }
  }

  // Function to fetch counsellor name by extension
  const fetchCounsellorName = async (extension) => {
    if (!extension || extension === '--') return

    // Don't fetch if already loading OR if we already have a valid name (not 'Unknown')
    const currentName = counsellorNames[extension]
    if (nameLoadingStates[extension] || (currentName && currentName !== 'Unknown')) return

    try {
      nameLoadingStates[extension] = true

      const response = await axiosInstance.get('/rpt', {
        params: {
          exten: extension,
          _c: 1
        }
      })

      if (response.data && response.data.users && response.data.users.length > 0) {
        const userData = response.data.users[0]

        if (Array.isArray(userData) && userData.length >= 2) {
          counsellorNames[extension] = userData[1] || 'Unknown'
        } else {
          counsellorNames[extension] = 'Unknown'
        }
      } else {
        counsellorNames[extension] = 'Unknown'
      }
    } catch (error) {
      console.error(`Error fetching name for ${extension}:`, error)
      counsellorNames[extension] = 'Unknown'
    } finally {
      nameLoadingStates[extension] = false
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
<template>
  <div class="container" :class="{ 'dark-mode': isDarkMode }">
    <!-- Header Component -->
    <WallboardHeader 
      :connection-status="connectionClass"
      :connection-label="connectionLabel"
      :last-update="lastUpdate"
      :is-dark-mode="isDarkMode"
      @toggle-theme="toggleDarkMode"
    />

    <!-- Top Row: Call Status Cards -->
    <CallsStatusCards 
      :loading="callsReportLoading"
      :error="callsReportError"
      :cards="callsCards"
    />

    <!-- Main Content: Two Column Layout -->
    <div class="main-content">
      <!-- Left Column: Tables -->
      <div class="tables-column">
        <!-- Counsellors Table Component -->
        <CounsellorsTable 
          :counsellors="counsellorsWithQueueData"
          :online-count="onlineCounsellorsCount"
        />

        <!-- Callers Table Component -->
        <CallersTable 
          :callers="callersData"
          :online-count="onlineCallersCount"
        />
      </div>

      <!-- Right Column: Cases Tiles -->
      <div class="cases-column">
        <CasesTiles :tiles="casesTiles" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import axiosInstance from "@/utils/axios.js"

// Import new components
import WallboardHeader from '@/components/wallboard/WallboardHeader.vue'
import CasesTiles from '@/components/wallboard/CasesTiles.vue'
import CallsStatusCards from '@/components/wallboard/CallsStatusCards.vue'
//import TopStatsRow from './components/TopStatsRow.vue'
import CounsellorsTable from '@/components/wallboard/CounsellorsTable.vue'
import CallersTable from '@/components/wallboard/CallersTable.vue'
// import QueueActivityGraph from './components/QueueActivityGraph.vue'

// Import utilities
import { useWebSocketConnection } from '@/composables/useWebSocketConnection.js'
import { useCounsellorData } from '@/composables/useCounsellorData'
import { useApiData } from '@/composables/useApiData'
import { formatDuration, getStatusText } from '@/utils/formatters'

const WSHOST = 'wss://192.168.10.12:8384/ami/sync?c=-2'

export default {
  name: 'App',
  components: {
    WallboardHeader,
    CasesTiles,
    CallsStatusCards,
    //TopStatsRow,
    CounsellorsTable,
    CallersTable,
    //QueueActivityGraph
  },
  setup() {
    const isDarkMode = ref(false)
    
    // Use WebSocket composable
    const {
      channels,
      wsReady,
      lastUpdate,
      connect,
      disconnect
    } = useWebSocketConnection(WSHOST)
    
    // Use API data composable
    const {
      apiData,
      callsReportData,
      callsReportError,
      callsReportLoading,
      fetchCasesData,
      fetchCallsReportData
    } = useApiData(axiosInstance)
    
    // Use counsellor data composable
    const {
      counsellorNames,
      counsellorStats,
      fetchCounsellorName,
      fetchCounsellorStats
    } = useCounsellorData(axiosInstance)

    // Cases tiles with real data from API
    const casesTiles = computed(() => {
      const stats = apiData.value?.stats || {}
      
      const tiles = [
        { 
          id: 'ct1', 
          label: "TODAY'S ANSWERED CALLS", 
          value: stats.calls_today || '--', 
          variant: 'c-blue' 
        },
        { 
          id: 'ct2', 
          label: "TODAY'S CASES", 
          value: stats.cases_today || '--', 
          variant: 'c-amber' 
        },
        { 
          id: 'ct3', 
          label: 'ONGOING CASES', 
          value: stats.cases_ongoing_total || '--', 
          variant: 'c-red' 
        },
        { 
          id: 'ct4', 
          label: 'MONTH CLOSED CASES', 
          value: stats.cases_closed_this_month || '--', 
          variant: 'c-green' 
        },
        { 
          id: 'ct5', 
          label: 'TOTAL CALLS', 
          value: stats.calls_total || '--', 
          variant: 'c-black' 
        },
        { 
          id: 'ct6', 
          label: 'TOTAL CASES', 
          value: stats.cases_total || '--', 
          variant: 'c-black' 
        }
      ]
      
      return tiles
    })

    // Calls cards data computed from API response
    const callsCards = computed(() => {
      if (!callsReportData.value || !callsReportData.value.calls) {
        return []
      }
      
      return callsReportData.value.calls.map((call, index) => {
        const [status, count] = call
        return {
          id: `call-${index}`,
          status: status,
          count: parseInt(count) || 0,
          label: status.charAt(0).toUpperCase() + status.slice(1),
          variant: getCallStatusVariant(status)
        }
      })
    })

    // Helper function to assign color variants based on call status
    const getCallStatusVariant = (status) => {
      const statusLower = status.toLowerCase()
      switch (statusLower) {
        case 'answered': return 'success'
        case 'abandoned': return 'warning'
        case 'missed': return 'danger'
        case 'noanswer': return 'danger'
        case 'voicemail': return 'info'
        case 'ivr': return 'primary'
        case 'dump': return 'secondary'
        default: return 'secondary'
      }
    }

    // Calculate queue statistics from channel data
    const queueStats = computed(() => {
      const stats = { 
        total: channels.value.length,
        inQueue: 0, 
        connected: 0, 
        onHold: 0, 
        hangup: 0
      }
      
      channels.value.forEach(ch => {
        if (Number(ch.CHAN_STATE_QUEUE)) stats.inQueue++
        if (Number(ch.CHAN_STATE_CONNECT)) stats.connected++
        if (Number(ch.CHAN_STATE_HOLD)) stats.onHold++
        if (Number(ch.CHAN_STATE_HANGUP)) stats.hangup++
      })

      return stats
    })

    // Separate counsellors and callers based on CHAN_CONTEXT
    const counsellorsWithQueueData = computed(() => {
      const counsellorChannels = channels.value.filter(ch => {
        const context = (ch.CHAN_CONTEXT || '').toLowerCase()
        return context === 'agentlogin'
      })

      return counsellorChannels.map((ch) => {
        const extension = ch.CHAN_EXTEN || '--'
        const name = counsellorNames.value[extension] || 'Unknown'
        const stats = counsellorStats.value[extension] || { answered: '--', missed: '--', talkTime: '--' }

        // Find connected caller by matching bridge IDs
        let connectedCallerNumber = '--'
        if (Number(ch.CHAN_STATE_CONNECT) && ch.CHAN_BRIDGE_ID) {
          const connectedCaller = callersData.value.find(caller => 
            caller.channelData.CHAN_BRIDGE_ID === ch.CHAN_BRIDGE_ID
          )
          if (connectedCaller) {
            connectedCallerNumber = connectedCaller.callerNumber
          }
        }

        return {
          id: ch.CHAN_UNIQUEID || ch._uid,
          extension: extension,
          name: name,
          caller: connectedCallerNumber,
          answered: stats.answered,
          missed: stats.missed,
          talkTime: '--',
          queueStatus: getStatusText(ch),
          duration: Number(ch.CHAN_STATE_CONNECT) ? formatDuration(ch.CHAN_TS) : '--',
          isOnline: true,
          channelData: ch,
          channel: ch.CHAN_CHAN || '--',
          vector: ch.CHAN_VECTOR || '--',
          campaign: ch.CHAN_CAMPAIGN_ID || '--'
        }
      })
    })

    // Callers data - filtered by DLPN_callcenter context
    const callersData = computed(() => {
      return channels.value
        .filter(ch => {
          const context = (ch.CHAN_CONTEXT || '').toLowerCase()
          return context === 'trunk' || context === 'dlpn_callcenter'
        })
        .map((ch) => {
          return {
            id: ch.CHAN_UNIQUEID || ch._uid,
            callerNumber: ch.CHAN_CALLERID_NUM || '--',
            vector: ch.CHAN_VECTOR || '--',
            waitTime: formatDuration(ch.CHAN_TS),
            queueStatus: getStatusText(ch),
            bridgeId: ch.CHAN_BRIDGE_ID || '--',
            campaign: ch.CHAN_CAMPAIGN_ID || '--',
            sipCallId: ch.CHAN_SIPCALLID || '--',
            isOnline: true,
            channelData: ch
          }
        })
    })

    // Count of online counsellors and callers
    const onlineCounsellorsCount = computed(() => 
      counsellorsWithQueueData.value.filter(c => c.isOnline).length
    )
    
    const onlineCallersCount = computed(() => 
      callersData.value.filter(c => c.isOnline).length
    )

    // Connection status helpers
    const connectionClass = computed(() => 
      wsReady.value === 'open' ? 'on' : (wsReady.value === 'connecting' ? 'connecting' : 'off')
    )
    
    const connectionLabel = computed(() => {
      if (wsReady.value === 'connecting') return 'Connecting...'
      if (wsReady.value === 'open') return 'Connected'
      if (wsReady.value === 'error') return 'Error'
      return 'Disconnected'
    })

    // Theme management
    const applyThemeClass = () => {
      document.documentElement.classList.toggle('dark-mode', isDarkMode.value)
    }

    const toggleDarkMode = () => {
      isDarkMode.value = !isDarkMode.value
      localStorage.setItem('darkMode', isDarkMode.value.toString())
      applyThemeClass()
    }

    // Lifecycle
    onMounted(() => {
      const savedDarkMode = localStorage.getItem('darkMode')
      if (savedDarkMode !== null) {
        isDarkMode.value = savedDarkMode === 'true'
      }
      applyThemeClass()
      
      // Connect to WebSocket
      connect(channels, fetchCounsellorName, fetchCounsellorStats)
      
      // Fetch initial data
      fetchCasesData()
      fetchCallsReportData()
      
      // Refresh data every 5 minutes
      const dataInterval = setInterval(() => {
        fetchCasesData()
        fetchCallsReportData()
      }, 300000)
      
      onBeforeUnmount(() => {
        clearInterval(dataInterval)
        disconnect()
      })
    })

    // Keep DOM class in sync
    watch(isDarkMode, applyThemeClass)

    return {
      // State
      isDarkMode,
      
      // Data
      casesTiles,
      counsellorsWithQueueData,
      onlineCounsellorsCount,
      callsReportError,
      callsReportLoading,
      callsCards,
      callersData,
      onlineCallersCount,
      
      // Connection status
      connectionClass,
      connectionLabel,
      lastUpdate,
      
      // Axios instance for child components
      axiosInstance,
      
      // Methods
      toggleDarkMode
    }
  }
}
</script>

<style>
/* TV-Optimized Global Styles */
.container {
  max-width: 100vw;
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 5px 8px;
  background-color: #f8fafc;
  transition: background-color 0.3s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dark-mode .container {
  background-color: #1a202c;
  color: #e2e8f0;
}

/* Header - TV optimized */
.container > :first-child {
  flex-shrink: 0;
  margin-bottom: 6px;
}

/* Call status cards - TV optimized */
.container > :nth-child(2) {
  flex-shrink: 0;
  margin-bottom: 8px;
}

/* Main content - TV optimized layout with wider cases column */
.main-content {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 12px;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

/* Left column for tables - TV optimized */
.tables-column {
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow: hidden;
  min-height: 0;
}

/* Right column for cases tiles - TV optimized */
.cases-column {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

/* TV Screen specific optimizations */
@media screen and (min-width: 1920px) {
  .container {
    padding: 6px 10px;
  }
  
  .main-content {
    grid-template-columns: 1fr 400px;
    gap: 15px;
  }
}

@media screen and (max-width: 1600px) {
  .container {
    padding: 4px 6px;
  }
  
  .main-content {
    grid-template-columns: 1fr 300px;
    gap: 10px;
  }
}

/* 4K TV optimization */
@media screen and (min-width: 3840px) {
  .container {
    padding: 12px 20px;
  }
  
  .main-content {
    grid-template-columns: 1fr 500px;
    gap: 20px;
  }
}

/* Disable text selection for wallboard display */
.container {
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}

/* Optimize font rendering for TV displays */
.container {
  font-smooth: antialiased;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  font-display: swap;
}

/* Global scrollbar styling for TV */
::-webkit-scrollbar {
  width: 2px;
  height: 2px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: rgba(203, 213, 225, 0.3);
  border-radius: 1px;
}

.dark-mode ::-webkit-scrollbar-thumb {
  background: rgba(107, 114, 128, 0.3);
}

/* Remove all animations for better TV performance if needed */
@media (prefers-reduced-motion: reduce) {
  .container * {
    animation: none !important;
    transition: none !important;
  }
}
</style>
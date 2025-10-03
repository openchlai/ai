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

    <!-- Cases Grid Component -->
    <CasesTiles :tiles="casesTiles" />

    <!-- Calls Status Cards Component -->
    <CallsStatusCards 
      :loading="callsReportLoading"
      :error="callsReportError"
      :cards="callsCards"
    />

    <!-- Queue Activity Graph -->
    <QueueActivityGraph :axiosInstance="axiosInstance" />

    <!-- Top Statistics Component -->
    <TopStatsRow :stats="stats" />

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
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import axiosInstance from "@/utils/axios.js"

// Import new components
import WallboardHeader from './components/WallboardHeader.vue'
import CasesTiles from './components/CasesTiles.vue'
import CallsStatusCards from './components/CallsStatusCards.vue'
import TopStatsRow from './components/TopStatsRow.vue'
import CounsellorsTable from './components/CounsellorsTable.vue'
import CallersTable from './components/CallersTable.vue'
import QueueActivityGraph from './components/QueueActivityGraph.vue'

// Import utilities
import { useWebSocketConnection } from './composables/useWebSocketConnection'
import { useCounsellorData } from './composables/useCounsellorData'
import { useApiData } from './composables/useApiData'
import { formatDuration, getStatusText } from './utils/formatters'

const WSHOST = 'wss://192.168.10.120:8384/ami/sync?c=-2'

export default {
  name: 'App',
  components: {
    WallboardHeader,
    CasesTiles,
    CallsStatusCards,
    TopStatsRow,
    CounsellorsTable,
    CallersTable,
    QueueActivityGraph
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

      // TEMPORARY DEBUG - ADD THIS LINE  
  console.log('DEBUG - computed tiles:', tiles)
      
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

    // Get connected caller from CHAN_CID_NUM_2 (index 47) when agent is connected
    let connectedCallerNumber = '--'
    if (Number(ch.CHAN_STATE_CONNECT)) {
      // CHAN_CID_NUM_2 is at index 47 in the raw array
      const callerFromIndex47 = ch._raw?.[47] || ch.CHAN_CID_NUM_2
      connectedCallerNumber = callerFromIndex47 || '--'
    }

    return {
      id: ch.CHAN_UNIQUEID || ch._uid,
      extension: extension,
      name: name,
      caller: connectedCallerNumber, // Now using CHAN_CID_NUM_2
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
          return context === 'dlpn_callcenter'
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

    // TOP STATISTICS
    const stats = computed(() => [
      { id: 1, title: 'Total', value: queueStats.value.total.toString(), variant: 'total' },
      { id: 2, title: 'Answered', value: queueStats.value.connected.toString(), variant: 'answered' },
      { id: 3, title: 'In Queue', value: queueStats.value.inQueue.toString(), variant: 'abandoned' },
      { id: 4, title: 'On Hold', value: queueStats.value.onHold.toString(), variant: 'discarded' },
      { id: 5, title: 'Hangup', value: queueStats.value.hangup.toString(), variant: 'missed' },
      { id: 6, title: 'Online', value: counsellorsWithQueueData.value.filter(c => c.isOnline).length.toString(), variant: 'ivr' },
      { id: 7, title: 'Connected', value: queueStats.value.connected.toString(), variant: 'beep' }
    ])

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
      stats,
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
/* Global styles for the application */
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  min-height: 100vh;
  background-color: #f8fafc;
  transition: background-color 0.3s ease;
}

.dark-mode .container {
  background-color: #1a202c;
  color: #e2e8f0;
}

/* Global dark mode styles */
.dark-mode {
  background-color: #1a202c;
  color: #e2e8f0;
}

/* Responsive container */
@media (max-width: 1200px) {
  .container {
    max-width: 100%;
    padding: 0 15px;
  }
}

@media (max-width: 768px) {
  .container {
    padding: 0 10px;
  }
}

/* Scrollbar styling for dark mode */
.dark-mode ::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.dark-mode ::-webkit-scrollbar-track {
  background: #2d3748;
}

.dark-mode ::-webkit-scrollbar-thumb {
  background: #4a5568;
  border-radius: 4px;
}

.dark-mode ::-webkit-scrollbar-thumb:hover {
  background: #718096;
}
</style>
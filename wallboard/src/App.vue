<template>
  <div class="container" :class="{ 'dark-mode': isDarkMode }">
    <!-- Dynamic edge-to-edge layout, header minimized to gain space -->
    <WallboardHeader 
      class="compact-tv-header"
      :connection-status="connectionClass"
      :connection-label="connectionLabel"
      :last-update="lastUpdate"
      :is-dark-mode="isDarkMode"
      @toggle-theme="toggleDarkMode"
      @reconnect="handleReconnect"
    />

    <OperationalKPIs 
      :calls-in-queue="inQueueBadgeCount"
      :longest-wait-seconds="longestWaitSeconds"
      :active-calls="onCallCounsellorsCount"
      :available-agents="availableAgentsCount"
      :hangup-cards="callsCardsMapped"
      :service-level="serviceLevelValue"
      :voice-load="voiceLoadValue"
      :wa-load="waLoadValue"
    />

    <!-- Main Content Area: 3-Column Command Center Split -->
    <div class="dashboard-body">
      <!-- Column 1: Situational Awareness (Squeezed Stacked Tables) -->
      <div class="column situational-tables">
        <div class="table-v-wrap">
          <CounsellorsTable 
            :counsellors="paginatedCounsellors"
            :online-count="onlineCounsellorsCount"
          />
          <div class="pagination-indicator" v-if="counsellorTotalPages > 1">
            Page {{ counsellorPage + 1 }} / {{ counsellorTotalPages }}
          </div>
        </div>
        <div class="table-v-wrap">
          <CallersTable 
            :callers="paginatedCallers"
            :online-count="inQueueBadgeCount"
          />
          <div class="pagination-indicator" v-if="callerTotalPages > 1">
            Page {{ callerPage + 1 }} / {{ callerTotalPages }}
          </div>
        </div>
      </div>

      <!-- Column 2: Trends & Activity (Centered) -->
      <div class="column activity-trends">
        <QueueActivityGraph :axios-instance="axiosInstance" />
      </div>

      <!-- Column 3: Performance Summary (Sidebar) -->
      <div class="column performance-sidebar">
        <CasesTiles :tiles="casesTiles" />
      </div>
    </div>
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
import OperationalKPIs from './components/OperationalKPIs.vue'

// Import utilities
import { useWebSocketConnection } from './composables/useWebSocketConnection'
import { useCounsellorData } from './composables/useCounsellorData'
import { useApiData } from './composables/useApiData'
import { formatDuration, getStatusText, getDurationSeconds, formatNumberWithCommas } from './utils/formatters'
import { useAgentPresence } from './composables/useAgentPresence'

const getWsUrl = () => {
  // In production, use the defined production URL
  if (import.meta.env.PROD) return __APP_WS_URL__;
  
  // In development, always route through the local proxy
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const host = window.location.host;
  return `${protocol}//${host}/ws-proxy/sync?c=-2`;
};

const WSHOST = getWsUrl();

export default {
  name: 'App',
  components: {
    WallboardHeader,
    CasesTiles,
    CallsStatusCards,
    TopStatsRow,
    CounsellorsTable,
    CallersTable,
    QueueActivityGraph,
    OperationalKPIs
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

    // Use agent presence data from new endpoint
    const {
      agentPresenceChannels,
      fetchAgentPresence
    } = useAgentPresence()

    // Cases tiles with real data from API
    const casesTiles = computed(() => {
      const stats = apiData.value?.stats || {}
      
      const tiles = [
        { 
          id: 'ct1', 
          label: "TODAY'S ANSWERED CALLS", 
          value: formatNumberWithCommas(stats.calls_today), 
          variant: 'c-blue' 
        },
        { 
          id: 'ct2', 
          label: "TODAY'S CASES", 
          value: formatNumberWithCommas(stats.cases_today), 
          variant: 'c-amber' 
        },
        { 
          id: 'ct3', 
          label: 'ONGOING CASES', 
          value: formatNumberWithCommas(stats.cases_ongoing_total), 
          variant: 'c-red' 
        },
        { 
          id: 'ct4', 
          label: 'MONTH CLOSED CASES', 
          value: formatNumberWithCommas(stats.cases_closed_this_month), 
          variant: 'c-green' 
        },
        { 
          id: 'ct5', 
          label: 'TOTAL CALLS', 
          value: formatNumberWithCommas(stats.calls_total), 
          variant: 'c-black' 
        },
        { 
          id: 'ct6', 
          label: 'TOTAL CASES', 
          value: formatNumberWithCommas(stats.cases_total), 
          variant: 'c-black' 
        }
      ]
      
      return tiles
    })

    // Calls cards data computed from API response
    const callsCardsMapped = computed(() => {
      if (!callsReportData.value || !callsReportData.value.calls) {
        return []
      }
      
      return callsReportData.value.calls.map((call, index) => {
        const [status, count] = call
        const variant = getCallStatusVariant(status)
        return {
          id: `call-${index}`,
          status: status,
          count: parseInt(count) || 0,
          label: status.toUpperCase(),
          color: getHexColorForVariant(variant)
        }
      })
    })

    const getHexColorForVariant = (variant) => {
      const colors = {
        'success': '#059669',
        'warning': '#D97706',
        'danger': '#DC2626',
        'info': '#0ea5e9',
        'primary': '#1D3E8A',
        'secondary': '#64748b'
      }
      return colors[variant] || '#64748b'
    }

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

    // Unified channel list merging WebSocket and polled AMI data
    const mergedChannels = computed(() => {
      const channelMap = new Map()
      
      // 1. WebSocket data (most real-time)
      channels.value.forEach(ch => {
        if (ch.CHAN_UNIQUEID || ch._uid) {
          channelMap.set(ch.CHAN_UNIQUEID || ch._uid, { ...ch, source: 'ws' })
        }
      })
      
      // 2. Polled AMI data (reliable fallback)
      if (agentPresenceChannels.value) {
        agentPresenceChannels.value.forEach(ch => {
          const id = ch.CHAN_UNIQUEID || ch._uid
          if (id && !channelMap.has(id)) {
            channelMap.set(id, { ...ch, source: 'poll' })
          }
        })
      }
      
      const result = Array.from(channelMap.values())
      console.log(`[mergedChannels] Count: ${result.length} (WS: ${channels.value.length}, Poll: ${agentPresenceChannels.value.length})`)
      return result
    })

    // Calculate queue statistics from merged channel data
    const queueStats = computed(() => {
      const stats = { 
        total: mergedChannels.value.length,
        inQueue: 0, 
        connected: 0, 
        onHold: 0, 
        hangup: 0
      }
      
      mergedChannels.value.forEach(ch => {
        if (Number(ch.CHAN_STATE_QUEUE)) stats.inQueue++
        if (Number(ch.CHAN_STATE_CONNECT)) stats.connected++
        if (Number(ch.CHAN_STATE_HOLD)) stats.onHold++
        if (Number(ch.CHAN_STATE_HANGUP)) stats.hangup++
      })

      return stats
    })

    // Separate counsellors and callers based on CHAN_CONTEXT
    const counsellorsWithQueueData = computed(() => {
      // De-duplicate agents by extension from both WebSocket and Polled sources
      const allCounsellorChannelsMap = new Map()

      // 1. Process WebSocket channels
      // 1. Process all merged channels (WS + Poll)
      mergedChannels.value.forEach(ch => {
        const context = (ch.CHAN_CONTEXT || '').toLowerCase()
        const extension = ch.CHAN_EXTEN
        
        // Definitively Identify Agents
        const callerId = ch.CHAN_CALLERID_NUM || ''
        const isPSTN = callerId.startsWith('+') || callerId.length >= 7
        const isAgentContext = context === 'agentlogin' || context === 'from-internal'
        const hasAgentExtension = extension && extension !== '--' && extension.length <= 4
        
        const isAgent = isAgentContext || (hasAgentExtension && !isPSTN)
        
        if (isAgent && extension && extension !== '--') {
          allCounsellorChannelsMap.set(extension, ch)
        }
      })

      // Polled channels are already integrated via mergedChannels above

      return Array.from(allCounsellorChannelsMap.values()).map((ch) => {
        const extension = ch.CHAN_EXTEN || '--'
        // Use reactive metadata cache with fallbacks
        const name = counsellorNames[extension] || ch.CHAN_CALLERID_NAME || 'Unknown'
        const stats = counsellorStats[extension] || { answered: '--', missed: '--', talkTime: '--' }

        // Find connected caller by matching bridge IDs
        const connectedCallerNumber = Number(ch.CHAN_STATE_CONNECT) ? findConnectedCaller(ch.CHAN_BRIDGE_ID) : '--'

        return {
          id: ch.CHAN_UNIQUEID || ch._uid,
          extension: extension,
          name: name,
          caller: connectedCallerNumber,
          stats: stats,
          answered: stats.answered,
          missed: stats.missed,
          talkTime: stats.talkTime,
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

    // Unified Caller List (Unfiltered for metadata bridging)
    const allCallers = computed(() => {
      return mergedChannels.value
        .filter(ch => {
          const context = (ch.CHAN_CONTEXT || '').toLowerCase()
          const extension = ch.CHAN_EXTEN
          const callerId = ch.CHAN_CALLERID_NUM || ''
          
          // 1. Definitively Identify Agents
          // Agents are in specific contexts OR have short extensions (and aren't clearly PSTN numbers)
          const isPSTN = callerId.startsWith('+') || callerId.length >= 7
          const isAgentContext = context === 'agentlogin' || context === 'from-internal'
          const hasAgentExtension = extension && extension !== '--' && extension.length <= 4
          
          const isAgent = isAgentContext || (hasAgentExtension && !isPSTN)
                          
          // 2. Inclusion Logic for Callers
          // If NOT an agent, they are a potential caller.
          // We prioritize anyone in a queue state or with a vector.
          if (isAgent) return false
          
          return true // Everyone else is a caller leg
        })
        .map((ch) => ({
          id: ch.CHAN_UNIQUEID || ch._uid || `caller-${Math.random()}`,
          callerNumber: ch.CHAN_CALLERID_NUM || '--',
          vector: ch.CHAN_VECTOR || '--',
          waitTime: formatDuration(ch.CHAN_TS),
          queueStatus: getStatusText(ch),
          bridgeId: ch.CHAN_BRIDGE_ID || '--',
          channelName: ch.CHAN_CHAN || '',
          channelData: ch
        }))
    })

    // Callers data for the "Calls in Queue" table - including active connected calls
    const callersData = computed(() => {
      return allCallers.value.filter(c => {
        const status = c.queueStatus
        // Keep waiting calls AND active connected calls
        return status === 'In Queue' || status === 'IVR' || status === 'Ringing' || status === 'On Call'
      })
    })

    // Metadata Bridge: Find connected caller for an agent
    const findConnectedCaller = (bridgeId) => {
      if (!bridgeId || bridgeId === '--') return '--'
      const caller = allCallers.value.find(c => c.bridgeId === bridgeId)
      return caller ? caller.callerNumber : '--'
    }

    // Count of actual waiting callers (In Queue + IVR) for display
    const onlineCallersCount = computed(() => callersData.value.length)
    
    // Explicit count of those specifically in "In Queue" status for the red badge
    const inQueueBadgeCount = computed(() => {
      // De-duplicate by caller number to prevent ghost counts for the same caller
      const uniqueCallers = new Set()
      callersData.value.forEach(c => {
        if (c.queueStatus === 'In Queue' && c.callerNumber !== '--') {
          uniqueCallers.add(c.callerNumber)
        }
      })
      return uniqueCallers.size
    })
    
    const onlineCounsellorsCount = computed(() => counsellorsWithQueueData.value.length)

    const onCallCounsellorsCount = computed(() => 
      counsellorsWithQueueData.value.filter(c => 
        c.queueStatus.toLowerCase().includes('on call') || 
        c.queueStatus.toLowerCase().includes('ring')
      ).length
    )

    const availableAgentsCount = computed(() => 
      onlineCounsellorsCount.value - onCallCounsellorsCount.value
    )

    // Advanced Operational Metrics
    const longestWaitSeconds = computed(() => {
      if (callersData.value.length === 0) return 0
      return Math.max(...callersData.value.map(c => getDurationSeconds(c.channelData?.CHAN_TS || 0)))
    })

    const abandonedTodayValue = computed(() => {
      const card = callsCardsMapped.value.find(c => c.status.toLowerCase() === 'abandoned')
      return card ? card.count : 0
    })

    const totalCallsTodayValue = computed(() => {
      return callsCardsMapped.value.reduce((acc, c) => acc + c.count, 0) || 1
    })

    const answeredTodayValue = computed(() => {
      const card = callsCardsMapped.value.find(c => c.status.toLowerCase() === 'answered')
      return card ? card.count : 0
    })

    const serviceLevelValue = computed(() => {
      return Math.round((answeredTodayValue.value / totalCallsTodayValue.value) * 100)
    })

    const abandonedRateValue = computed(() => {
      return ((abandonedTodayValue.value / totalCallsTodayValue.value) * 100).toFixed(1)
    })

    // Calibrated for stacked vertical layout
    const counsellorPage = ref(0)
    const callerPage = ref(0)
    const PAGE_SIZE = 10 // Increased for better TV density

    const counsellorTotalPages = computed(() => Math.ceil((counsellorsWithQueueData.value?.length || 0) / PAGE_SIZE))
    const callerTotalPages = computed(() => Math.ceil((callersData.value?.length || 0) / PAGE_SIZE))

    const paginatedCounsellors = computed(() => {
      const start = counsellorPage.value * PAGE_SIZE
      return counsellorsWithQueueData.value.slice(start, start + PAGE_SIZE)
    })

    const paginatedCallers = computed(() => {
      const start = callerPage.value * PAGE_SIZE
      return callersData.value.slice(start, start + PAGE_SIZE)
    })

    // Cycle pages every 10 seconds
    const startPagination = () => {
      return setInterval(() => {
        if (counsellorTotalPages.value > 1) {
          counsellorPage.value = (counsellorPage.value + 1) % counsellorTotalPages.value
        }
        if (callerTotalPages.value > 1) {
          callerPage.value = (callerPage.value + 1) % callerTotalPages.value
        }
      }, 8000) // Faster cycle for TV engagement
    }

    // Simulated Load Factors (since specific vector data is often sparse)
    const voiceLoadValue = computed(() => {
      const total = onlineCallersCount.value + onCallCounsellorsCount.value
      if (total === 0) return 0
      return Math.min(Math.round((total / 20) * 100), 100)
    })

    const waLoadValue = computed(() => {
      return Math.min(Math.round((onlineCallersCount.value / 10) * 100), 100)
    })

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

    const handleReconnect = () => {
      console.log('Manual reconnect requested')
      disconnect()
      setTimeout(() => {
        connect(channels, fetchCounsellorName, fetchCounsellorStats)
      }, 500)
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
      fetchAgentPresence()
      
      // Refresh data intervals
      const dataInterval = setInterval(() => {
        fetchCasesData()
        fetchCallsReportData()
      }, 300000)

      const presenceInterval = setInterval(fetchAgentPresence, 30000)
      const pageInterval = startPagination()
      
      onBeforeUnmount(() => {
        clearInterval(dataInterval)
        clearInterval(presenceInterval)
        clearInterval(pageInterval)
        disconnect()
      })
    })

    // Watch merged channels to trigger metadata fetching for any new extensions (Polled or WS)
    watch(mergedChannels, (newChannels) => {
      newChannels.forEach(ch => {
        const context = (ch.CHAN_CONTEXT || '').toLowerCase()
        const extension = ch.CHAN_EXTEN
        
        const isAgent = context === 'agentlogin' || 
                        context === 'from-internal' || 
                        (extension && /^\d{3,4}$/.test(extension))
                        
        if (isAgent && extension && extension !== '--') {
          fetchCounsellorName(extension)
          fetchCounsellorStats(extension)
        }
      })
    }, { deep: true })

    // Keep DOM class in sync
    watch(isDarkMode, applyThemeClass)

    return {
      // State
      isDarkMode,
      
      // Data
      casesTiles,
      counsellorsWithQueueData,
      onlineCounsellorsCount,
      onlineCallersCount,
      callsReportError,
      callsReportLoading,
      callersData,
      onCallCounsellorsCount,
      availableAgentsCount,
      longestWaitSeconds,
      callsCardsMapped,
      serviceLevelValue,
      voiceLoadValue,
      waLoadValue,
      
      // Connection status
      connectionClass,
      connectionLabel,
      lastUpdate,
      
      // Axios instance for child components
      axiosInstance,
      
      // Paginated Data
      paginatedCounsellors,
      paginatedCallers,
      counsellorPage,
      callerPage,
      counsellorTotalPages,
      callerTotalPages,
      
      // Methods
      toggleDarkMode,
      handleReconnect
    }
  }
}
</script>

<style>
/* TV-Optimized Global Styles */
.container {
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 0; 
  background-color: var(--light-bg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

.pagination-indicator {
  font-size: 0.7rem;
  font-weight: 800;
  text-align: right;
  color: var(--text-secondary);
  padding: 4px 12px;
  background: var(--card-bg);
  border-radius: 10px;
  margin-top: 4px;
  align-self: flex-end;
  border: 1px solid var(--border-color);
}

.dark-mode .container {
  color: var(--text-primary);
}

/* Header - TV optimized */
.container > :first-child {
  flex-shrink: 0;
}

/* Operational KPIs - TV optimized */
.container > :nth-child(2) {
  flex-shrink: 0;
  margin-bottom: 6px;
}

/* Main Broadcast Body - 3 Column Command Center */
.dashboard-body {
  display: grid;
  grid-template-columns: 1.2fr 1fr 0.8fr; /* 1/3rd tables, central graph, sidebar tiles */
  gap: var(--spacing-sm);
  flex: 1;
  min-height: 0;
  margin: 0 10px 10px 10px;
}

.column {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  min-height: 0;
}

.situational-tables {
  min-width: 0;
}

.table-v-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.activity-trends {
  background: var(--card-bg);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  padding: 10px;
}

.performance-sidebar {
  min-width: 0;
}

.operational-kpis {
  flex-shrink: 0;
  margin: 0 10px 10px 10px;
}

@media screen and (min-width: 1920px) {
  .dashboard-body {
    grid-template-columns: 1fr 1fr 1fr; /* True 1/3rd split on 1080p+ */
    gap: var(--spacing-md);
  }
}

/* Disable movements for extreme performance/passive display */
@media (prefers-reduced-motion: reduce) {
  .container * {
    animation: none !important;
    transition: none !important;
  }
}
</style>
<template>
  <div class="container" :class="{ 'dark-mode': isDarkMode }">
    <WallboardHeader 
      :is-dark-mode="isDarkMode" 
      @toggle-theme="toggleDarkMode" 
      :connection-status="connectionClass"
      :connection-label="connectionLabel"
      :last-update="lastUpdate"
      @reconnect="handleReconnect"
    />

    <div class="dashboard-body">
      <!-- Tier 1: Top KPIs (4 Cards) -->
      <div class="stats-overview">
        <TopStatsRow 
          :calls-in-queue="inQueueBadgeCount"
          :longest-wait-seconds="longestWaitSeconds"
          :active-calls="onCallCounsellorsCount"
          :available-agents="availableAgentsCount"
        />
      </div>

      <!-- Tier 2: Call Status Distribution (8 Cards) -->
      <div class="status-cards-row">
        <CallsStatusCards :cards="callsCardsMapped" />
      </div>

      <!-- Tier 3: Main Strategic Area (Split View) -->
      <div class="main-grid-layout">
        
        <!-- Column 1: Workforce & Waiting Queue -->
        <div class="grid-column tables-col">
          <div class="widget-container">
            <div class="widget-header">
              <h2 class="widget-title">Counsellors Online</h2>
              <div class="badge">{{ onlineCounsellorsCount }} ACTIVE</div>
            </div>
            <CounsellorsTable :counsellors="paginatedCounsellors" />
          </div>

          <div class="widget-container">
            <div class="widget-header">
              <h2 class="widget-title">Calls in Queue</h2>
              <div class="badge badge-danger">{{ inQueueBadgeCount }} TOTAL</div>
            </div>
            <CallersTable :callers="callersData" />
          </div>
        </div>

        <!-- Column 2: Performance Analytics (Today) -->
        <div class="grid-column center-col">
          <div class="widget-container full-height">
            <div class="widget-header">
              <h2 class="widget-title">QUEUE ACTIVITY - TODAY</h2>
            </div>
            <QueueActivityGraph :axios-instance="axiosInstance" />
          </div>
        </div>

        <!-- Column 3: Volume & Historical Stats -->
        <div class="grid-column tiles-col">
          <!-- Channel Load (SIP vs WA) -->
          <div class="widget-container">
            <div class="widget-header">
              <h2 class="widget-title">CHANNEL LOAD</h2>
            </div>
            <div class="load-card-professional">
              <div class="load-body">
                <div class="load-item">
                  <div class="load-info">
                    <span class="load-label">Voice / SIP</span>
                    <span class="load-percent">{{ voiceLoadValue }}%</span>
                  </div>
                  <div class="progress-track"><div class="progress-fill voice" :style="{ width: voiceLoadValue + '%' }"></div></div>
                </div>
                <div class="load-item">
                    <div class="load-info">
                      <span class="load-label">WhatsApp</span>
                      <span class="load-percent">{{ waLoadValue }}%</span>
                    </div>
                    <div class="progress-track"><div class="progress-fill wa" :style="{ width: waLoadValue + '%' }"></div></div>
                </div>
              </div>
            </div>
          </div>

          <!-- 6 Case Analytics Tiles -->
          <CasesTiles :tiles="casesTiles" />
        </div>
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
import { formatDuration, getStatusText, getDurationSeconds, formatNumberWithCommas, formatCompactNumber } from './utils/formatters'
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
    TopStatsRow,
    CallsStatusCards,
    CounsellorsTable,
    CallersTable,
    QueueActivityGraph,
    CasesTiles
  },
  setup() {
    const isDarkMode = ref(false)
    
    // WebSockets (Near Real-time)
    const {
      channels,
      wsReady,
      lastUpdate,
      connect,
      disconnect
    } = useWebSocketConnection(WSHOST)
    
    const {
      apiData,
      callsReportData,
      fetchCasesData,
      fetchCallsReportData
    } = useApiData(axiosInstance)
    
    const {
      counsellorNames,
      counsellorStats,
      fetchCounsellorName,
      fetchCounsellorStats
    } = useCounsellorData(axiosInstance)

    const {
      agentPresenceChannels,
      fetchAgentPresence
    } = useAgentPresence()

    // --- OPERATIONAL METRICS (Decision Support & Historical) ---
    
    const getStatusTotal = (resp, statusKey) => {
      if (!resp) return 0
      
      // Support for multiple aliases (e.g. 'dump' OR 'hangup' OR 'disconnect')
      const keys = Array.isArray(statusKey) ? statusKey.map(k => k.toLowerCase()) : [statusKey.toLowerCase()]
      let total = 0

      // Priority 1: Aggregate from 'calls' array (Time-series/Stacked data)
      // Format: ["status", "time_bucket", "count"]
      if (resp.calls && Array.isArray(resp.calls)) {
        resp.calls.forEach(item => {
           if (Array.isArray(item) && item.length >= 3) {
             const status = String(item[0]).toLowerCase()
             if (keys.includes(status)) {
               total += (parseInt(item[2]) || 0)
             }
           }
        })
        // If we found data in the array, return the calculated total
        if (total > 0) return total
      }
      
      // Priority 2: Check 'calls_fmt' (Legacy Summary format)
      const fmt = resp.calls_fmt || []
      const found = fmt.find(f => {
        if (!Array.isArray(f) || f.length < 2) return false
        const itemStatus = String(f[0]).toLowerCase()
        return keys.some(k => itemStatus.includes(k))
      })
      if (found) return parseInt(found[1])
      
      // Priority 3: Direct key check in response object
      for (const k of keys) {
        if (resp[k]) return parseInt(resp[k])
      }
      
      return 0
    }

    const serviceLevelValue = computed(() => {
      const resp = callsReportData.value
      if (!resp) return 0
      const answered = getStatusTotal(resp, 'answered')
      const total = getStatusTotal(resp, 'total') || 1
      return Math.round((answered / total) * 100)
    })

    const abandonedTodayValue = computed(() => {
      return getStatusTotal(callsReportData.value, 'abandoned')
    })

    const answeredTodayValue = computed(() => {
      return getStatusTotal(callsReportData.value, 'answered')
    })

    const hangupTodayValue = computed(() => {
      return getStatusTotal(callsReportData.value, ['hangup', 'dump', 'disconnect'])
    })

    // Cases data from apiData (Historical Statistics)
    const casesTodayValue = computed(() => {
      const stats = apiData.value?.stats || apiData.value || {}
      return stats.cases_today || stats.cases_created_today || 0
    })

    const abandonedRecentValue = computed(() => {
      return abandonedTodayValue.value > 12 ? 3 : (abandonedTodayValue.value > 5 ? 1 : 0)
    })

    const getSLColor = (sl) => {
      if (sl < 80) return '#C0392B' // Red
      if (sl < 90) return '#D35400' // Orange
      return '#0E7337' // Green
    }

    // --- RESTORED FOR IMAGE MATCHING ---
    const casesTiles = computed(() => {
      const stats = apiData.value?.stats || apiData.value || {}
      return [
        { 
          id: 'ct1', 
          label: "TODAY'S ANSWERED CALLS", 
          value: formatCompactNumber(answeredTodayValue.value), 
          variant: 'c-blue',
          icon: 'phone'
        },
        { 
          id: 'ct2', 
          label: "TODAY'S CASES", 
          value: formatCompactNumber(casesTodayValue.value), 
          variant: 'c-amber' 
        },
        { 
          id: 'ct3', 
          label: 'ONGOING CASES', 
          value: formatCompactNumber(stats.cases_ongoing_total || 0), 
          variant: 'c-red' 
        },
        { 
          id: 'ct4', 
          label: 'MONTH CLOSED CASES', 
          value: formatCompactNumber(stats.cases_closed_this_month || 0), 
          variant: 'c-green' 
        },
        { 
          id: 'ct5', 
          label: 'TOTAL CALLS', 
          value: formatCompactNumber(stats.calls_total || 0), 
          variant: 'c-black' 
        },
        { 
          id: 'ct6', 
          label: 'TOTAL CASES', 
          value: formatCompactNumber(stats.cases_total || 0), 
          variant: 'c-black' 
        }
      ]
    })

    const callsCardsMapped = computed(() => {
      const resp = callsReportData.value || {}
      
      // Define mapping with aliases where needed
      const keywordsMapping = [
        { key: 'abandoned', label: 'ABANDONED' },
        { key: 'answered', label: 'ANSWERED' },
        { key: ['dump', 'hangup', 'disconnect'], label: 'HANGUP' }, // Use HANGUP as the label but support DUMP data
        { key: 'ivr', label: 'IVR' },
        { key: 'missed', label: 'MISSED' },
        { key: 'noanswer', label: 'NO ANSWER' },
        { key: 'voicemail', label: 'VOICEMAIL' }
      ]
      
      const cards = keywordsMapping.map((item) => {
        const val = getStatusTotal(resp, item.key)
        const displayKey = Array.isArray(item.key) ? item.key[0] : item.key
        return {
          id: `card-${displayKey}`,
          status: item.label,
          count: val,
          label: item.label,
          color: getHexColorForStatus(displayKey)
        }
      })

      return cards
    })

    const getHexColorForStatus = (status) => {
      const colors = {
        abandoned: '#D35400',
        answered: '#0E7337',
        dump: '#991B1B',
        ivr: '#1D3E8A',
        missed: '#C0392B',
        noanswer: '#E11D48',
        voicemail: '#10B981'
      }
      return colors[status.toLowerCase()] || '#6B7280'
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
      
      // Log reporting data to see where summary stats are
      if (apiData.value) console.log('Current apiData (KPIs):', apiData.value)
      if (callsReportData.value) {
        console.log('Current callsReportData (Cards) FULL:', JSON.stringify(callsReportData.value, null, 2))
      }
      
      if (result.length > 0) {
        console.log('Sample Channel Data:', JSON.stringify(result[0], null, 2))
      }
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
      const allCounsellorChannelsMap = new Map()

      // 1. Process all merged channels (WS + Poll)
      mergedChannels.value.forEach(ch => {
        const context = (ch.CHAN_CONTEXT || '').toLowerCase()
        const extension = ch.CHAN_EXTEN
        const callerId = ch.CHAN_CALLERID_NUM || ''
        const channelName = (ch.CHAN_CHAN || '').toLowerCase()
        
        // Identify Agents: Look for agent contexts, SIP extensions, or short internal IDs
        const isAgentContext = context === 'agentlogin' || context === 'from-internal' || context.includes('macro-dial')
        const isAgentSIP = channelName.includes('sip/1') || channelName.includes('pjsip/1') || channelName.includes('pjsip/2') || channelName.includes('pjsip/8')
        const isShortExt = extension && extension.length <= 4 && extension !== 's' && extension !== '--'
        
        const isAgent = isAgentContext || isAgentSIP || isShortExt
        
        if (isAgent) {
          // The "Lookup Extension" is what we use for names/stats
          // If extension is 's', it's likely a macro-dial start; use callerId if it's the agent's extension
          const lookupExt = (extension && extension !== 's' && extension !== '--') 
            ? extension 
            : (callerId.length <= 4 && callerId !== '' ? callerId : extension)

          if (lookupExt && lookupExt !== '--') {
            allCounsellorChannelsMap.set(lookupExt, { ...ch, _lookupExt: lookupExt })
          }
        }
      })

      return Array.from(allCounsellorChannelsMap.values()).map((ch) => {
        const extension = ch.CHAN_EXTEN || '--'
        const lookupExt = ch._lookupExt || extension
        
        // Resolution: Try reactive cache -> CallerID Name -> Fallback
        let name = counsellorNames[lookupExt]
        if (!name || name === 'Unknown') {
          name = ch.CHAN_CALLERID_NAME && ch.CHAN_CALLERID_NAME !== '--' ? ch.CHAN_CALLERID_NAME : ('Agent ' + lookupExt)
        }
        
        const stats = counsellorStats[lookupExt] || { answered: '0', missed: '0', talkTime: '0:00' }
        const connectedCallerNumber = Number(ch.CHAN_STATE_CONNECT) ? findConnectedCaller(ch.CHAN_BRIDGE_ID) : '--'

        return {
          id: ch.CHAN_UNIQUEID || ch._uid,
          extension: extension, // We still display the raw extension column
          lookupExt: lookupExt, // Internal reference
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
          channel: ch.CHAN_CHAN || '--'
        }
      })
    })

    // Unified Caller List (Strict Inbound Filtering)
    const allCallers = computed(() => {
      return mergedChannels.value
        .filter(ch => {
          const extension = ch.CHAN_EXTEN
          const callerId = ch.CHAN_CALLERID_NUM || ''
          const channelName = (ch.CHAN_CHAN || '').toLowerCase()
          
          // 1. Identify Agents (Internal Legs)
          // Agents usually have 3-4 digit extensions. Exclude them from the "Callers" list.
          const isShortCallerId = callerId.length >= 1 && callerId.length <= 4
          const isAgentSIP = channelName.includes('sip/1') || channelName.includes('pjsip/1') || channelName.includes('pjsip/2') || channelName.includes('pjsip/8')
          
          // 2. Identify Inbound (External Legs)
          const isPSTN = callerId.length >= 7 || callerId.startsWith('+')
          const isInQueue = Number(ch.CHAN_STATE_QUEUE) === 1 || (ch.CHAN_VECTOR && ch.CHAN_VECTOR !== '--')
          
          // STRICTURE: If it looks like an internal extension (3-4 digits), it is NOT an external caller
          if (isShortCallerId || isAgentSIP) return false
          
          // To be a valid inbound caller, it must be PSTN OR explicitly in a queue state
          return isPSTN || isInQueue
        })
        .map((ch) => {
          const queueStatus = getStatusText(ch)
          const agentExt = (queueStatus === 'On Call' || queueStatus === 'Connected') ? findConnectedAgentByBridge(ch.CHAN_BRIDGE_ID) : '--'
          return {
            id: ch.CHAN_UNIQUEID || ch._uid || `caller-${Math.random()}`,
            callerNumber: ch.CHAN_CALLERID_NUM || '--',
            vector: ch.CHAN_VECTOR || '--',
            waitTime: formatDuration(ch.CHAN_TS),
            queueStatus: queueStatus,
            bridgeId: ch.CHAN_BRIDGE_ID || '--',
            channelName: ch.CHAN_CHAN || '',
            agentExtension: agentExt,
            agentName: agentExt !== '--' ? (counsellorNames[agentExt] || 'Agent ' + agentExt) : '--',
            channelData: ch
          }
        })
    })

    // Helper: Find which agent is connected to this bridge
    const findConnectedAgentByBridge = (bridgeId) => {
      if (!bridgeId || bridgeId === '--') return '--'
      const agent = mergedChannels.value.find(ch => {
        const extension = ch.CHAN_EXTEN
        const isAgent = extension && extension !== '--' && extension.length <= 4
        return isAgent && ch.CHAN_BRIDGE_ID === bridgeId
      })
      return agent ? agent.CHAN_EXTEN : '--'
    }

    // Callers data for the "Calls in Queue" table - Only active waiting calls (Inbound)
    const callersData = computed(() => {
      return allCallers.value.filter(c => {
        const status = c.queueStatus
        // ONLY Inbound waiting/processing legs should appear in the queue list
        return status === 'In Queue' || status === 'IVR'
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
    
    // Unified count for the red badge: ONLY counts Inbound Waiting (In Queue + IVR)
    const inQueueBadgeCount = computed(() => {
      return callersData.value.length
    })

    // Sub-count: Only those explicitly waiting in the queue (for the n of m display)
    const actualQueuedCount = computed(() => {
      return allCallers.value.filter(c => c.queueStatus === 'In Queue').length
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

    // --- PAGINATION & REFRESH ---

    const counsellorPage = ref(0)
    const PAGE_SIZE = 12
    const paginatedCounsellors = computed(() => {
      const start = counsellorPage.value * PAGE_SIZE
      return counsellorsWithQueueData.value.slice(start, start + PAGE_SIZE)
    })

    const toggleDarkMode = () => {
      isDarkMode.value = !isDarkMode.value
      document.documentElement.classList.toggle('dark-mode', isDarkMode.value)
    }

    const handleReconnect = () => {
      disconnect()
      setTimeout(() => connect(channels, fetchCounsellorName, fetchCounsellorStats), 500)
    }

    onMounted(() => {
      // Dynamic Branding from Env
      const brandPrimary = import.meta.env.VITE_BRAND_COLOR_PRIMARY
      if (brandPrimary) {
        document.documentElement.style.setProperty('--primary-color', brandPrimary)
        document.documentElement.style.setProperty('--info-color', brandPrimary)
        document.documentElement.style.setProperty('--text-main', brandPrimary)
      }
      
      const brandSecondary = import.meta.env.VITE_BRAND_COLOR_SECONDARY
      if (brandSecondary) {
        document.documentElement.style.setProperty('--secondary-color', brandSecondary)
      }

      connect(channels, fetchCounsellorName, fetchCounsellorStats)
      fetchCasesData()
      fetchCallsReportData()
      fetchAgentPresence()
      
      // Near Real-time Decision Metrics (10s)
      const refreshInterval = setInterval(() => {
        fetchCasesData()
        fetchCallsReportData()
        fetchAgentPresence()
      }, 10000)

      const pageCycle = setInterval(() => {
        const total = Math.ceil(counsellorsWithQueueData.value.length / PAGE_SIZE)
        if (total > 1) counsellorPage.value = (counsellorPage.value + 1) % total
      }, 8000)

      onBeforeUnmount(() => {
        clearInterval(refreshInterval)
        clearInterval(pageCycle)
        disconnect()
      })
    })

    // --- RE-ENABLING NAME RESOLUTION WATCH ---
    watch(mergedChannels, (newChannels) => {
      newChannels.forEach(ch => {
        const extension = ch.CHAN_EXTEN
        const callerId = ch.CHAN_CALLERID_NUM || ''
        const lookupExt = (extension && extension !== 's' && extension !== '--') 
          ? extension 
          : (callerId.length <= 4 && callerId !== '' ? callerId : null)

        if (lookupExt) {
          fetchCounsellorName(lookupExt)
          fetchCounsellorStats(lookupExt)
        }
      })
    }, { immediate: true })

    return {
      isDarkMode, inQueueBadgeCount, longestWaitSeconds, onCallCounsellorsCount, availableAgentsCount,
      serviceLevelValue, abandonedTodayValue, abandonedRecentValue, onlineCounsellorsCount,
      answeredTodayValue, hangupTodayValue, casesTodayValue,
      casesTiles, callsCardsMapped, callersData,
      paginatedCounsellors, lastUpdate, connectionClass: computed(() => wsReady.value === 'open' ? 'on' : 'off'),
      connectionLabel: computed(() => wsReady.value === 'open' ? 'Live' : 'Offline'),
      axiosInstance, toggleDarkMode, handleReconnect, getSLColor,
      voiceLoadValue: computed(() => Math.min(Math.round((inQueueBadgeCount.value / 10) * 100), 100)),
      waLoadValue: computed(() => 25)
    }
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

:root {
  --primary-color: #1D3E8A;
  --secondary-color: #D35400;
  --success-color: #0E7337;
  --danger-color: #C0392B;
  --warning-color: #B95E06;
  --info-color: #1D3E8A;
  --bg-color: #E8F0FA;
  --card-bg: #ffffff;
  --text-main: #1D3E8A;
  --text-muted: #4A4A4A;
  --border-color: #dee2e6;
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --border-radius-sm: 8px;
  --border-radius-md: 12px;
  --border-radius-lg: 20px;
  --shadow-sm: 0 4px 6px rgba(29, 62, 138, 0.05);
  --shadow-md: 0 10px 15px rgba(29, 62, 138, 0.1);
}

body {
  margin: 0;
  background-color: var(--bg-color);
  color: var(--text-main);
  font-family: 'Outfit', system-ui, -apple-system, sans-serif;
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
}

* {
  box-sizing: border-box;
}

/* Main Dashboard Container - Full Viewport Lock */
.container {
  width: 100vw;
  height: 100vh;
  margin: 0;
  padding: 1vh 1vw;
  background-color: var(--bg-color);
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden; 
  transition: background-color 0.3s ease;
}

.dashboard-body {
  flex: 1;
  padding: 0 var(--spacing-sm) var(--spacing-sm) var(--spacing-sm); /* Reduced padding top */
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm); /* Tighter gap */
  min-height: 0; /* Critical for nested scrolling/flex */
  overflow: hidden;
}

/* TOP KPI SECTION */
.stats-overview {
  width: 100%;
}

.status-cards-row {
  width: 100%;
}

.cards-and-load {
  display: grid;
  grid-template-columns: 1fr 280px;
  gap: var(--spacing-md);
  align-items: start;
}

/* CHANNEL LOAD WIDGET */
.channel-load-section {
  height: 100%;
}

.load-card {
  background: white;
  border-radius: var(--border-radius-md);
  padding: 12px 16px;
  box-shadow: var(--shadow-sm);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.load-header {
  margin-bottom: 12px;
}

.load-title {
  font-size: 0.75rem;
  font-weight: 800;
  color: #64748b;
  letter-spacing: 0.05em;
}

.load-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.load-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.load-info {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  font-weight: 700;
  color: #1e293b;
}

.progress-track {
  height: 6px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.8s ease;
}

.progress-fill.voice { background: #3b82f6; }
.progress-fill.wa { background: #10b981; }

.status-cards-row {
  width: 100%;
  margin-bottom: var(--spacing-sm);
}

/* ZONE 3: MAIN GRID LAYOUT (Strict 3-Column Match) */
.main-grid-layout {
  display: grid;
  grid-template-columns: 32% 43% 1fr;
  gap: var(--spacing-md);
  flex: 1;
  min-height: 0;
}

.grid-column {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  min-height: 0;
}

.tables-col {
  /* Tables column stacks items vertically */
  overflow: hidden;
}

.tables-col .widget-container {
  flex: 1; /* Both tables share 50/50 space usually */
  min-height: 0;
}

.center-col {
  /* Graph column occupies the middle */
}

.tiles-col {
  /* Tiles column on the far right */
}

.load-card-professional {
  padding: 16px;
}

.load-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.load-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
}

.load-label { font-weight: 800; font-size: 0.85rem; }
.load-percent { font-weight: 900; color: var(--primary-color); }

@media (max-width: 1440px) {
  .main-grid-layout {
    grid-template-columns: 1fr;
    height: auto;
    overflow-y: auto;
  }
}

/* WIDGET CONTAINER */
.widget-container {
  background: white;
  border-radius: var(--border-radius-lg);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.widget-container.full-height { flex: 1; }

.widget-header {
  padding: 10px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #f1f5f9;
}

.widget-title {
  font-size: 1rem;
  font-weight: 900;
  margin: 0;
  color: #111827;
  text-transform: uppercase;
}

.badge {
  background: var(--primary-color);
  color: white;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 800;
}

.badge-danger { background: var(--danger-color); }

/* DARK MODE */
.dark-mode .widget-container,
.dark-mode .load-card-professional {
  background: #1e293b;
  color: white;
}
.dark-mode .widget-title { color: white; }
.dark-mode .widget-header { border-bottom-color: #334155; }
.dark-mode .load-percent { color: #f8fafc; }

@media (min-width: 1024px) {
  .container {
    height: 100vh;
    overflow: hidden;
  }
}
</style>
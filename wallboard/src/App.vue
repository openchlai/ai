<template>
  <div class="container" :class="{ 'dark-mode': isDarkMode }">
    <!-- Header -->
    <div class="header">
      <div class="title-section">
        <h1>Sauti Helpline Wallboard</h1>
        <p>Real-time counselling and support</p>
      </div>
      <div class="header-controls">
        <div class="connection-status">
          <span :class="['dot', connectionClass]"></span>
          <span class="status-text">{{ connectionLabel }}</span>
          <small v-if="lastUpdate"> · last update: {{ lastUpdate }}</small>
        </div>
        <button class="theme-toggle" @click="toggleDarkMode" :title="isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'">
          <span class="theme-icon">{{ isDarkMode ? '☀️' : '🌙' }}</span>
        </button>
      </div>
    </div>

    <!-- Cases Grid Row (Using mock data for now) -->
    <div class="cases-grid">
      <div 
        v-for="item in casesTiles" 
        :key="item.id" 
        :class="['case-card', item.variant]"
      >
        <div class="case-inner">
          <div v-if="item.value" class="case-value">{{ item.value }}</div>
          <div class="case-label">{{ item.label }}</div>
        </div>
      </div>
    </div>

    <!-- Top Statistics Row - NOW WITH REAL QUEUE DATA -->
    <div class="top-stats-row">
      <div 
        v-for="stat in stats" 
        :key="stat.id" 
        :class="['stat-card', stat.variant]"
      >
        <div class="stat-content">
          <div class="stat-label">{{ stat.title.toUpperCase() }}</div>
          <div class="stat-value">{{ stat.value }}</div>
        </div>
      </div>
    </div>

    <!-- Counsellors Section - NOW WITH REAL QUEUE DATA -->
    <div class="counsellors-section">
      <div class="section-header">
        <h2 class="section-title">Counsellors Online: {{ onlineCounsellorsCount }}</h2>
        <div class="filter-buttons">
         
        </div>
      </div>
      <div class="counsellors-table">
        <div class="table-header">
          <div class="col-ext">Ext.</div>
          <div class="col-name">Name</div>
          <div class="col-caller">Caller</div>
          <div class="col-answered">Answered</div>
          <div class="col-missed">Missed</div>
          <div class="col-talk-time">Talk Time</div>
          <div class="col-queue-status">Queue Status</div>
          <div class="col-duration">Duration</div>
        </div>
        <div class="table-body">
          <div v-if="counsellorsWithQueueData.length === 0" class="no-counsellors-row">
            <div class="no-counsellors-text">No counsellors currently online</div>
          </div>
          <div 
            v-for="counsellor in counsellorsWithQueueData" 
            :key="counsellor.id"
            class="table-row"
          >
            <div class="col-ext">{{ counsellor.extension }}</div>
            <div class="col-name">{{ counsellor.name }}</div>
            <div class="col-caller">{{ counsellor.caller || '--' }}</div>
            <div class="col-answered">{{ counsellor.answered || '0' }}</div>
            <div class="col-missed">{{ counsellor.missed || '0' }}</div>
            <div class="col-talk-time">{{ counsellor.talkTime || '--' }}</div>
            <div :class="['col-queue-status', statusClass(counsellor.queueStatus)]">
              {{ counsellor.queueStatus || 'Offline' }}
            </div>
            <div class="col-duration">{{ counsellor.duration || '--' }}</div>
          </div>
        </div>
      </div>
    </div>
    <!-- Callers Section -->
    <div class="counsellors-section">
      <div class="section-header">
        <h2 class="section-title">Callers Online: {{ onlineCallersCount }}</h2>
      </div>
      <div class="counsellors-table">
        <div class="table-header callers-header">
          <div class="col-caller-num">Caller Number</div>
          <div class="col-caller-name">Caller Name</div>
          <div class="col-vector">Queue</div>
          <div class="col-wait-time">Wait Time</div>
          <div class="col-status">Status</div>
          <div class="col-bridge">Bridge ID</div>
        </div>
        <div class="table-body">
          <div v-if="callersData.length === 0" class="no-counsellors-row">
            <div class="no-counsellors-text">No callers currently online</div>
          </div>
          <div 
            v-for="caller in callersData" 
            :key="caller.id"
            class="table-row callers-row"
          >
            <div class="col-caller-num">{{ caller.callerNumber || '--' }}</div>
            <div class="col-caller-name">{{ caller.callerName || 'Unknown' }}</div>
            <div class="col-vector">{{ caller.vector || '--' }}</div>
            <div class="col-wait-time">{{ caller.waitTime || '--' }}</div>
            <div :class="['col-status', statusClass(caller.queueStatus)]">
              {{ caller.queueStatus || 'Unknown' }}
            </div>
            <div class="col-bridge">{{ caller.bridgeId || '--' }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.callers-header,
.callers-row {
  display: grid !important;
  grid-template-columns: 180px 200px 120px 120px 140px 1fr !important;
  gap: 15px !important;
}

.callers-header > div,
.callers-row > div {
  padding: 8px 12px !important;
}
</style>

<script>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'

const WSHOST = 'wss://demo-openchs.bitz-itc.com:8384/ami/sync?c=-2&'

export default {
  name: 'App',
  setup() {
    const isDarkMode = ref(false)
    const activeFilter = ref('all')
    
    // WebSocket and queue data state
    const ws = ref(null)
    const wsReady = ref('closed')
    const channels = ref([])
    const lastUpdate = ref(null)
    const reconnectAttempt = ref(0)
    // API data state
    const reconnectTimer = ref(null)
    
    // API data state
    const apiData = ref(null)
    const apiError = ref(null)
    const apiLoading = ref(false)

    // API call function with CORS error handling
    const fetchCasesData = async () => {
      apiLoading.value = true
      apiError.value = null
      
      try {
        const response = await fetch('https://demo-openchs.bitz-itc.com/helpline/api/wallonly/rpt?&type=bar&stacked=stacked&xaxis=hangup_status_txt&yaxis=-&vector=1&rpt=call_count&metrics=call_count&', {
          mode: 'cors',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          }
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        console.log('Cases API Response:', data)
        apiData.value = data
      } catch (error) {
        console.error('Error fetching cases data (likely CORS):', error)
        apiError.value = error.message
        
        // Use fallback mock data when CORS blocks the request
        console.log('Using fallback mock data due to CORS error')
        apiData.value = {
          stats: {
            cases_today: "1",
            cases_closed_this_month: "5", 
            cases_ongoing_total: "250",
            cases_total: "255",
            calls_today: "12",
            calls_total: "465"
          }
        }
      } finally {
        apiLoading.value = false
      }
    }



    // Cases tiles with real data from API
    const casesTiles = computed(() => {
      const stats = apiData.value?.stats || {}
      
      return [
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
    })

    // Filters with added 'online' filter
    const filters = ref([
      { id: 'all', label: 'All' },
      { id: 'online', label: 'Online' },
      { id: 'on_call', label: 'On Call' },
      { id: 'in_queue', label: 'In Queue' },
      { id: 'available', label: 'Available' },
      { id: 'ringing', label: 'Ringing' }
    ])

    // WebSocket connection functions
    const handleMessage = (payload) => {
      console.log('=== WebSocket Data Received ===')
      console.log('Raw payload:', payload)
      
      lastUpdate.value = new Date().toLocaleString()
      
      let obj = payload
      if (typeof payload === 'string') {
        try {
          obj = JSON.parse(payload)
          console.log('Parsed JSON object:', obj)
        } catch (err) {
          console.error('[QueueMonitor] Failed to parse JSON payload', err)
          return
        }
      }

      // Handle both array and object keyed by channel IDs
      let chArr = []
      if (Array.isArray(obj.channels)) {
        console.log('Channels data is array format:', obj.channels)
        chArr = obj.channels
      } else if (obj.channels && typeof obj.channels === 'object') {
        console.log('Channels data is object format:', obj.channels)
        // Convert object to array with id + values
        chArr = Object.entries(obj.channels).map(([key, arr]) => {
          if (Array.isArray(arr)) {
            const mappedChannel = {
              _uid: key,
              CHAN_TS: arr[1] || Date.now(),
              CHAN_UNIQUEID: arr[2] || key,
              CHAN_CHAN: arr[3] || '',
              CHAN_CALLERID_NUM: arr[4] || '',
              CHAN_CALLERID_NAME: arr[5] || '',
              CHAN_CONTEXT: arr[6] || '',
              CHAN_EXTEN: arr[7] || '',
              CHAN_ACTION_ID: arr[8] || '',
              CHAN_STATE_UP: arr[13] || 0,
              CHAN_STATE_QUEUE: arr[14] || 0,
              CHAN_STATE_CONNECT: arr[15] || 0,
              CHAN_STATE_HANGUP: arr[16] || 0,
              CHAN_STATE_HOLD: arr[18] || 0,
              CHAN_CBO_TS: arr[20] || '',
              CHAN_CBO: arr[21] || '',
              CHAN_CBO_UNIQUEID: arr[22] || '',
              CHAN_CBO_CID: arr[23] || '',
              CHAN_XFER_TS: arr[24] || '',
              CHAN_XFER: arr[25] || '',
              CHAN_XFER_UNIQUEID: arr[26] || '',
              CHAN_XFER_CID: arr[27] || '',
              CHAN_ORIG: arr[36] || '',
              CHAN_CONTEXT_MASQ: arr[43] || '',
              CHAN_EXTEN_MASQ: arr[44] || '',
              CHAN_UNIQUEID_2: arr[45] || '',
              CHAN_CHAN_2: arr[46] || '',
              CHAN_CID_NUM_2: arr[47] || '',
              CHAN_SIPCALLID: arr[50] || '',
              CHAN_BRIDGE_ID: arr[51] || '',
              CHAN_CAMPAIGN_ID: arr[53] || '',
              CHAN_CAMPAIGN_WRAPUP: arr[54] || '',
              CHAN_PROMPT_TS0: arr[67] || '',
              CHAN_VECTOR: arr[74] || '',
              CHAN_EVENT: arr[76] || '',
              CHAN_EVENT_N: arr[77] || '',
              CHAN_SIPID_JS_: arr[80] || '',
              CHAN_STATUS_: arr[81] || '',
              CHAN_STATUS_TXT_: arr[82] || '',
              CHAN_STATUS_TS_: arr[83] || '',
              CHAN_STATUS_TS_TXT_: arr[84] || '',
              _raw: arr
            }
            console.log(`Mapped channel ${key}:`, mappedChannel)
            return mappedChannel
          }
          console.log(`Channel ${key} (object format):`, arr)
          return { _uid: key, ...arr }
        })
      } else {
        console.warn('[QueueMonitor] payload does not contain channels array/object', obj)
      }

      console.log('Final channels array:', chArr)
      console.log(`Total channels: ${chArr.length}`)
      console.log('=== End WebSocket Data ===')
      
      channels.value = chArr
    }

    const connect = () => {
      if (ws.value && wsReady.value === 'open') return
      wsReady.value = 'connecting'

      try {
        ws.value = new WebSocket(WSHOST)

        ws.value.onopen = () => {
          reconnectAttempt.value = 0
          wsReady.value = 'open'
          console.log('[QueueMonitor] WebSocket opened')
        }

        ws.value.onmessage = (ev) => {
          try {
            handleMessage(ev.data)
          } catch (err) {
            console.error('[QueueMonitor] error handling message', err)
          }
        }

        ws.value.onclose = (ev) => {
          console.warn('[QueueMonitor] WebSocket closed', ev.code, ev.reason)
          wsReady.value = 'closed'
          scheduleReconnect()
        }

        ws.value.onerror = (err) => {
          console.error('[QueueMonitor] WebSocket error', err)
          wsReady.value = 'error'
        }
      } catch (err) {
        console.error('[QueueMonitor] WebSocket connect failed', err)
        wsReady.value = 'error'
        scheduleReconnect()
      }
    }

    const scheduleReconnect = () => {
      if (reconnectTimer.value) return
      reconnectAttempt.value++
      const attempt = reconnectAttempt.value
      const backoff = Math.min(30000, 1000 * Math.pow(1.8, attempt))
      console.log(`[QueueMonitor] reconnect in ${Math.round(backoff)}ms (attempt ${attempt})`)
      reconnectTimer.value = setTimeout(() => {
        reconnectTimer.value = null
        connect()
      }, backoff)
    }

    const disconnect = () => {
      if (reconnectTimer.value) {
        clearTimeout(reconnectTimer.value)
        reconnectTimer.value = null
      }
      if (ws.value) {
        try { ws.value.close() } catch (e) { /* ignore */ }
        ws.value = null
      }
      wsReady.value = 'closed'
    }

    // Helper functions
    const getStatusText = (ch) => {
      if (ch.CHAN_STATUS_TXT_) return String(ch.CHAN_STATUS_TXT_)
      if (Number(ch.CHAN_STATE_HANGUP)) return 'Hangup'
      if (Number(ch.CHAN_STATE_CONNECT)) return 'On Call'
      if (Number(ch.CHAN_STATE_HOLD)) return 'On Hold'
      if (Number(ch.CHAN_STATE_QUEUE)) return 'In Queue'
      if (ch.CHAN_EVENT_N) return String(ch.CHAN_EVENT_N)
      return 'Available'
    }

    const formatDuration = (ts) => {
      if (!ts) return '--'
      const now = Date.now()
      const start = Number(ts) < 1e11 ? Number(ts) * 1000 : Number(ts)
      const diff = Math.max(0, now - start)
      const minutes = Math.floor(diff / 60000)
      const seconds = Math.floor((diff % 60000) / 1000)
      return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
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
      return channels.value
        .filter(ch => {
          const context = (ch.CHAN_CONTEXT || '').toLowerCase()
          console.log(`Channel ${ch.CHAN_UNIQUEID}: CONTEXT = "${ch.CHAN_CONTEXT}" (checking for agentlogin)`)
          return context === 'agentlogin'
        })
        .map((ch) => {
          return {
            id: ch.CHAN_UNIQUEID || ch._uid,
            extension: ch.CHAN_EXTEN || '--',
            name: ch.CHAN_CALLERID_NAME || 'Unknown',
            caller: ch.CHAN_CALLERID_NUM || '--',
            answered: '--', // Not available in current channel data
            missed: '--',   // Not available in current channel data
            talkTime: formatDuration(ch.CHAN_TS),
            queueStatus: getStatusText(ch),
            duration: Number(ch.CHAN_STATE_CONNECT) ? formatDuration(ch.CHAN_TS) : '--',
            isOnline: true,
            channelData: ch,
            // Additional data from backend
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
          console.log(`Channel ${ch.CHAN_UNIQUEID}: CONTEXT = "${ch.CHAN_CONTEXT}" (checking for DLPN_callcenter)`)
          return context === 'dlpn_callcenter'
        })
        .map((ch) => {
          return {
            id: ch.CHAN_UNIQUEID || ch._uid,
            callerNumber: ch.CHAN_CALLERID_NUM || '--',
            callerName: ch.CHAN_CALLERID_NAME || 'Unknown',
            vector: ch.CHAN_VECTOR || '--',
            waitTime: formatDuration(ch.CHAN_TS), // Time since call started
            queueStatus: getStatusText(ch),
            bridgeId: ch.CHAN_BRIDGE_ID || '--',
            campaign: ch.CHAN_CAMPAIGN_ID || '--',
            sipCallId: ch.CHAN_SIPCALLID || '--',
            isOnline: true,
            channelData: ch
          }
        })
    })

    // TOP STATISTICS - NOW WITH REAL QUEUE DATA
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

    // Filter callers based on active filter
    const filteredCallers = computed(() => {
      return callersData.value.filter(c => {
        const status = (c.queueStatus || '').toLowerCase()
        switch (activeFilter.value) {
          case 'online':
            return c.isOnline
          case 'on_call':
            return status.includes('on call') || status.includes('connect')
          case 'in_queue':
            return status.includes('queue')
          case 'available':
            return status.includes('available')
          case 'ringing':
            return status.includes('ring')
          default:
            return true
        }
      })
    })

    // Filter matching function
    const matchesFilter = (c) => {
      const status = (c.queueStatus || '').toString().toLowerCase()
      switch (activeFilter.value) {
        case 'online':
          return c.isOnline
        case 'on_call':
          return status.includes('on call')
        case 'in_queue':
          return status.includes('queue')
        case 'available':
          return status.includes('available')
        case 'ringing':
          return status.includes('ring')
        default:
          return true
      }
    }

    // Filtered counsellors
    const filteredCounsellors = computed(() => {
      return counsellorsWithQueueData.value.filter(matchesFilter)
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

    // Methods
    const setActiveFilter = (id) => {
      activeFilter.value = id
    }

    const statusClass = (status) => {
      const s = (status || 'Available').toString().toLowerCase()
      if (s.includes('on call')) return 'status-oncall'
      if (s.includes('ring')) return 'status-ringing'
      if (s.includes('queue')) return 'status-inqueue'
      if (s.includes('available')) return 'status-available'
      if (s.includes('offline')) return 'status-offline'
      return 'status-neutral'
    }

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
      connect()
      
      // Try to fetch cases data (will use fallback if CORS blocked)
      fetchCasesData()
      
      // Refresh cases data every 5 minutes instead of every minute to reduce CORS errors
      const casesInterval = setInterval(() => {
        fetchCasesData()
      }, 300000) // 5 minutes
      
      // Clean up on unmount
      onBeforeUnmount(() => {
        clearInterval(casesInterval)
      })
    })

    onBeforeUnmount(() => {
      disconnect()
    })

    // Keep DOM class in sync
    watch(isDarkMode, applyThemeClass)

    return {
      // State
      isDarkMode,
      activeFilter,
      wsReady,
      lastUpdate,
      
      // Data
      casesTiles,
      stats,
      filters,
      counsellorsWithQueueData,
      filteredCounsellors,
      onlineCounsellorsCount,
      
      // API data
      apiData,
      apiError,
      apiLoading,
      
      // Callers data
      callersData,
      filteredCallers,
      onlineCallersCount,
      
      // Connection status
      connectionClass,
      connectionLabel,
      
      // Methods
      setActiveFilter,
      statusClass,
      toggleDarkMode
    }
  }
}
</script>
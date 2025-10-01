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

    <!-- Cases Grid Row -->
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

    <!-- Calls Status Cards Section -->
    <div class="calls-cards-section">
      <div class="section-header">
        <h2 class="section-title">Today's Call Status</h2>
      </div>
      <div class="calls-cards-grid">
        <div v-if="callsReportLoading" class="loading-message">
          Loading call status data...
        </div>
        <div v-else-if="callsReportError" class="error-message">
          Error loading call status: {{ callsReportError }}
        </div>
        <div v-else-if="callsCards.length === 0" class="no-data-message">
          No call status data available
        </div>
        <div 
          v-else
          v-for="card in callsCards" 
          :key="card.id"
          :class="['call-status-card', `card-${card.variant}`]"
        >
          <div class="card-content">
            <div class="card-count">{{ card.count }}</div>
            <div class="card-label">{{ card.label }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Queue Activity Graph -->
    <QueueActivityGraph :axiosInstance="axiosInstance" />

    <!-- Top Statistics Row -->
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

    <!-- Counsellors Section -->
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
            <div class="col-name">
              <span v-if="counsellor.nameLoading" class="name-loading">Loading...</span>
              <span v-else>{{ counsellor.name }}</span>
            </div>
            <div class="col-caller">{{ counsellor.caller || '--' }}</div>
            <div class="col-answered">
              <span v-if="counsellor.statsLoading" class="name-loading">Loading...</span>
              <span v-else>{{ counsellor.answered || '0' }}</span>
            </div>
            <div class="col-missed">
              <span v-if="counsellor.statsLoading" class="name-loading">Loading...</span>
              <span v-else>{{ counsellor.missed || '0' }}</span>
            </div>
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
          <div class="col-vector">Queue</div>
          <div class="col-wait-time">Wait Time</div>
          <div class="col-status">Status</div>
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
            <div class="col-vector">{{ caller.vector || '--' }}</div>
            <div class="col-wait-time">{{ caller.waitTime || '--' }}</div>
            <div :class="['col-status', statusClass(caller.queueStatus)]">
              {{ caller.queueStatus || 'Unknown' }}
            </div>
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
  grid-template-columns: 180px 120px 120px 1fr !important;
  gap: 15px !important;
}

.callers-header > div,
.callers-row > div {
  padding: 8px 12px !important;
}

.name-loading {
  color: #888;
  font-style: italic;
}

/* Calls Cards Section Styles */
.calls-cards-section {
  margin: 20px 0;
}

.calls-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-top: 15px;
}

.call-status-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  transition: transform 0.2s ease;
}

.call-status-card:hover {
  transform: translateY(-2px);
}

.dark-mode .call-status-card {
  background: #2d3748;
}

.card-content {
  text-align: center;
}

.card-count {
  font-size: 2.5rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 8px;
}

.card-label {
  font-size: 0.9rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: 0.8;
}

/* Card variants */
.card-success .card-count {
  color: #10b981;
}

.card-warning .card-count {
  color: #f59e0b;
}

.card-danger .card-count {
  color: #ef4444;
}

.card-info .card-count {
  color: #3b82f6;
}

.card-primary .card-count {
  color: #8b5cf6;
}

.card-secondary .card-count {
  color: #6b7280;
}

.loading-message, .error-message, .no-data-message {
  grid-column: 1 / -1;
  text-align: center;
  padding: 20px;
  border-radius: 8px;
  background: #f8f9fa;
  color: #6c757d;
}

.error-message {
  background: #fee;
  color: #dc3545;
}

.dark-mode .loading-message,
.dark-mode .no-data-message {
  background: #374151;
  color: #9ca3af;
}

.dark-mode .error-message {
  background: #450a0a;
  color: #f87171;
}
</style>

<script>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { fetchCasesData as fetchFromApi } from "@/utils/axios.js"
import axiosInstance from "@/utils/axios.js"
import QueueActivityGraph from './components/QueueActivityGraph.vue'

const WSHOST = 'wss://192.168.10.120:8384/ami/sync?c=-2'

export default {
  name: 'App',
  components: {
    QueueActivityGraph
  },
  setup() {
    const isDarkMode = ref(false)
    const activeFilter = ref('all')
    
    // WebSocket and queue data state
    const ws = ref(null)
    const wsReady = ref('closed')
    const channels = ref([])
    const lastUpdate = ref(null)
    const reconnectAttempt = ref(0)
    const reconnectTimer = ref(null)
    
    // API data state
    const apiData = ref(null)
    const apiError = ref(null)
    const apiLoading = ref(false)
    
    // Calls report data state
    const callsReportData = ref(null)
    const callsReportError = ref(null)
    const callsReportLoading = ref(false)
    
    // Counsellor names state - using reactive refs for better reactivity
    const counsellorNames = ref({})
    const nameLoadingStates = ref({})
    
    // Counsellor stats state
    const counsellorStats = ref({})
    const statsLoadingStates = ref({})

    // Function to fetch counsellor stats by extension
    const fetchCounsellorStats = async (extension) => {
      console.log(`📊 STARTING fetchCounsellorStats for extension: ${extension}`)
      
      if (!extension || extension === '--') {
        console.log(`❌ Invalid extension for stats: ${extension}`)
        return
      }

      // Don't fetch if already loading
      if (statsLoadingStates.value[extension]) {
        console.log(`⏳ Extension ${extension} stats already loading, skipping...`)
        return
      }
      
      // Don't fetch if already cached
      if (counsellorStats.value[extension]) {
        console.log(`💾 Extension ${extension} stats already cached:`, counsellorStats.value[extension])
        return
      }

      console.log(`🌐 Making stats API call for extension: ${extension}`)
      console.log(`📊 API endpoint: api/wallonly/ with params: {exten: ${extension}, stats: 1}`)
      
      try {
        statsLoadingStates.value[extension] = true
        console.log(`⏳ Set stats loading state to TRUE for extension: ${extension}`)
        
        const response = await axiosInstance.get('api/wallonly/', {
          params: {
            exten: extension,
            stats: 1
          }
        })
        
        console.log(`✅ Stats API Response received for extension ${extension}:`)
        console.log('Response status:', response.status)
        console.log('Response data:', JSON.stringify(response.data, null, 2))
        
        if (response.data && response.data.stats && response.data.stats.length > 0) {
          // Extract stats from response format: [["0","36","0"]]
          const statsData = response.data.stats[0]
          console.log('Stats data array:', statsData)
          
          if (Array.isArray(statsData) && statsData.length >= 3) {
            const answered = statsData[0] || '0'
            const missed = statsData[1] || '0'
            const talkTime = statsData[2] || '0'
            
            console.log(`📊 EXTRACTED STATS:`, {
              answered: answered,
              missed: missed,
              talkTime: talkTime
            })
            
            const stats = {
              answered: answered,
              missed: missed,
              talkTime: talkTime
            }
            
            counsellorStats.value[extension] = stats
            console.log(`✅ SUCCESS: Set stats for extension ${extension}:`, stats)
            console.log('Updated counsellorStats:', counsellorStats.value)
          } else {
            console.log(`❌ Invalid stats data format for extension ${extension}:`, statsData)
            counsellorStats.value[extension] = { answered: '0', missed: '0', talkTime: '0' }
          }
        } else {
          counsellorStats.value[extension] = { answered: '0', missed: '0', talkTime: '0' }
          console.log(`❌ No stats data found for extension ${extension}`)
          console.log('Response structure:', {
            hasData: !!response.data,
            hasStats: !!(response.data && response.data.stats),
            statsLength: response.data && response.data.stats ? response.data.stats.length : 0
          })
        }
      } catch (error) {
        console.error(`❌ ERROR fetching counsellor stats for extension ${extension}:`)
        console.error('Error details:', error)
        console.error('Error message:', error.message)
        if (error.response) {
          console.error('Response status:', error.response.status)
          console.error('Response data:', error.response.data)
        }
        counsellorStats.value[extension] = { answered: '0', missed: '0', talkTime: '0' }
      } finally {
        statsLoadingStates.value[extension] = false
        console.log(`⏳ Set stats loading state to FALSE for extension: ${extension}`)
        console.log('Final counsellorStats state:', counsellorStats.value)
        console.log('Final statsLoadingStates:', statsLoadingStates.value)
      }
    }

    // Function to fetch counsellor name by extension
    const fetchCounsellorName = async (extension) => {
      console.log(`🚀 STARTING fetchCounsellorName for extension: ${extension}`)
      
      if (!extension || extension === '--') {
        console.log(`❌ Invalid extension: ${extension}`)
        return
      }

      // Don't fetch if already loading
      if (nameLoadingStates.value[extension]) {
        console.log(`⏳ Extension ${extension} already loading, skipping...`)
        return
      }
      
      // Don't fetch if already cached
      if (counsellorNames.value[extension]) {
        console.log(`💾 Extension ${extension} already cached: ${counsellorNames.value[extension]}`)
        return
      }

      console.log(`🌐 Making API call for extension: ${extension}`)
      console.log(`📞 API endpoint: api/wallonly/ with params: {exten: ${extension}, _c: 1}`)
      
      try {
        nameLoadingStates.value[extension] = true
        console.log(`⏳ Set loading state to TRUE for extension: ${extension}`)
        
        const response = await axiosInstance.get('api/wallonly/', {
          params: {
            exten: extension,
            _c: 1
          }
        })
        
        console.log(`✅ API Response received for extension ${extension}:`)
        console.log('Response status:', response.status)
        console.log('Response data:', JSON.stringify(response.data, null, 2))
        
        if (response.data && response.data.users && response.data.users.length > 0) {
          // Extract name from response format: [["329","Natalie"]]
          const userData = response.data.users[0]
          console.log('User data array:', userData)
          console.log('userData[0] (ID/Extension):', userData[0])
          console.log('userData[1] (Name):', userData[1])
          
          if (Array.isArray(userData) && userData.length >= 2) {
            const extractedName = userData[1]
            console.log(`🎯 EXTRACTED NAME: "${extractedName}" (type: ${typeof extractedName})`)
            
            const name = extractedName || 'Unknown'
            counsellorNames.value[extension] = name
            console.log(`✅ SUCCESS: Set name for extension ${extension} = "${name}"`)
            console.log('Updated counsellorNames:', counsellorNames.value)
          } else {
            console.log(`❌ Invalid user data format for extension ${extension}:`, userData)
            counsellorNames.value[extension] = 'Unknown'
          }
        } else {
          counsellorNames.value[extension] = 'Unknown'
          console.log(`❌ No user data found for extension ${extension}`)
          console.log('Response structure:', {
            hasData: !!response.data,
            hasUsers: !!(response.data && response.data.users),
            usersLength: response.data && response.data.users ? response.data.users.length : 0
          })
        }
      } catch (error) {
        console.error(`❌ ERROR fetching counsellor name for extension ${extension}:`)
        console.error('Error details:', error)
        console.error('Error message:', error.message)
        if (error.response) {
          console.error('Response status:', error.response.status)
          console.error('Response data:', error.response.data)
        }
        counsellorNames.value[extension] = 'Unknown'
      } finally {
        nameLoadingStates.value[extension] = false
        console.log(`⏳ Set loading state to FALSE for extension: ${extension}`)
        console.log('Final counsellorNames state:', counsellorNames.value)
        console.log('Final nameLoadingStates:', nameLoadingStates.value)
      }
    }

    // Fetch calls report data using axios
    const fetchCallsReportData = async () => {
      callsReportLoading.value = true
      callsReportError.value = null
      
      try {
        const response = await axiosInstance.get('api/wallonly/rpt', {
          params: {
            dash_period: 'today',
            type: 'bar',
            stacked: 'stacked',
            xaxis: 'hangup_status_txt',
            yaxis: '-',
            vector: 1,
            rpt: 'call_count',
            metrics: 'call_count'
          }
        })
        
        if (response.data) {
          console.log('Calls Report API Response:', response.data)
          callsReportData.value = response.data
        } else {
          throw new Error('No calls report data returned from API')
        }
      } catch (error) {
        console.error('Error fetching calls report data:', error)
        callsReportError.value = error.message
      } finally {
        callsReportLoading.value = false
      }
    }

    // Fetch cases data using axios
    const fetchCasesData = async () => {
      console.log('='.repeat(50))
      console.log('📦 STARTING CASES DATA FETCH!')
      console.log('='.repeat(50))
      
      apiLoading.value = true
      apiError.value = null
      
      try {
        console.log('📦 Calling fetchFromApi() from utils...')
        const data = await fetchFromApi()
        
        console.log('📦 Cases API Raw Response:')
        console.log(JSON.stringify(data, null, 2))
        
        if (data) {
          console.log('✅ Cases data received!')
          console.log('📦 Data structure:')
          console.log('- Has stats property:', !!data.stats)
          console.log('- Stats keys:', data.stats ? Object.keys(data.stats) : 'No stats')
          console.log('- Full stats object:', data.stats)
          
          apiData.value = data
        } else {
          console.log('❌ No data returned from fetchFromApi()')
          throw new Error('No data returned from API')
        }
      } catch (error) {
        console.error('💥 ERROR FETCHING CASES DATA!')
        console.error('Error details:', error)
        console.error('Error message:', error.message)
        apiError.value = error.message
      } finally {
        apiLoading.value = false
        console.log('📦 Cases loading set to false')
        console.log('='.repeat(50))
      }
    }

    // Calls cards data computed from API response
    const callsCards = computed(() => {
      if (!callsReportData.value || !callsReportData.value.calls) {
        return []
      }
      
      // Transform the calls array into card data
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

    // Filters
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
      // Log the raw Asterisk data
      console.log('==========================================')
      console.log('ASTERISK DATA RECEIVED:', new Date().toLocaleString())
      console.log('Raw Payload:', payload)
      console.log('==========================================\n')
      
      lastUpdate.value = new Date().toLocaleString()
      
      let obj = payload
      if (typeof payload === 'string') {
        try {
          obj = JSON.parse(payload)
        } catch (err) {
          console.error('[QueueMonitor] Failed to parse JSON payload', err)
          return
        }
      }

      let chArr = []
      if (Array.isArray(obj.channels)) {
        chArr = obj.channels
      } else if (obj.channels && typeof obj.channels === 'object') {
        chArr = Object.entries(obj.channels).map(([key, arr]) => {
          if (Array.isArray(arr)) {
            return {
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
          }
          return { _uid: key, ...arr }
        })
      }
      
      channels.value = chArr

      // Log all channels for debugging
      console.log('📊 PROCESSED CHANNELS:', chArr.length)
      
      // Trigger name fetching for new counsellor extensions
      const counsellorChannels = chArr.filter(ch => {
        const context = (ch.CHAN_CONTEXT || '').toLowerCase()
        return context === 'agentlogin'
      })
      
      console.log('👥 COUNSELLOR CHANNELS FOUND:', counsellorChannels.length)
      
      counsellorChannels.forEach((ch, index) => {
        const extension = ch.CHAN_EXTEN
        const context = ch.CHAN_CONTEXT
        
        console.log(`👤 Counsellor ${index + 1}:`, {
          extension: extension,
          context: context,
          uniqueId: ch.CHAN_UNIQUEID,
          callerIdName: ch.CHAN_CALLERID_NAME
        })
        
        if (extension && extension !== '--') {
          const alreadyCachedName = counsellorNames.value[extension]
          const currentlyLoadingName = nameLoadingStates.value[extension]
          const alreadyCachedStats = counsellorStats.value[extension]
          const currentlyLoadingStats = statsLoadingStates.value[extension]
          
          console.log(`📝 Extension ${extension} status:`, {
            alreadyCachedName: alreadyCachedName,
            currentlyLoadingName: currentlyLoadingName,
            shouldFetchName: !alreadyCachedName && !currentlyLoadingName,
            alreadyCachedStats: alreadyCachedStats,
            currentlyLoadingStats: currentlyLoadingStats,
            shouldFetchStats: !alreadyCachedStats && !currentlyLoadingStats
          })
          
          if (!alreadyCachedName && !currentlyLoadingName) {
            console.log(`🔍 TRIGGERING NAME FETCH for extension: ${extension}`)
            fetchCounsellorName(extension)
          }
          
          if (!alreadyCachedStats && !currentlyLoadingStats) {
            console.log(`📊 TRIGGERING STATS FETCH for extension: ${extension}`)
            fetchCounsellorStats(extension)
          }
        }
      })
      
      // Log current cached names
      console.log('💾 CURRENT CACHED NAMES:', counsellorNames.value)
      console.log('⏳ CURRENT LOADING STATES:', nameLoadingStates.value)
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
      const counsellorChannels = channels.value.filter(ch => {
        const context = (ch.CHAN_CONTEXT || '').toLowerCase()
        return context === 'agentlogin'
      })

      console.log(`🖥️ COMPUTED: Processing ${counsellorChannels.length} counsellor channels for UI`)
      console.log('🖥️ Current counsellorNames cache:', counsellorNames.value)
      console.log('🖥️ Current nameLoadingStates:', nameLoadingStates.value)
      console.log('🖥️ Current counsellorStats cache:', counsellorStats.value)
      console.log('🖥️ Current statsLoadingStates:', statsLoadingStates.value)

      const result = counsellorChannels.map((ch, index) => {
        const extension = ch.CHAN_EXTEN || '--'
        const isNameLoading = nameLoadingStates.value[extension] || false
        const name = counsellorNames.value[extension] || 'Unknown'
        const isStatsLoading = statsLoadingStates.value[extension] || false
        const stats = counsellorStats.value[extension] || { answered: '--', missed: '--', talkTime: '--' }

        // Find connected caller by matching bridge IDs
        let connectedCallerNumber = '--'
        if (Number(ch.CHAN_STATE_CONNECT) && ch.CHAN_BRIDGE_ID) {
          const connectedCaller = callersData.value.find(caller => 
            caller.channelData.CHAN_BRIDGE_ID === ch.CHAN_BRIDGE_ID
          )
          if (connectedCaller) {
            connectedCallerNumber = connectedCaller.callerNumber
            console.log(`📞 Counsellor ${extension} is talking to caller: ${connectedCallerNumber}`)
          }
        }

        console.log(`🖥️ Counsellor ${index + 1} UI Data:`, {
          extension: extension,
          name: name,
          nameLoading: isNameLoading,
          stats: stats,
          statsLoading: isStatsLoading,
          connectedCaller: connectedCallerNumber,
          bridgeId: ch.CHAN_BRIDGE_ID,
          isConnected: Number(ch.CHAN_STATE_CONNECT),
          context: ch.CHAN_CONTEXT,
          uniqueId: ch.CHAN_UNIQUEID
        })

        return {
          id: ch.CHAN_UNIQUEID || ch._uid,
          extension: extension,
          name: name,
          nameLoading: isNameLoading,
          caller: connectedCallerNumber, // Show connected caller number
          answered: stats.answered,
          missed: stats.missed,
          talkTime: '--', // Keep blank as requested
          statsLoading: isStatsLoading,
          queueStatus: getStatusText(ch),
          duration: Number(ch.CHAN_STATE_CONNECT) ? formatDuration(ch.CHAN_TS) : '--',
          isOnline: true,
          channelData: ch,
          channel: ch.CHAN_CHAN || '--',
          vector: ch.CHAN_VECTOR || '--',
          campaign: ch.CHAN_CAMPAIGN_ID || '--'
        }
      })

      console.log('🖥️ FINAL UI COUNSELLORS LIST:', result)
      return result
    })

    // Callers data - filtered by DLPN_callcenter context (removed name column)
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
      
      // Fetch cases data
      fetchCasesData()
      
      // Fetch calls report data
      fetchCallsReportData()
      
      // Refresh data every 5 minutes
      const dataInterval = setInterval(() => {
        fetchCasesData()
        fetchCallsReportData()
      }, 300000)
      
      // Clean up on unmount
      onBeforeUnmount(() => {
        clearInterval(dataInterval)
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
      
      // Calls report data
      callsReportData,
      callsReportError,
      callsReportLoading,
      callsCards,
      
      // Callers data
      callersData,
      filteredCallers,
      onlineCallersCount,
      
      // Connection status
      connectionClass,
      connectionLabel,
      
      // Axios instance for child components
      axiosInstance,
      
      // Methods
      setActiveFilter,
      statusClass,
      toggleDarkMode
    }
  }
}
</script>
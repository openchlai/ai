<template>
  <div 
    class="space-y-4"
  >
    <!-- Header -->
    <WallboardHeader 
      :connection-status="connectionClass"
      :connection-label="connectionLabel"
      :last-update="lastUpdate"
      :is-dark-mode="isDarkMode"
      @toggle-theme="toggleTheme"
    />

    <!-- Main Dashboard Grid -->
    <div class="mt-4 grid grid-cols-1 xl:grid-cols-12 gap-4">
      
      <!-- Top Section: Stats Tiles (Full width) -->
      <div class="xl:col-span-12">
        <CasesTiles :tiles="casesTiles" />
      </div>

      <!-- Bottom Section: Tables (Full width) -->
      <div class="xl:col-span-12 grid grid-cols-1 lg:grid-cols-2 gap-4">
        <CounsellorsTable 
          :counsellors="counsellorsWithQueueData"
          :online-count="onlineCounsellorsCount"
        />
        
        <CallersTable 
          :callers="callersData"
          :online-count="onlineCallersCount"
        />
      </div>

    </div>
  </div>
</template>

<script>
import { computed, onMounted, onBeforeUnmount, watch, provide } from 'vue'
import axiosInstance from "@/utils/axios.js"

// Import components
import WallboardHeader from '@/components/wallboard/WallboardHeader.vue'
import CasesTiles from '@/components/wallboard/CasesTiles.vue'
import CounsellorsTable from '@/components/wallboard/CounsellorsTable.vue'
import CallersTable from '@/components/wallboard/CallersTable.vue'

// Import utilities
import { useWebSocketConnection } from '@/composables/useWebSocketConnection.js'
import { useCounsellorData } from '@/composables/useCounsellorData'
import { useApiData } from '@/composables/useApiData'
import { formatDuration, getStatusText } from '@/utils/formatters'
import { useTheme } from '@/composables/useTheme' // ✅ Import shared theme composable

// Use environment variable or fallback to new demo server
const AMI_HOST = import.meta.env.VITE_AMI_WS_URL || 'wss://demo-openchs.bitz-itc.com:8384/ami/sync'
const WSHOST = `${AMI_HOST}?c=-2`

export default {
  name: 'App',
  components: {
    WallboardHeader,
    CasesTiles,
    CounsellorsTable,
    CallersTable
  },
  setup() {
    // ✅ Use the SHARED theme composable instead of local state
    const { isDarkMode, toggleTheme } = useTheme()
    
    // Provide theme to all child components
    provide('isDarkMode', isDarkMode)
    provide('toggleTheme', toggleTheme)
    
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
      wallboardData,
      fetchCasesData,
      fetchLiveAgents
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
          label: "Today's Answered", 
          value: stats.calls_today || '0', 
          variant: 'blue',
          icon: 'phone'
        },
        { 
          id: 'ct2', 
          label: "Today's Cases", 
          value: stats.cases_today || '0', 
          variant: 'amber',
          icon: 'folder'
        },
        { 
          id: 'ct3', 
          label: 'Ongoing Cases', 
          value: stats.cases_ongoing_total || '0', 
          variant: 'red',
          icon: 'alert'
        },
        { 
          id: 'ct4', 
          label: 'Month Closed', 
          value: stats.cases_closed_this_month || '0', 
          variant: 'green',
          icon: 'check'
        },
        { 
          id: 'ct5', 
          label: 'Total Calls', 
          value: stats.calls_total || '0', 
          variant: 'purple',
          icon: 'chart'
        },
        { 
          id: 'ct6', 
          label: 'Total Cases', 
          value: stats.cases_total || '0', 
          variant: 'indigo',
          icon: 'database'
        }
      ]
      
      return tiles
    })

    // Separate counsellors and callers based on CHAN_CONTEXT
    const counsellorsWithQueueData = computed(() => {
      // 1. Combine Logged-in Agents from both 'live' and 'users' API collections
      const { live, users, live_k, users_k } = wallboardData.value
      
      const processApiList = (list, k, source) => {
          if (!list || list.length === 0) return []
          
          // Extension is usually at index 7 based on legacy keys, or found by name
          // Fallback to commonly observed indices if keys are missing
          const extIdx = k.exten?.[0] ?? k.extension?.[0] ?? 0
          const nameIdx = k.contact_fullname?.[0] ?? k.name?.[0] ?? 1
          
          return list.map(row => {
              const extension = String(row[extIdx] || '')
              const name = row[nameIdx] || 'Unknown'
              
              return {
                  extension,
                  name,
                  isAvailable: true,
                  source
              }
          }).filter(a => a.extension && a.extension !== 'undefined' && a.extension !== 'null')
      }

      const apiAgents = [
          ...processApiList(live, live_k, 'live'),
          ...processApiList(users, users_k, 'users')
      ]

      // 2. Identify active channels from WebSocket for counsellors
      const activeChannels = channels.value.filter(ch => {
        const context = (ch.CHAN_CONTEXT || '').toLowerCase()
        return context === 'agentlogin' || context === 'counselor' || context === 'agent' || context.includes('login')
      })

      // 3. Merge: Start with API list, then add WS agents (deduplicate by extension)
      const mergedMap = new Map()
      
      apiAgents.forEach(a => {
          // Normalize extension
          const key = String(a.extension)
          if (!mergedMap.has(key)) {
              mergedMap.set(key, { ...a, isOnline: true })
          }
      })
      
      activeChannels.forEach(ch => {
          const ext = String(ch.CHAN_EXTEN)
          const existing = mergedMap.get(ext)
          if (existing) {
              existing.channelData = ch
              existing.id = ch.CHAN_UNIQUEID || ch._uid
          } else {
              mergedMap.set(ext, {
                  extension: ext,
                  name: counsellorNames.value[ext] || 'User ' + ext,
                  channelData: ch,
                  id: ch.CHAN_UNIQUEID || ch._uid,
                  isOnline: true,
                  isAvailable: true,
                  source: 'websocket'
              })
          }
      })

      const finalRows = Array.from(mergedMap.values()).map(agent => {
        const ch = agent.channelData
        const stats = counsellorStats.value[agent.extension] || { answered: '--', missed: '--', talkTime: '--' }

        return {
          id: agent.id || `agent-${agent.extension}`,
          extension: agent.extension,
          name: agent.name,
          caller: agent.callerNumber || '--',
          answered: stats.answered,
          missed: stats.missed,
          talkTime: '--',
          queueStatus: ch ? getStatusText(ch) : (agent.isAvailable ? 'Available' : 'Paused'),
          duration: (ch && Number(ch.CHAN_STATE_CONNECT)) ? formatDuration(ch.CHAN_TS) : '--',
          isOnline: true,
          channelData: ch
        }
      })

      if (finalRows.length > 0) {
          // console.info('[Wallboard] Final Merged List Count:', finalRows.length)
      }

      return finalRows
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

    // Lifecycle
    onMounted(() => {
      // Connect to WebSocket
      connect(channels, fetchCounsellorName, fetchCounsellorStats)
      
      // Fetch initial data
      fetchCasesData()
      fetchLiveAgents()
      
      // Refresh data periodically
      const dataInterval = setInterval(() => {
        fetchCasesData()
        fetchLiveAgents()
      }, 30000) // Lowered to 30s for better live feel
      
      onBeforeUnmount(() => {
        clearInterval(dataInterval)
        disconnect()
      })
    })

    // Watch for data changes
    watch(() => apiData.value, (newVal) => {
      // console.log('apiData changed:', newVal)
    })
    
    watch(() => channels.value, (newVal) => {
      // Channels updated
    })

    return {
      // State
      isDarkMode,
      
      // Data
      casesTiles,
      counsellorsWithQueueData,
      onlineCounsellorsCount,
      callersData,
      onlineCallersCount,
      
      // Connection status
      connectionClass,
      connectionLabel,
      lastUpdate,
      
      // Methods
      toggleTheme // ✅ Now uses shared toggleTheme
    }
  }
}
</script>
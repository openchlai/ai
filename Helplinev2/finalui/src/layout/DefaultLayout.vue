<template>
  <div class="flex min-h-screen" :class="isDarkMode ? 'bg-[#0B1120]' : 'bg-gray-50'">
    <!-- Fixed Sidebar - Only show when NOT on login page -->
    <Sidebar v-if="showSidebar" :isDarkMode="isDarkMode" @toggle-theme="toggleTheme" />
    
    <!-- Main Content Area with conditional left margin -->
    <div 
      class="flex-1 flex flex-col min-h-screen relative" 
      :class="[
        showSidebar ? 'ml-64' : '',
        isDarkMode ? 'bg-[#0B1120]' : 'bg-gray-50'
      ]"
    >
      <!-- Static Navbar -->
      <Navbar v-if="showSidebar" :isDarkMode="isDarkMode" />

      <!-- Main Content Container -->
      <main class="flex-1 overflow-auto p-6">
        <RouterView />
      </main>
    </div>

    <!-- Global Active Call Toolbar -->
    <ActiveCallToolbar />
  </div>
</template>

<script setup>
import { computed, provide, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import { useTheme } from '@/composables/useTheme'
import { useAuthStore } from '@/stores/auth'
import { useRealtimeStore } from '@/stores/realtime'
import { useActiveCallStore } from '@/stores/activeCall'
import { useAiInsightsFetcher } from '@/composables/useAiInsightsFetcher'
import Sidebar from '@/components/layout/Sidebar.vue'
import Navbar from '@/components/layout/Navbar.vue'
import ActiveCallToolbar from '@/components/softphone/ActiveCallToolbar.vue'

const route = useRoute()
const { isDarkMode, toggleTheme } = useTheme()
const authStore = useAuthStore()
const realtimeStore = useRealtimeStore()
const activeCallStore = useActiveCallStore()

// Provide theme to all child components
provide('isDarkMode', isDarkMode)
provide('toggleTheme', toggleTheme)

// Hide sidebar and navbar on login page
const showSidebar = computed(() => {
  return route.path !== '/login'
})

// ── Global Real-Time Connections ────────────────────────────────
onMounted(() => {
  if (authStore.isAuthenticated && route.path !== '/login') {
    realtimeStore.connect()
  }
})

// React to auth changes (login/logout)
watch(() => authStore.isAuthenticated, (isAuth) => {
  if (isAuth) {
    realtimeStore.connect()
  } else {
    realtimeStore.disconnect()
  }
})

onBeforeUnmount(() => {
  realtimeStore.disconnect()
})

// ── AMI → activeCall Enrichment Bridge ──────────────────────────
// When a call is active, find its AMI channel and sync UniqueID + BridgeID
watch(
  () => realtimeStore.amiChannelsList,
  (channels) => {
    if (!['ringing', 'active', 'calling'].includes(activeCallStore.callState)) return

    const ext = authStore.profile?.extension || authStore.profile?.exten
    if (!ext) return

    const match = channels.find(ch =>
      ch.CHAN_EXTEN === String(ext) ||
      ch.CHAN_CALLERID_NUM === activeCallStore.callerNumber
    )

    if (match) {
      if (!activeCallStore.src_uid && match.CHAN_UNIQUEID) {
        console.log('[Realtime] AMI enrichment: syncing UniqueID', match.CHAN_UNIQUEID)
        activeCallStore.setAmiUniqueId(match.CHAN_UNIQUEID)
      }
      if (match.CHAN_BRIDGE_ID) {
        activeCallStore.setBridgeId(match.CHAN_BRIDGE_ID)
      }
    }
  }
)

// ── ATI → activeCall AI Insights Bridge ─────────────────────────
// Monitors ATI text channel for AI notifications (src='aii', context='trunk')
// and matches them against the active call via bridge_id, src_uid, src_callid,
// or lastCallUniqueId (persisted in store through wrapup into case-creation).
// Insights arrive AFTER the call ends (20–120s processing).
const { fetchAiInsightsForCall, scheduleRetry } = useAiInsightsFetcher()

watch(
  () => realtimeStore.aiNotifications,
  async (notifications) => {
    if (!notifications.length) return

    // Allow processing during active call, wrapup, OR while on case-creation page
    const isActiveCall = ['active', 'wrapup'].includes(activeCallStore.callState)
    const isCaseCreation = route.path.includes('case-creation')

    if (!isActiveCall && !isCaseCreation) return

    // Collect all possible IDs to match against ATI_BRIDGE_ID
    const callIds = new Set()
    if (activeCallStore.bridge_id) callIds.add(activeCallStore.bridge_id)
    if (activeCallStore.src_uid) callIds.add(activeCallStore.src_uid)
    if (activeCallStore.src_callid) callIds.add(activeCallStore.src_callid)
    if (activeCallStore.lastCallUniqueId) callIds.add(activeCallStore.lastCallUniqueId)
    if (route.query.uniqueid) callIds.add(route.query.uniqueid)

    if (callIds.size === 0) return

    // Find matching notification
    const matchedNotif = notifications.find(n => callIds.has(n.ATI_BRIDGE_ID))
    if (!matchedNotif) return

    const queryCallId = matchedNotif.ATI_BRIDGE_ID

    console.log('[AI Panel] ATI notification matched call_id:', queryCallId)

    await fetchAiInsightsForCall(queryCallId)
    scheduleRetry(queryCallId)
  },
  { deep: true }
)
</script>
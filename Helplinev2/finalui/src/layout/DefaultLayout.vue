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

    const matches = channels.filter(ch =>
      (ch.CHAN_EXTEN === String(ext) ||
       ch.CHAN_CALLERID_NUM === activeCallStore.callerNumber) &&
      (ch.CHAN_STATE_UP || ch.CHAN_STATE_QUEUE || ch.CHAN_STATE_CONNECT)
    )
    // Sort descending by CHAN_UNIQUEID (epoch.sequence) so the most recently
    // created channel wins — stale channels from prior calls sort to the back.
    const match = matches.sort((a, b) =>
      parseFloat(b.CHAN_UNIQUEID) - parseFloat(a.CHAN_UNIQUEID)
    )[0]

    if (match) {
      console.group('[AMI] Call ID snapshot — state: ' + activeCallStore.callState)
      console.log('candidates          :', matches.length, '→ UIDs:', matches.map(c => c.CHAN_UNIQUEID))
      console.log('selected CHAN_UNIQUEID  :', match.CHAN_UNIQUEID)
      console.log('selected CHAN_UNIQUEID_2:', match.CHAN_UNIQUEID_2, '← = ATI_BRIDGE_ID (stored as lastCallerUniqueId)')
      console.log('selected CHAN_BRIDGE_ID :', match.CHAN_BRIDGE_ID)
      console.groupEnd()

      if (!activeCallStore.src_uid && match.CHAN_UNIQUEID) {
        activeCallStore.setAmiUniqueId(match.CHAN_UNIQUEID)
      }
      if (match.CHAN_BRIDGE_ID) {
        activeCallStore.setBridgeId(match.CHAN_BRIDGE_ID)
      }
      if (match.CHAN_UNIQUEID_2) {
        activeCallStore.setCallerUniqueId(match.CHAN_UNIQUEID_2)
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

    // AI insights are post-call; block entirely during live call states
    const callIsLive = ['active', 'calling', 'ringing'].includes(activeCallStore.callState)
    if (callIsLive) return

    const isCaseCreation = route.path.includes('case-creation')
    const isWrapup = activeCallStore.callState === 'wrapup'

    if (!isWrapup && !isCaseCreation) return

    // Collect all possible IDs to match against ATI_BRIDGE_ID
    const callIds = new Set()
    if (activeCallStore.bridge_id) callIds.add(activeCallStore.bridge_id)
    if (activeCallStore.src_uid) callIds.add(activeCallStore.src_uid)
    if (activeCallStore.src_callid) callIds.add(activeCallStore.src_callid)
    if (activeCallStore.lastCallUniqueId) callIds.add(activeCallStore.lastCallUniqueId)
    if (activeCallStore.lastCallerUniqueId) callIds.add(activeCallStore.lastCallerUniqueId)
    if (route.query.uniqueid) callIds.add(route.query.uniqueid)
    if (route.query.call_id) callIds.add(route.query.call_id)

    if (callIds.size === 0) return

    // Find matching notification
    let matchedNotif = notifications.find(n => callIds.has(n.ATI_BRIDGE_ID))

    if (!matchedNotif) {
      // No ATI notification matches any of our known call IDs — the real notification
      // for this call hasn't arrived yet (AI pipeline takes 20–120s post-call).
      // Do NOT fall back to the numerically largest ATI_BRIDGE_ID; that would pick up
      // a stale notification from a previous call and load the wrong insights.
      // Just wait — the watcher will fire again when the correct notification arrives.
      console.log('[AI Panel] No ID match for current call IDs:', Array.from(callIds), '— waiting for correct ATI notification')
      return
    }

    const queryCallId = matchedNotif.ATI_BRIDGE_ID

    console.group('[AI DEBUG] ATI notification — call ID resolution')
    console.log('ATI_BRIDGE_ID (from notification)  :', queryCallId)
    console.log('activeCallStore.bridge_id           :', activeCallStore.bridge_id)
    console.log('activeCallStore.lastCallUniqueId     :', activeCallStore.lastCallUniqueId)
    console.log('activeCallStore.src_uid              :', activeCallStore.src_uid)
    console.log('activeCallStore.src_callid           :', activeCallStore.src_callid)
    console.log('activeCallStore.callState            :', activeCallStore.callState)
    console.log('route.query.call_id                  :', route.query.call_id)
    console.log('route.query.uniqueid                 :', route.query.uniqueid)
    console.groupEnd()

    console.log('[AI Panel] ATI notification matched call_id:', queryCallId)
    console.log('Call Ids in store:', Array.from(callIds).join(', '))

    await fetchAiInsightsForCall(queryCallId)
    scheduleRetry(queryCallId)
  },
  { deep: true }
)
</script>
// composables/useAiInsightsFetcher.js
// Shared logic for fetching post-call AI insights from the predictions pipeline.
// Uses module-level singletons so dedup and in-progress state are shared across
// all components that use this composable (DefaultLayout, CaseCreate, CaseSingleFormView).
import { ref } from 'vue'
import axiosInstance from '@/utils/axios'
import { useActiveCallStore } from '@/stores/activeCall'
import { useAuthStore } from '@/stores/auth'

const _aiFetchInProgress = ref(false)
const _fetchedCallIds = new Set()
let _retryTimer = null

export function useAiInsightsFetcher() {
  const activeCallStore = useActiveCallStore()
  const authStore = useAuthStore()

  async function fetchAiInsightsForCall(queryCallId) {
    if (!queryCallId || _aiFetchInProgress.value) return
    if (_fetchedCallIds.has(queryCallId)) return

    _aiFetchInProgress.value = true
    _fetchedCallIds.add(queryCallId)

    console.log('[AI Panel] Fetching insights for call_id:', queryCallId)

    try {
      // Fetch all AI messages for this call directly from the flat messages table.
      // The ATI service stores insights via rest_uri_post("messages") — they live in
      // the msg table (api/messages/), NOT in pmessage sessions (api/pmessages/).
      const { data } = await axiosInstance.get('api/messages/', {
        params: { src_callid: queryCallId, src: 'aii', _c: 30, sort: 'id' },
        headers: { 'Session-Id': authStore.sessionId }
      })

      const messages = data.messages || []
      const msgKeys = data.messages_k || {}
      const srcMsgIdx = msgKeys.src_msg ? msgKeys.src_msg[0] : 17 // src_msg is at index 17

      if (!messages.length) {
        console.log('[AI Panel] No AI messages yet for call_id:', queryCallId)
        _fetchedCallIds.delete(queryCallId)  // Allow retry when ATI notification arrives later
        return
      }

      let added = 0
      for (const row of messages) {
        const rawMsg = row[srcMsgIdx]
        if (!rawMsg) continue
        try {
          const decoded = JSON.parse(atob(rawMsg))
          if (decoded && decoded.notification_type) {
            activeCallStore.addAiInsight(decoded)
            added++
          }
        } catch (e) {
          // Skip non-JSON or invalid base64 entries
        }
      }
      console.log(`[AI Panel] Decoded ${added} insights from ${messages.length} messages for call_id ${queryCallId}`)
    } catch (err) {
      console.warn('[AI Panel] Failed to fetch AI insights:', err.message)
      // Remove from fetched set so a retry is possible
      _fetchedCallIds.delete(queryCallId)
    } finally {
      _aiFetchInProgress.value = false
    }
  }

  // Schedule a one-time retry to catch late-arriving insights (AI pipeline may still be writing)
  function scheduleRetry(queryCallId, delayMs = 15000) {
    if (_retryTimer) clearTimeout(_retryTimer)
    _retryTimer = setTimeout(() => {
      _retryTimer = null
      console.log('[AI Panel] Retry fetch for late-arriving insights:', queryCallId)
      _fetchedCallIds.delete(queryCallId)
      fetchAiInsightsForCall(queryCallId)
    }, delayMs)
  }

  return { fetchAiInsightsForCall, scheduleRetry }
}

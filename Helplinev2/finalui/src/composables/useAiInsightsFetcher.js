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

    // Never fetch insights while a call is live — they are post-call only
    const callIsLive = ['active', 'calling', 'ringing'].includes(activeCallStore.callState)
    if (callIsLive) return

    _aiFetchInProgress.value = true
    _fetchedCallIds.add(queryCallId)

    console.group(`[AI DEBUG] fetchAiInsightsForCall — call_id: ${queryCallId}`)
    console.log('In progress:', _aiFetchInProgress.value)
    console.log('Already fetched:', _fetchedCallIds.has(queryCallId))
    console.log('Fetched IDs set:', [..._fetchedCallIds])
    console.groupEnd()

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

      console.group('[AI DEBUG] api/messages/ response')
      console.log('params sent        :', { src_callid: queryCallId, src: 'aii', _c: 30, sort: 'id' })
      console.log('messages count     :', messages.length)
      console.log('messages_k         :', msgKeys)
      console.log('srcMsgIdx used     :', srcMsgIdx)
      if (messages.length > 0) {
        console.log('first raw row      :', messages[0])
      }
      console.groupEnd()

      if (!messages.length) {
        console.warn('[AI DEBUG] api/messages/ returned 0 results for call_id:', queryCallId, '— will allow retry')
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
          console.log('[AI DEBUG] decoded insight:', decoded?.notification_type, decoded)
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

  // Schedule a one-time retry to catch late-arriving insights (AI pipeline may still be writing).
  // Snapshots the current bridge_id so the retry is silently dropped if the call context
  // has changed by the time the timer fires (prevents stale call 1 data leaking into call 2).
  function scheduleRetry(queryCallId, delayMs = 15000) {
    if (_retryTimer) clearTimeout(_retryTimer)
    const snapshotBridgeId = activeCallStore.bridge_id
    _retryTimer = setTimeout(() => {
      _retryTimer = null
      // If the bridge ID changed since scheduling, this retry belongs to a stale call — skip it
      if (activeCallStore.bridge_id !== snapshotBridgeId) {
        console.log('[AI DEBUG] scheduleRetry cancelled — bridge_id changed from', snapshotBridgeId, 'to', activeCallStore.bridge_id)
        return
      }
      console.log('[AI DEBUG] scheduleRetry firing for call_id:', queryCallId, 'after', delayMs, 'ms')
      console.log('[AI Panel] Retry fetch for late-arriving insights:', queryCallId)
      _fetchedCallIds.delete(queryCallId)
      fetchAiInsightsForCall(queryCallId)
    }, delayMs)
  }

  return { fetchAiInsightsForCall, scheduleRetry }
}

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
      // Step 1: Get conversation list to find the pmessage ID
      const { data: listData } = await axiosInstance.get('api/pmessages/', {
        params: { src_callid: queryCallId, src: 'aii', _c: 30 },
        headers: { 'Session-Id': authStore.sessionId }
      })

      const conversations = listData.pmessages || []
      const listKeys = listData.pmessages_k || {}

      if (!conversations.length || !listKeys.id) {
        console.log('[AI Panel] No conversations found for call_id:', queryCallId)
        return
      }

      const idIdx = listKeys.id[0]

      // Step 2: For each conversation fetch all individual messages
      for (const conv of conversations) {
        const pmessageId = conv[idIdx]
        if (!pmessageId) continue

        console.log('[AI Panel] Fetching message details for pmessage:', pmessageId)

        const { data: detailData } = await axiosInstance.get(`api/pmessages/${pmessageId}?`, {
          headers: { 'Session-Id': authStore.sessionId }
        })

        if (detailData.messages && detailData.messages_k) {
          const msgKeys = detailData.messages_k
          const srcMsgIdx = msgKeys.src_msg ? msgKeys.src_msg[0] : -1
          if (srcMsgIdx === -1) continue

          let added = 0
          for (const row of detailData.messages) {
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
          console.log(`[AI Panel] Decoded ${added} insights from pmessage ${pmessageId} (${detailData.messages.length} total messages)`)
        }
      }
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

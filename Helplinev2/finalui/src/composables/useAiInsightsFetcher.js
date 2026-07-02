// composables/useAiInsightsFetcher.js
// Shared logic for fetching post-call AI insights from the predictions pipeline.
// Uses module-level singletons so dedup and in-progress state are shared across
// all components that use this composable (DefaultLayout, CaseCreate, CaseSingleFormView).
import { ref, watch } from 'vue'
import axiosInstance from '@/utils/axios'
import { useActiveCallStore } from '@/stores/activeCall'
import { useAuthStore } from '@/stores/auth'

const _aiFetchInProgress = ref(false)
const _isRetrying = ref(false)   // true while waiting between retries
const _hasGivenUp = ref(false)   // true after all retries exhausted
const _currentRetryAttempt = ref(0) // 0 = initial fetch, 1-4 = which retry we're on
const _fetchedCallIds = new Set()
const _retryCountMap = new Map() // callId → retry count (0-based)
const RETRY_DELAYS = [15000, 30000, 60000, 120000]
let _retryTimer = null
let _bridgeIdResolved = false
let _deferredFetchUnwatch = null

export function useAiInsightsFetcher() {
  const activeCallStore = useActiveCallStore()
  const authStore = useAuthStore()

  function _decodeAndStore(rawMsg) {
    if (!rawMsg) return false
    let decoded
    try {
      decoded = JSON.parse(rawMsg)
    } catch {
      try {
        decoded = JSON.parse(atob(rawMsg))
      } catch {
        return false
      }
    }
    if (!decoded) return false
    // Support legacy `step` field when notification_type is absent
    if (!decoded.notification_type && decoded.step) {
      decoded.notification_type = 'post_call_' + decoded.step
    }
    if (decoded.notification_type) {
      const normalized = decoded.notification_type.replace(/^postcall_/, 'post_call_')
      if (!normalized.startsWith('post_call_')) return false
      activeCallStore.addAiInsight(decoded)
      return true
    }
    return false
  }

  async function fetchAiInsightsForCall(queryCallId) {
    if (!queryCallId || _aiFetchInProgress.value) return
    if (_fetchedCallIds.has(queryCallId)) return

    _aiFetchInProgress.value = true
    _fetchedCallIds.add(queryCallId)

    console.log('[AI Panel] Fetching insights for call_id:', queryCallId)

    try {
      const { data } = await axiosInstance.get('api/messages/', {
        params: { src_callid: queryCallId, _c: 30, sort: 'id' },
        headers: { 'Session-Id': authStore.sessionId }
      })

      const messages = data.messages || []
      const msgKeys = data.messages_k || {}

      if (!messages.length) {
        console.log('[AI Panel] No messages found for call_id:', queryCallId)
        _fetchedCallIds.delete(queryCallId)
        _scheduleRetry(queryCallId)
        return
      }

      // src_msg is at index 17 (raw JSON, not base64)
      const srcMsgIdx = msgKeys.src_msg ? msgKeys.src_msg[0] : 17

      let added = 0
      for (const row of messages) {
        if (_decodeAndStore(row[srcMsgIdx])) added++
      }

      console.log(`[AI Panel] Decoded ${added} insights from ${messages.length} messages for call ${queryCallId}`)

      if (added === 0) {
        // Messages exist but none decoded — retry in case pipeline is still writing
        _fetchedCallIds.delete(queryCallId)
        _scheduleRetry(queryCallId)
      }
    } catch (err) {
      console.warn('[AI Panel] Failed to fetch AI insights:', err.message)
      _fetchedCallIds.delete(queryCallId)
      _scheduleRetry(queryCallId)
    } finally {
      _aiFetchInProgress.value = false
    }
  }

  function _scheduleRetry(queryCallId) {
    const count = _retryCountMap.get(queryCallId) ?? 0
    if (count >= RETRY_DELAYS.length) {
      console.log('[AI Panel] Max retries reached for call_id:', queryCallId)
      _hasGivenUp.value = true
      return
    }
    if (_retryTimer) clearTimeout(_retryTimer)
    const delay = RETRY_DELAYS[count]
    _retryCountMap.set(queryCallId, count + 1)
    _currentRetryAttempt.value = count + 1
    _isRetrying.value = true
    console.log(`[AI Panel] Scheduling retry ${count + 1}/${RETRY_DELAYS.length} in ${delay / 1000}s for:`, queryCallId)
    _retryTimer = setTimeout(() => {
      _retryTimer = null
      _isRetrying.value = false
      fetchAiInsightsForCall(queryCallId)
    }, delay)
  }

  async function resolveAndFetch() {
    // Block fetch while a call is in progress; re-run automatically on wrapup/idle
    const state = activeCallStore.callState
    if (['ringing', 'calling', 'active'].includes(state)) {
      console.log('[AI Panel] Call in progress (' + state + ') — deferring fetch...')
      if (_deferredFetchUnwatch) _deferredFetchUnwatch()
      _deferredFetchUnwatch = watch(
        () => activeCallStore.callState,
        (newState) => {
          if (['wrapup', 'idle'].includes(newState)) {
            if (_deferredFetchUnwatch) { _deferredFetchUnwatch(); _deferredFetchUnwatch = null }
            resolveAndFetch()
          }
        }
      )
      return
    }

    // Already have a valid Asterisk bridge_id (contains a dot: timestamp.sequence)
    let callId = activeCallStore.bridge_id
    if (callId && callId.includes('.')) {
      if (activeCallStore.aiInsights.length === 0) fetchAiInsightsForCall(callId)
      return
    }

    // Try to resolve from calls API using caller phone number (once per call)
    if (!_bridgeIdResolved) {
      _bridgeIdResolved = true
      const callerNum = activeCallStore.callerNumber
      const isValidCaller = callerNum && callerNum !== 'Unknown' && callerNum !== 'Unknown Caller'

      if (isValidCaller) {
        try {
          const { data } = await axiosInstance.get('api/calls/', {
            params: { phone: callerNum, _c: 1, _o: 0, _a: 0 },
            headers: { 'Session-Id': authStore.sessionId }
          })
          const calls = data.calls || []
          if (calls.length) {
            const uidIdx = data.calls_k?.uniqueid?.[0] ?? 0
            const resolved = calls[0][uidIdx]
            if (resolved && String(resolved).includes('.')) {
              console.log('[AI Panel] Resolved bridge_id from calls API:', resolved)
              activeCallStore.setBridgeId(String(resolved))
              callId = String(resolved)
            }
          }
        } catch (e) {
          console.warn('[AI Panel] Could not resolve bridge_id from calls API:', e.message)
        }
      }
    }

    // Fall back to lastCallUniqueId if resolution failed
    if (!callId) callId = activeCallStore.lastCallUniqueId

    if (callId && activeCallStore.aiInsights.length === 0) {
      fetchAiInsightsForCall(callId)
    }
  }

  function resetForNewCall() {
    if (_retryTimer) {
      clearTimeout(_retryTimer)
      _retryTimer = null
    }
    if (_deferredFetchUnwatch) {
      _deferredFetchUnwatch()
      _deferredFetchUnwatch = null
    }
    _fetchedCallIds.clear()
    _retryCountMap.clear()
    _bridgeIdResolved = false
    _isRetrying.value = false
    _hasGivenUp.value = false
    _currentRetryAttempt.value = 0
    console.log('[AI Panel] Reset fetcher state for new call')
  }

  return {
    fetchAiInsightsForCall,
    resolveAndFetch,
    resetForNewCall,
    isFetching: _aiFetchInProgress,
    isRetrying: _isRetrying,
    hasGivenUp: _hasGivenUp,
    retryAttempt: _currentRetryAttempt,
    maxRetries: RETRY_DELAYS.length
  }
}

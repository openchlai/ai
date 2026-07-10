import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'
import { ref } from 'vue'

export const useActiveCallStore = defineStore('activeCall', () => {
    // State
    const currentSession = ref(null)
    const callState = ref('idle') // idle, ringing, active, ended
    const callerNumber = ref('')
    const ssid = ref('')
    const src_callid = ref('')
    const src_uid = ref(null) // AMI CHAN_UNIQUEID
    const bridge_id = ref('') // AMI CHAN_BRIDGE_ID — used for AI insight matching
    const aiInsights = ref([]) // Decoded AI insight payloads for current call
    const _seenInsightTypes = new Set() // Dedup tracker (notification_type keys)
    const lastCallUniqueId = ref('') // Persists the call's CHAN_UNIQUEID across wrapup into case-creation
    const startedAt = ref(null)
    const durationSeconds = ref(0)
    const hasAudioTrack = ref(false)
    const autoAnswerEnabled = ref(localStorage.getItem('sip_auto_answer') === 'true')
    const awaitingQueueConfirmation = ref(false)
    let isQueueConfirmationCall = false

    function toggleAutoAnswer() {
        autoAnswerEnabled.value = !autoAnswerEnabled.value
        localStorage.setItem('sip_auto_answer', autoAnswerEnabled.value)
    }

    let timerInterval = null
    let wrapupTimer = null
    const ringtoneAudio = new Audio('/sounds/ringtone.mp3')
    ringtoneAudio.loop = true

    // Warm-up function to be called on user interaction (e.g., 'Go Online' click)
    function initRingtone() {
        console.log('[ActiveCall] Initializing ringtone audio context...')
        ringtoneAudio.volume = 0
        ringtoneAudio.play().then(() => {
            ringtoneAudio.pause()
            ringtoneAudio.currentTime = 0
            ringtoneAudio.volume = 1
        }).catch(e => console.warn('Ringtone init failed (autoplay blocked):', e))
    }

    function playRingtone() {
        ringtoneAudio.currentTime = 0
        ringtoneAudio.volume = 1
        ringtoneAudio.play().catch(e => console.warn('Ringtone playback failed (user interaction required):', e))
    }

    function stopRingtone() {
        ringtoneAudio.pause()
        ringtoneAudio.currentTime = 0
    }

    // Actions
    function onIncomingCall(session) {
        console.log('[STORE-DEBUG] onIncomingCall triggered. Current State:', callState.value)

        // Relaxed busy check to allow self-dial/testing scenarios
        if (callState.value !== 'idle') {
            console.warn('[STORE-DEBUG] Incoming call while busy - overriding session', callState.value)
            resetCall() // Force clear previous outbound state
        }

        currentSession.value = session
        callState.value = 'ringing'

        // Extract caller number from session remote identity
        try {
            // Check possible paths for remote identity
            if (session.remoteIdentity && session.remoteIdentity.uri && session.remoteIdentity.uri.user) {
                callerNumber.value = session.remoteIdentity.uri.user
            } else if (session.request && session.request.from && session.request.from.uri && session.request.from.uri.user) {
                callerNumber.value = session.request.from.uri.user
            } else {
                callerNumber.value = 'Unknown Caller'
            }
        } catch (e) {
            console.error('Error extracting caller ID:', e)
            callerNumber.value = 'Unknown'
        }

        // Legacy ID extraction
        try {
            ssid.value = session.id
            src_callid.value = session.id.substring(0, 20)
        } catch (e) {
            ssid.value = 'unknown-id'
        }

        src_uid.value = null // Will be set later via AMI or header

        // Seed lastCallUniqueId from SIP call-id immediately as a fallback.
        // The AMI enrichment bridge will overwrite this with the accurate CHAN_UNIQUEID once available.
        if (src_callid.value) lastCallUniqueId.value = src_callid.value

        // Queue confirmation call: Asterisk sends INVITE after agent joins queue.
        // Auto-answer this to complete the login, same as the old UI behavior.
        if (awaitingQueueConfirmation.value) {
            console.log('[ActiveCall] Queue confirmation call detected — auto-answering in 500ms...')
            awaitingQueueConfirmation.value = false
            isQueueConfirmationCall = true
            setTimeout(() => answerCall(), 500)
            return // Don't ring for confirmation calls
        }

        playRingtone()

        // Auto-answer if user has enabled the toggle
        if (autoAnswerEnabled.value) {
            console.log('[ActiveCall] Auto-answer enabled — answering in 500ms...')
            setTimeout(() => answerCall(), 500)
        }
    }

    function startOutboundCall(session) {
        if (callState.value !== 'idle') {
            console.warn('Cannot start outbound call while busy')
            return
        }
        currentSession.value = session
        callState.value = 'calling'

        // For outbound, remote identity is the target
        // session.request.ruri.user might be available if created via Inviter
        // Or we just rely on what we dialed.
        // SIP.js Inviter usually has 'uri' property for target
        if (session.request && session.request.ruri) {
            callerNumber.value = session.request.ruri.user
        } else {
            callerNumber.value = 'Outbound'
        }

        console.log('Starting outbound call to:', callerNumber.value)
    }

    function callEstablished() {
        if (!currentSession.value) return

        console.log('Call established')
        stopRingtone()
        callState.value = 'active'
        startedAt.value = new Date()
        startTimer()
    }

    async function answerCall() {
        if (!currentSession.value) {
            console.error('Cannot answer: No current session')
            return
        }

        // Wait for session to be in a state where it can be accepted
        if (currentSession.value.state === 'Establishing') {
            console.log('Session still establishing, waiting to answer...')
            let waitAttempts = 0
            while (currentSession.value.state === 'Establishing' && waitAttempts < 10) {
                await new Promise(r => setTimeout(r, 200))
                waitAttempts++
            }
        }

        if (callState.value !== 'ringing') {
            console.warn('Cannot answer: Call state is not ringing', callState.value)
            return
        }

        console.log('Answering call... Session ID:', currentSession.value.id)

        try {
            const options = {
                sessionDescriptionHandlerOptions: {
                    constraints: { audio: true, video: false }
                }
            }

            // Wait for getUserMedia and SDP answer generation
            await currentSession.value.accept(options)

            console.log('Call accepted successfully, transitioning to active')
            callEstablished()
        } catch (e) {
            console.error('Error answering call (SDP/Media failure):', e)
        }
    }

    function hangupCall() {
        if (!currentSession.value) return

        const wasActive = callState.value === 'active'

        console.log('Hanging up...')
        switch (currentSession.value.state) {
            case 'Initial':
            case 'Establishing':
                if (currentSession.value.reject) currentSession.value.reject()
                else if (currentSession.value.cancel) currentSession.value.cancel()
                break
            case 'Established':
                if (currentSession.value.bye) currentSession.value.bye()
                break
            default:
                if (currentSession.value.bye) currentSession.value.bye()
                else if (currentSession.value.terminate) currentSession.value.terminate()
        }

        if (wasActive) {
            enterWrapup()
        } else {
            resetCall()
        }
    }

    // Called by SIP store when session terminates (remote hangup or BYE confirmed)
    function onCallTerminated() {
        // Don't override wrapup or idle states
        if (callState.value === 'wrapup' || callState.value === 'idle') return

        // Queue confirmation calls (Asterisk login handshake) should not trigger wrapup
        if (isQueueConfirmationCall) {
            isQueueConfirmationCall = false
            resetCall()
            return
        }

        if (callState.value === 'active') {
            enterWrapup()
        } else {
            resetCall()
        }
    }

    function enterWrapup() {
        console.log('[ActiveCall] Entering wrapup state')
        stopRingtone()
        stopTimer()
        currentSession.value = null
        callState.value = 'wrapup'
        hasAudioTrack.value = false
        // Keep callerNumber/callid for reference during wrapup
        // Auto-clear after 30 seconds
        if (wrapupTimer) clearTimeout(wrapupTimer)
        wrapupTimer = setTimeout(() => endWrapup(), 30000)
    }

    function endWrapup() {
        if (wrapupTimer) clearTimeout(wrapupTimer)
        wrapupTimer = null
        console.log('[ActiveCall] Wrapup ended')
        callState.value = 'idle'
        callerNumber.value = ''
        ssid.value = ''
        src_callid.value = ''
        src_uid.value = null
        // bridge_id is intentionally kept here — cleared by resetCall() on the next call.
        // This ensures catch-up fetches on case-creation can still match src_callid after wrapup expires.
        startedAt.value = null
        durationSeconds.value = 0
        // Don't clear aiInsights here — insights arrive AFTER call ends (20-120s processing)
        // and the user may still be on the case-creation page. Cleared on next call via resetCall().
    }

    function resetCall() {
        stopRingtone()
        stopTimer()
        isQueueConfirmationCall = false
        currentSession.value = null
        callState.value = 'idle'
        callerNumber.value = ''
        ssid.value = ''
        src_callid.value = ''
        src_uid.value = null
        bridge_id.value = ''
        lastCallUniqueId.value = ''
        startedAt.value = null
        durationSeconds.value = 0
        hasAudioTrack.value = false
        clearAiInsights()
    }

    function startTimer() {
        stopTimer()
        durationSeconds.value = 0
        timerInterval = setInterval(() => {
            durationSeconds.value++
        }, 1000)
    }

    function stopTimer() {
        if (timerInterval) clearInterval(timerInterval)
        timerInterval = null
    }

    function setAmiUniqueId(uid) {
        src_uid.value = uid
        if (uid) lastCallUniqueId.value = uid // Overwrite fallback with accurate CHAN_UNIQUEID
    }

    function setBridgeId(id) {
        if (id && id !== bridge_id.value) {
            console.log('[ActiveCall] Bridge ID set:', id)
            bridge_id.value = id
        }
    }

    function addAiInsight(payload) {
        if (!payload || !payload.notification_type) return
        // Dedup by notification_type + call_id from payload metadata (survives wrapup state clear)
        const callId = payload.call_metadata?.call_id || bridge_id.value || src_uid.value || ''
        const dedupKey = `${payload.notification_type}:${callId}`
        if (_seenInsightTypes.has(dedupKey)) return
        _seenInsightTypes.add(dedupKey)
        console.log('[ActiveCall] AI Insight added:', payload.notification_type)
        aiInsights.value.push(payload)
    }

    function clearAiInsights() {
        aiInsights.value = []
        _seenInsightTypes.clear()
    }

    function formatDuration(seconds) {
        const mins = Math.floor(seconds / 60)
        const secs = seconds % 60
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }

    // ── Server-side queue sync via AMI channel data ─────────────────
    // Periodically checks the AMI realtime store to detect when the agent
    // is removed from the queue externally (e.g., by a supervisor or legacy UI).
    // AMI queue member entries have UniqueIDs ending in "-mbr" with context
    // "agentlogin" and event "mbradd". The isExtensionInQueue getter in
    // the realtime store matches these entries via CHAN_EXTEN.
    let queueSyncTimer = null
    let consecutiveMisses = 0
    const MISS_THRESHOLD = 3
    const SYNC_INTERVAL = 10000 // 10 seconds

    async function getAgentExtension() {
        const authStore = (await import('./auth')).useAuthStore()
        const sipStore = (await import('./sip')).useSipStore()
        return authStore.profile?.extension || authStore.profile?.exten || sipStore.extension
    }

    function startQueueSync() {
        if (queueSyncTimer) return

        console.log('[Queue Sync] Starting AMI-based queue state sync')
        consecutiveMisses = 0

        queueSyncTimer = setInterval(async () => {
            if (queueStatus.value !== 'online') {
                stopQueueSync()
                return
            }

            const ext = await getAgentExtension()
            if (!ext) return

            try {
                const realtimeStore = (await import('./realtime')).useRealtimeStore()

                // Skip check if AMI WebSocket is not connected
                if (!realtimeStore.isAmiConnected) return

                const isPresent = realtimeStore.isExtensionInQueue(ext)

                if (!isPresent) {
                    consecutiveMisses++
                    console.log(`[Queue Sync] Extension ${ext} not in AMI data (miss ${consecutiveMisses}/${MISS_THRESHOLD})`)
                    if (consecutiveMisses >= MISS_THRESHOLD) {
                        console.log(`[Queue Sync] Extension ${ext} not found in AMI for ${consecutiveMisses} checks — marking offline`)
                        setQueueStatus('offline')
                        stopQueueSync()
                    }
                } else {
                    if (consecutiveMisses > 0) {
                        console.log(`[Queue Sync] Extension ${ext} found in AMI — resetting miss counter`)
                    }
                    consecutiveMisses = 0
                }
            } catch (e) {
                // Error — don't count as miss
            }
        }, SYNC_INTERVAL)
    }

    function stopQueueSync() {
        if (queueSyncTimer) {
            console.log('[Queue Sync] Stopping AMI-based queue state sync')
            clearInterval(queueSyncTimer)
            queueSyncTimer = null
            consecutiveMisses = 0
        }
    }


    // Queue status persistence
    const queueStatus = ref(localStorage.getItem('queueStatus') || 'offline') // 'offline' | 'online'
    const setQueueStatus = (status) => {
        console.log(`[Queue Status Change] ${queueStatus.value} -> ${status}`)
        queueStatus.value = status
        localStorage.setItem('queueStatus', status)
    }

    async function joinQueue() {
        // Guard against duplicate joins (e.g., SIP onRegistered re-triggering)
        if (queueStatus.value === 'online' || queueStatus.value === 'joining') {
            console.log('[ActiveCall] Already', queueStatus.value, '— skipping duplicate joinQueue')
            startQueueSync() // Ensure sync is running even on re-init
            return true
        }

        try {
            const authStore = (await import('./auth')).useAuthStore()
            const sipStore = (await import('./sip')).useSipStore()

            // Ensure SIP is registered BEFORE telling Asterisk to join queue.
            // Asterisk sends a confirmation INVITE immediately — SIP must be ready to receive it.
            if (!sipStore.isRegistered) {
                if (!sipStore.isConnected && !sipStore.isRegistering) {
                    await sipStore.start()
                }
                // Wait for registration to complete (up to 5 seconds)
                let attempts = 0
                while (!sipStore.isRegistered && attempts < 20) {
                    await new Promise(r => setTimeout(r, 250))
                    attempts++
                }
                if (!sipStore.isRegistered) {
                    throw new Error('SIP registration failed. Cannot join queue without voice connection.')
                }
            }

            let ext = authStore.profile?.extension || authStore.profile?.exten || sipStore.extension
            if (!ext) {
                try { ext = await sipStore.fetchExtension() } catch (e) { }
            }

            if (!ext) {
                throw new Error('No extension assigned to your account.')
            }

            // Warm up audio context on user click
            initRingtone()

            setQueueStatus('joining')
            awaitingQueueConfirmation.value = true

            console.log('[ActiveCall] SIP registered, sending join queue to Asterisk...')
            const payload = { action: '1' }

            const response = await axiosInstance.post('api/agent/', payload)

            if (response.status === 200 || response.status === 203) {
                setQueueStatus('online')
                startQueueSync()
            } else {
                setQueueStatus('offline')
            }

            return true
        } catch (e) {
            console.error("Queue join failed:", e.message)
            awaitingQueueConfirmation.value = false
            setQueueStatus('offline')
            throw e
        }
    }

    async function leaveQueue() {
        awaitingQueueConfirmation.value = false
        try {
            const authStore = (await import('./auth')).useAuthStore()
            const sipStore = (await import('./sip')).useSipStore()

            let ext = authStore.profile?.extension || authStore.profile?.exten || sipStore.extension
            if (!ext) {
                try { ext = await sipStore.fetchExtension() } catch (e) { }
            }

            const payload = {
                action: '0',
                break: 'logout'
            }

            await axiosInstance.post('api/agent/', payload)

            setQueueStatus('offline')
            stopQueueSync()

        } catch (e) {
            console.error('Queue leave failed', e.message)
        }
    }

    function getFriendlyErrorMessage(err) {
        if (err.message?.includes('timeout') || err.code === 'ECONNABORTED') {
            return 'Server is taking too long to respond. Please check your connection and try again.'
        }
        if (err.response?.status === 401) {
            return 'Your session has expired. Please log out and back in.'
        }
        if (err.message?.includes('extension')) {
            return err.message
        }
        return 'An unexpected error occurred. Please try again or contact support.'
    }

    function resetQueueState() {
        stopQueueSync()
        setQueueStatus('offline')
    }

    function initializeQueue() {
        if (queueStatus.value === 'online') {
            // Re-join queue (which will also start sync on success)
            joinQueue().catch(() => { })
        }
    }

    return {
        currentSession,
        callState,
        callerNumber,
        ssid,
        src_callid,
        src_uid,
        bridge_id,
        aiInsights,
        lastCallUniqueId,
        startedAt,
        durationSeconds,
        hasAudioTrack,
        formatDuration,
        queueStatus,
        joinQueue,
        leaveQueue,
        setQueueStatus,

        onIncomingCall,
        startOutboundCall,
        callEstablished,
        answerCall,
        hangupCall,
        resetCall,
        onCallTerminated,
        endWrapup,
        setAmiUniqueId,
        setBridgeId,
        addAiInsight,
        clearAiInsights,
        autoAnswerEnabled,
        awaitingQueueConfirmation,
        toggleAutoAnswer,
        initializeQueue,
        resetQueueState
    }
})

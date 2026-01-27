import { defineStore } from 'pinia'
import axiosInstance from '@/utils/axios'
import { computed, ref } from 'vue'

export const useActiveCallStore = defineStore('activeCall', () => {
    // State
    const currentSession = ref(null)
    const callState = ref('idle') // idle, ringing, active, ended
    const callerNumber = ref('')
    const ssid = ref('')
    const src_callid = ref('')
    const src_uid = ref(null) // AMI CHAN_UNIQUEID
    const startedAt = ref(null)
    const durationSeconds = ref(0)
    const hasAudioTrack = ref(false)
    const autoAnswerEnabled = ref(localStorage.getItem('sip_auto_answer') === 'true')

    function toggleAutoAnswer() {
        autoAnswerEnabled.value = !autoAnswerEnabled.value
        localStorage.setItem('sip_auto_answer', autoAnswerEnabled.value)
    }

    let timerInterval = null
    let pollInterval = null

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

        console.error('[ActiveCall] POPUP STATE SHOULD NOW BE RINGING');

        /* Disable auto-answer during diagnosis to ensure popup remains visible 
        if (autoAnswerEnabled.value) {
            console.log('Auto-Answering enabled, answering in 500ms...')
            setTimeout(() => answerCall(), 500)
        }
        */
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

        console.log('Hanging up...')
        // Check state to decide between reject (if ringing) or bye (if active)
        // SIP.js session.state might be used, or our local state

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
                // Try bye/terminate anyway
                if (currentSession.value.bye) currentSession.value.bye()
                else if (currentSession.value.terminate) currentSession.value.terminate()
        }

        resetCall()
    }

    function resetCall() {
        stopTimer()
        currentSession.value = null
        callState.value = 'idle'
        callerNumber.value = ''
        ssid.value = ''
        src_callid.value = ''
        src_uid.value = null
        startedAt.value = null
        durationSeconds.value = 0
        hasAudioTrack.value = false
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
    }

    function formatDuration(seconds) {
        const mins = Math.floor(seconds / 60)
        const secs = seconds % 60
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }

    // Polling logic for live status and UniqueID identification
    function startPollingLiveStatus(extension) {
        if (pollInterval) return
        console.log('[ActiveCall] Starting live status polling for exten:', extension)

        pollInterval = setInterval(async () => {
            if (queueStatus.value !== 'online') {
                stopPollingLiveStatus()
                return
            }

            try {
                // Poll the wallonly endpoint as requested
                const { data } = await axiosInstance.get('api/wallonly/', {
                    params: { exten: extension, _c: 5 } // Fetch live entries
                })

                if (data.live && data.live.length > 0) {
                    const k = data.live_k
                    const liveAgents = data.live

                    // Veracity check: Is the current extension in the live list?
                    const extIdx = k.exten?.[0] ?? k.extension?.[0] ?? -1
                    if (extIdx !== -1) {
                        const isPresent = liveAgents.some(row => String(row[extIdx]) === String(extension))
                        if (isPresent) {
                            console.info(`[Queue] VERIFIED: Extension ${extension} is actively present in the server's live queue.`);

                            // Phase 5 - AMI Peer State Verification
                            try {
                                const { data: amiData } = await axiosInstance.get('ami/svrts?c=-2');
                                // console.error("AMI peer state snippet:", JSON.stringify(amiData).substring(0, 200));
                            } catch (amiErr) {
                                console.warn("AMI verification failed:", amiErr.message);
                            }
                        } else {
                            console.error(`[Queue] WARNING: Your extension ${extension} is NOT found in the server's active agents list despite being 'Online' in UI.`);
                        }
                    }

                    const call = data.live[0]
                    if (call && k) {
                        // Identify indices
                        const uidIdx = k.uniqueid?.[0] ?? k.id?.[0] ?? 0
                        const callerIdx = k.caller_id?.[0] ?? k.phone?.[0] ?? 1

                        const uniqueid = call[uidIdx]
                        const remoteNumber = call[callerIdx]

                        // If we are in ringing/active/calling, sync the uniqueid
                        if (['ringing', 'active', 'calling'].includes(callState.value)) {
                            if (!src_uid.value && uniqueid) {
                                console.log('[ActiveCall] Syncing live call UniqueID:', uniqueid)
                                src_uid.value = uniqueid
                            }
                        }

                        // Fallback: If we detect a call in wallboard but SIP hasn't fired yet
                        // (Usually wallboard is slightly ahead or bypasses SIP WebSocket delays)
                        /* 
                        if (callState.value === 'idle' && uniqueid) {
                             // potential for auto-trigger if needed, 
                             // but we usually prefer SIP for actual media
                        }
                        */
                    }
                }
            } catch (e) {
                console.warn('[ActiveCall] Live polling failed:', e)
            }
        }, 3000)
    }

    function stopPollingLiveStatus() {
        if (pollInterval) {
            console.log('[ActiveCall] Stopping live status polling')
            clearInterval(pollInterval)
            pollInterval = null
        }
    }

    // Queue status persistence
    const queueStatus = ref(localStorage.getItem('queueStatus') || 'offline') // 'offline' | 'online'
    const setQueueStatus = (status) => {
        console.log(`[Queue Status Change] ${queueStatus.value} -> ${status}`)
        queueStatus.value = status
        localStorage.setItem('queueStatus', status)
    }

    async function checkWallboard(ext) {
        try {
            const { data } = await axiosInstance.get('api/wallonly/', {
                params: { exten: ext, _c: 1 }
            })
            return data
        } catch (e) {
            // silent check
        }
    }

    async function joinQueue() {
        try {
            const authStore = (await import('./auth')).useAuthStore()
            const sipStore = (await import('./sip')).useSipStore()

            // Trigger SIP registration if not already active
            if (!sipStore.isConnected && !sipStore.isRegistering) {
                sipStore.start().catch(err => {
                    console.error('[Helper] SIP auto-start check:', err)
                })
            }

            let ext = authStore.profile?.extension || authStore.profile?.exten || sipStore.extension
            if (!ext) {
                try { ext = await sipStore.fetchExtension() } catch (e) { }
            }

            if (!ext) {
                throw new Error('No extension assigned to your account.')
            }

            setQueueStatus('joining')

            // Authoritative payload: Only action "1"
            const payload = { action: '1' }

            const response = await axiosInstance.post('api/agent/', payload)

            if (response.status === 200 || response.status === 203) {
                setQueueStatus('online')
                // Immediate validation
                await checkWallboard(ext)
            } else {
                setQueueStatus('offline')
            }

            return true
        } catch (e) {
            console.error("Queue join failed:", e.message)
            setQueueStatus('offline')
            throw e
        }
    }

    async function leaveQueue() {
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
            stopPollingLiveStatus()

            // Immediate validation
            if (ext) await checkWallboard(ext)

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
        setQueueStatus('offline')
    }

    function initializeQueue() {
        if (queueStatus.value === 'online') {
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
        setAmiUniqueId,
        autoAnswerEnabled,
        toggleAutoAnswer,
        initializeQueue,
        resetQueueState
    }
})

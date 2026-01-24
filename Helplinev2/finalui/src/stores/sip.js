import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import * as SIP from 'sip.js'
import { config, getSipConfig } from '@/config/sip'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/users'
import { useActiveCallStore } from '@/stores/activeCall'

export const useSipStore = defineStore('sip', () => {
    // State
    const ua = ref(null)
    const registerer = ref(null)
    const status = ref('disconnected') // disconnected, connecting, connected, registered, error
    const error = ref(null)
    const extension = ref(null)
    const autoAnswer = ref(false)
    const isEnabled = ref(localStorage.getItem('sipEnabled') === 'true') // Persistent intent
    const isRegistering = ref(false)
    const uaInstanceId = ref(Math.random().toString(36).substring(7))

    // Stores
    const authStore = useAuthStore()
    const userStore = useUserStore()
    const activeCallStore = useActiveCallStore()

    // Computed
    const isRegistered = computed(() => status.value === 'registered')
    const isConnected = computed(() => status.value === 'connected' || status.value === 'registered')

    // Actions
    async function fetchExtension() {
        // console.log('[SIP Store] Fetching extension for user:', authStore.userId)
        try {
            const userId = authStore.userId
            if (!userId) throw new Error('User ID not found')

            const userData = await userStore.viewUser(userId)
            // console.log('[SIP Store] User data received:', userData)

            const user = userData?.users?.[0]
            const keys = userData?.users_k || {}

            const extenIdx = keys.exten?.[0]

            if (!user || extenIdx === undefined || !user[extenIdx]) {
                throw new Error('No extension assigned to your account. Please contact your supervisor to configure your telephony settings.')
            }

            extension.value = user[extenIdx]

            // Note: System uses shared secret for all extensions.

            return extension.value
        } catch (err) {
            console.error('[SIP Store] Error fetching extension:', err)
            error.value = err.message
            throw err
        }
    }

    async function start() {
        if (ua.value) {
            if (!isRegistered.value && registerer.value) {
                console.log('[SIP Store] UA exists but not registered. Retrying registration...')
                try {
                    status.value = 'connecting'
                    await registerer.value.register()
                } catch (e) {
                    console.error('[SIP Store] Re-registration failed:', e)
                }
            }
            return
        }
        try {
            isEnabled.value = true
            localStorage.setItem('sipEnabled', 'true')
            status.value = 'connecting'
            isRegistering.value = true
            error.value = null

            if (!extension.value) {
                await fetchExtension()
            }

            // console.log(`[SIP Store] Starting UA for extension: ${extension.value}`)
            const passToUse = null // Global secret
            // console.log(`[SIP Store] Using Password: GLOBAL SECRET (starts with 23k...)`) 

            const uri = SIP.UserAgent.makeURI(config.buildSipUri(extension.value))
            if (!uri) throw new Error('Invalid SIP URI configuration')

            // AUTHENTICATION LOGIC:
            // Profile has no password field, so we default to Global Secret.
            // On Demo server, Auth User is likely the Extension ('100'), not the Web User ('test').
            const password = null // Defaults to Global Secret
            const authUser = extension.value // Reverting to extension based auth

            console.log('🔐 [SIP DEBUG] Credentials Used:', {
                extension: extension.value,
                authorizationUsername: authUser,
                password: password ? 'User Profile Secret' : (config.SIP_PASSWORD || '23kdefrtgos09812100'),
                server: config.SIP_WS_URL
            })

            const sipConfig = getSipConfig(extension.value, {
                onInvite: (invitation) => handleIncomingCall(invitation)
            }, password)

            // Explicitly set Auth User
            sipConfig.authorizationUsername = authUser

            sipConfig.uri = uri

            ua.value = new SIP.UserAgent(sipConfig)

            // Explicitly set delegate to ensure onInvite is captured
            ua.value.delegate = {
                onInvite: (invitation) => handleIncomingCall(invitation)
            }

            // Transport events
            ua.value.transport.onConnect = () => {
                console.log('[SIP Store] WebSocket Connected')
                status.value = 'connected'
            }

            ua.value.transport.onDisconnect = (err) => {
                console.warn('[SIP Store] WebSocket Disconnected', err)
                status.value = 'disconnected'
                if (err) error.value = 'Connection lost'
            }

            try {
                await ua.value.start()
            } catch (wsErr) {
                console.warn('[SIP Store] WS Connection failed:', wsErr)
                status.value = 'error'
                error.value = 'Voice server unreachable. Click to retry.'

                // CRITICAL: Destroy the failed UA so we can try again from scratch next time
                ua.value = null
                isEnabled.value = false
                throw new Error('Connection failed')
            }

            // console.log('[SIP Store] UA Started, initializing Registerer...')

            // Registerer
            registerer.value = new SIP.Registerer(ua.value, {
                delegate: {
                    onRegistered: () => {
                        console.log('[SIP Store] Registered successfully')
                        status.value = 'registered'
                    },
                    onRegistrationFailed: (response) => {
                        const code = response?.statusCode
                        const reason = response?.reasonPhrase
                        console.error('[SIP Store] Registration failed:', code, reason);

                        let msg = `Registration failed (${code})`
                        if (code === 401 || code === 403) {
                            msg = 'Authentication failed. Checking credentials...'
                        } else if (code === 408) {
                            msg = 'Registration timed out. Server not responding.'
                        } else if (code >= 500) {
                            msg = 'Server error. Please try again later.'
                        }

                        error.value = msg
                        status.value = 'error'
                    }
                }
            })

            registerer.value.stateChange.addListener((newState) => {
                console.log('[SIP Store] Registerer State:', newState)
                if (newState === SIP.RegistererState.Registered) {
                    // Clear any previous errors on success
                    error.value = null
                    status.value = 'registered'
                    isRegistering.value = false
                    localStorage.setItem('sipConnected', 'true')

                    const activeCallStore = useActiveCallStore()
                    if (activeCallStore.queueStatus === 'online') {
                        activeCallStore.joinQueue()
                    }
                } else if (newState === SIP.RegistererState.Unregistered) {
                    // If we were trying to register and ended up Unregistered, it's a failure
                    if (isRegistering.value) {
                        console.warn('[SIP Store] Registration rejected (Silent Failure)')
                        status.value = 'error'
                        error.value = 'Registration rejected. Check credentials.'
                    } else {
                        status.value = 'connected'
                    }
                    isRegistering.value = false
                } else if (newState === SIP.RegistererState.Terminated) {
                    status.value = 'connected'
                    isRegistering.value = false
                }
            })

            // console.log(`[SIP Store] Registering extension: ${extension.value}`)
            await registerer.value.register()
            // console.log('[SIP Store] Registration request sent.')

            // Auto-start if persisted
            if (localStorage.getItem('sipConnected') === 'true') {
                // console.log('[SIP Store] Restoring persisted SIP connection')
            }

        } catch (err) {
            // console.error('[SIP Store] Failed to start:', err)
            status.value = 'error'

            // Map to friendly message
            let msg = err.message || 'Failed to start SIP agent'
            if (msg.includes('timeout') || msg.includes('ECONNABORTED')) {
                msg = 'Connection to voice server timed out. Please check your network.'
            } else if (msg.includes('401') || msg.includes('Unauthorized')) {
                msg = 'Authentication failed. Please verify your extension settings.'
            }

            error.value = msg
            isEnabled.value = false
            throw new Error(msg)
        }
    }

    async function stop() {
        if (!ua.value) return

        try {
            if (registerer.value) {
                await registerer.value.unregister()
                registerer.value = null
            }
            await ua.value.stop()
            ua.value = null
            status.value = 'disconnected'
            isEnabled.value = false
            isRegistering.value = false
            localStorage.removeItem('sipEnabled')
            localStorage.removeItem('sipConnected')
        } catch (err) {
            // console.error('[SIP Store] Error stopping:', err)
        }
    }

    function handleIncomingCall(invitation) {
        invitation.stateChange.addListener((state) => {
            // console.error('[SIP Store] Session state changed:', state)
            if (state === SIP.SessionState.Established) {
                activeCallStore.callEstablished()
            } else if (state === SIP.SessionState.Terminated) {
                activeCallStore.resetCall()
            }
        })

        // Notify activeCallStore
        activeCallStore.onIncomingCall(invitation)
    }

    async function makeCall(targetDetails) {
        if (!ua.value || !isRegistered.value) {
            throw new Error('SIP Agent not connected')
        }

        let number = typeof targetDetails === 'string' ? targetDetails : targetDetails.number
        // Sanitize: remove whitespace, dashes, parens
        number = number.replace(/[\s\-\(\)]/g, '')

        console.log('[SIP Store] Dialing sanitized number:', number)

        try {
            const target = SIP.UserAgent.makeURI(`sip:${number}@${config.SIP_HOST}`)
            if (!target) throw new Error('Invalid target URI after sanitization')

            const inviter = new SIP.Inviter(ua.value, target, {
                sessionDescriptionHandlerOptions: {
                    constraints: { audio: true, video: false }
                }
            })

            // Notify activeCallStore
            activeCallStore.startOutboundCall(inviter)

            // Listen for state changes
            inviter.stateChange.addListener((state) => {
                // console.log('[SIP Store] Outbound session state:', state)
                if (state === SIP.SessionState.Established) {
                    activeCallStore.callEstablished()
                } else if (state === SIP.SessionState.Terminated) {
                    activeCallStore.resetCall()
                }
            })

            await inviter.invite()
            return inviter
        } catch (err) {
            // console.error('[SIP Store] Call failed:', err)
            throw err
        }
    }

    function sendDtmf(session, digit) {
        if (!session) return
        // console.log('[SIP Store] Sending DTMF:', digit)
        const options = {
            requestOptions: {
                body: {
                    contentDisposition: 'render',
                    contentType: 'application/dtmf-relay',
                    content: `Signal=${digit}\r\nDuration=100`
                }
            }
        }
        session.info(options)
    }

    return {
        ua,
        registerer,
        status,
        error,
        extension,
        autoAnswer,
        isEnabled,
        isRegistering,
        isRegistered,
        isConnected,
        start,
        stop,
        makeCall,
        sendDtmf,
        fetchExtension
    }
})

import { ref } from 'vue'
import * as SIP from 'sip.js'
import { useActiveCallStore } from '@/stores/activeCall'
import { useAuthStore } from '@/stores/auth'
import { useUserStore } from '@/stores/users'

let userAgent = null
let registerer = null
const audioElement = new Audio() // Remote audio

export function useWebRtcClient() {
    const isRegistered = ref(false)
    const isConnected = ref(false)

    const activeCallStore = useActiveCallStore()
    const authStore = useAuthStore()

    const init = async () => {
        if (userAgent) return // Already initialized

        // Credentials
        // We assume extension is available. Password might be needed.
        let extension = authStore.user?.extension || authStore.profile?.extension || authStore.profile?.exten
        let password = authStore.user?.secret || authStore.profile?.secret || authStore.profile?.password || 'Starten1' // Fallback/Placeholder
        const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
        // Hardcode domain to localhost (no port) for dev environment SIP consistency
        const domain = 'localhost'
        const wsServer = `${protocol}://${window.location.host}/ws/`

        console.log('[SIP-DEBUG] Using SIP Domain:', domain, 'WS Server:', wsServer)

        // Check if extension is missing but we have a user ID (e.g. after refresh)
        if (!extension && authStore.userId) {
            console.log('Extension missing, fetching user details for SIP init...')
            try {
                const userStore = useUserStore()
                // api/users/:id response structure investigation handling
                const data = await userStore.viewUser(authStore.userId)

                let fetchedProfile = {}

                // Helper to extract if it's the efficient format
                if (data.users && data.users_k) {
                    // It's the compact format
                    const k = data.users_k
                    const row = data.users[0]
                    if (row) {
                        fetchedProfile.extension = row[k.exten?.[0] || -1] || row[k.extension?.[0] || -1]
                        fetchedProfile.username = row[k.username?.[0] || -1] || row[k.name?.[0] || -1]
                        // Try multiple keys for secret
                        const secretIndex = k.secret?.[0] ?? k.password?.[0] ?? k.pass?.[0] ?? k.sip_secret?.[0] ?? -1
                        fetchedProfile.secret = row[secretIndex]
                    }
                } else {
                    // Maybe it's a direct object
                    fetchedProfile = data
                }

                // If we found an extension, update authStore
                if (fetchedProfile.extension || fetchedProfile.exten) {
                    const ext = fetchedProfile.extension || fetchedProfile.exten
                    const secret = fetchedProfile.secret || 'Starten1'

                    // Update store state
                    authStore.profile = {
                        ...authStore.profile,
                        extension: ext,
                        secret: secret,
                        username: fetchedProfile.username || authStore.username
                    }

                    // Update local vars
                    extension = ext
                    password = secret

                    // Persist for next time (matching auth store logic)
                    localStorage.setItem('user-profile', JSON.stringify(authStore.profile))
                    console.log('Profile fetched and updated:', authStore.profile)
                }
            } catch (e) {
                console.error('Failed to fetch user profile for SIP', e)
            }
        }

        if (!extension) {
            console.warn('No extension found, skipping SIP init')
            return
        }

        const uri = SIP.UserAgent.makeURI(`sip:${extension}@${domain}`)

        const transportOptions = {
            server: wsServer
        }

        userAgent = new SIP.UserAgent({
            uri,
            transportOptions,
            authorizationUsername: extension,
            authorizationPassword: password,
            delegate: {
                onConnect: () => {
                    isConnected.value = true
                    console.log('SIP Transport Connected')
                },
                onDisconnect: (error) => {
                    isConnected.value = false
                    isRegistered.value = false
                    console.log('SIP Transport Disconnected', error)
                    // Auto-reconnect logic is built-in to SIP.js UserAgent default behavior usually, 
                    // or we can attempt userAgent.reconnect()
                },
                onInvite: (invitation) => {
                    console.log('[SIP-DEBUG] SIP Invite Received', invitation)
                    console.log('[SIP-DEBUG] From:', invitation.remoteIdentity.uri.user)
                    handleIncomingCall(invitation)
                }
            }
        })

        await userAgent.start()

        // Register
        registerer = new SIP.Registerer(userAgent)

        // Setup registration state tracking
        registerer.stateChange.addListener((newState) => {
            if (newState === SIP.RegistererState.Registered) {
                isRegistered.value = true
            } else {
                isRegistered.value = false
            }
        })

        await registerer.register()
    }

    const stop = async () => {
        if (registerer) {
            await registerer.unregister()
            registerer = null
        }
        if (userAgent) {
            await userAgent.stop()
            userAgent = null
        }
    }

    const handleIncomingCall = (session) => {
        console.log('[SIP-DEBUG] Handling incoming call session...', session.id)
        // Setup media handling
        session.stateChange.addListener((newState) => {
            if (newState === SIP.SessionState.Established) {
                setupRemoteMedia(session)
            }
            if (newState === SIP.SessionState.Terminated) {
                activeCallStore.resetCall()
            }
        })

        activeCallStore.onIncomingCall(session)
    }

    const setupRemoteMedia = (session) => {
        const pc = session.sessionDescriptionHandler.peerConnection
        const remoteStream = new MediaStream()

        pc.getReceivers().forEach((receiver) => {
            if (receiver.track) {
                remoteStream.addTrack(receiver.track)
            }
        })

        audioElement.srcObject = remoteStream
        audioElement.play().catch(e => console.error('Audio play failed', e))
    }

    const invite = async (destination) => {
        if (!userAgent) {
            console.log('UserAgent not initialized, attempting init...')
            await init()
            if (!userAgent) {
                console.error('UserAgent failed to initialize')
                return
            }
        }

        const domain = window.location.hostname
        const target = SIP.UserAgent.makeURI(`sip:${destination}@${domain}`)
        if (!target) {
            console.error('Invalid target URI')
            return
        }

        const inviter = new SIP.Inviter(userAgent, target, {
            sessionDescriptionHandlerOptions: {
                constraints: { audio: true, video: false }
            }
        })

        // Setup similar event handling as incoming
        inviter.stateChange.addListener((newState) => {
            if (newState === SIP.SessionState.Established) {
                setupRemoteMedia(inviter)
                // Logic to update store state to 'active' would be good here or handled by the store listening to this session
                activeCallStore.callEstablished()
            }
            if (newState === SIP.SessionState.Terminated) {
                activeCallStore.resetCall()
            }
        })

        // Unlike incoming, we don't wait for 'onIncomingCall' to set the session.
        // We set it immediately as an outbound call.
        activeCallStore.startOutboundCall(inviter)

        await inviter.invite()
    }

    return {
        init,
        stop,
        invite,
        isRegistered,
        isConnected
    }
}

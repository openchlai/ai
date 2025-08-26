// src/utils/sipClient.js
import JsSIP from 'jssip';

// Global SIP variables
let ua = null; // User Agent
let activeSession = null; // Ongoing call session
let incomingSession = null; // Incoming call session
let eventListeners = {}; // Registered event handlers
let isInQueue = false; // Queue registration status
let iceServers = [ // Default ICE servers
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' }
];

/**
 * Initializes the SIP client using JsSIP and sets up the WebSocket connection.
 * Handles basic transport-level errors.
 */
export function initSIP({ Desc, sipUri, password, websocketURL, debug = false }) {
    try {
        const connectionDetails = { Desc, sipUri, password, websocketURL, debug };
        console.log('Initializing SIP with:', connectionDetails);

        if (!sipUri || !password || !websocketURL) {
            throw new Error('Missing required SIP connection parameters');
        }

        const socket = new JsSIP.WebSocketInterface(websocketURL, {
            useSipCreds: true,
            connectionTimeout: 10000,
            maxReconnectionAttempts: 5,
            reconnectionTimeout: 10000,
            binaryType: 'arraybuffer',
            keepAliveInterval: 30000
        });

        const config = {
            sockets: [socket],
            uri: sipUri,
            password: password,
            realm: '172.31.11.85'
        };

        ua = new JsSIP.UA(config);

        // Listen for transport errors
        ua.on('transportError', (error) => {
            console.error('Transport Error:', error);
            eventListeners['onTransportError']?.(error);
        });

        return true;
    } catch (error) {
        console.error('SIP Init Failed:', error);
        setTimeout(() => initSIP({ sipUri, password, websocketURL, debug }), 5000);
        throw error;
    }
}

/**
 * Registers the user agent and joins a call queue, optionally with a queue number.
 */
export function joinQueue(queueNumber = '') {
    if (!ua) throw new Error('SIP client not initialized');

    const options = {
        extraHeaders: queueNumber ? [`X-Queue: ${queueNumber}`] : []
    };

    ua.register(options)
        .then(() => {
            isInQueue = true;
            console.log('Joined queue successfully');
            eventListeners['onQueueJoined']?.();
        })
        .catch(error => {
            console.error('Failed to join queue:', error);
            eventListeners['onQueueJoinFailed']?.(error);
            throw error;
        });
}

/**
 * Unregisters the user agent and leaves the call queue.
 */
export function leaveQueue() {
    if (!ua) throw new Error('SIP client not initialized');

    ua.unregister()
        .then(() => {
            isInQueue = false;
            console.log('Left queue successfully');
            eventListeners['onQueueLeft']?.();
        })
        .catch(error => {
            console.error('Failed to leave queue:', error);
            eventListeners['onQueueLeaveFailed']?.(error);
            throw error;
        });
}

/**
 * Answers an incoming SIP call with predefined media constraints.
 */
export function answerCall() {
    if (!incomingSession) throw new Error('No incoming call to answer');

    const options = {
        mediaConstraints: { audio: true, video: false },
        pcConfig: { iceServers, iceTransportPolicy: 'all' },
        rtcConstraints: { optional: [{ googDscp: true }] },
        rtcOfferConstraints: { offerToReceiveAudio: true, offerToReceiveVideo: false }
    };

    incomingSession.answer(options);
    activeSession = incomingSession;
    incomingSession = null;
    console.log('Call answered successfully');
    eventListeners['onCallAnswered']?.(activeSession);
}

/**
 * Rejects the current incoming SIP call.
 */
export function rejectCall() {
    if (!incomingSession) throw new Error('No incoming call to reject');

    incomingSession.terminate({
        status_code: 486,
        reason_phrase: 'Busy Here'
    });

    incomingSession = null;
    console.log('Call rejected successfully');
    eventListeners['onCallRejected']?.();
}

/**
 * Terminates the current active call session.
 */
export function hangupCall() {
    if (!activeSession) throw new Error('No active call to hang up');

    activeSession.terminate();
    activeSession = null;
    console.log('Call ended successfully');
    eventListeners['onCallEnded']?.();
}

/**
 * Mutes or unmutes the audio track of the active call.
 */
export function muteCall(mute = true) {
    if (!activeSession) throw new Error('No active call to mute');

    const audioTrack = activeSession.connection.getSenders()
        .find(sender => sender.track.kind === 'audio');

    if (audioTrack) {
        audioTrack.track.enabled = !mute;
        console.log(mute ? 'Call muted' : 'Call unmuted');
        eventListeners['onCallMuted']?.(mute);
    }
}

/**
 * Sends a DTMF tone (e.g., 1-9, *, #) during an active call.
 */
export function sendDTMF(tone, duration = 100, interToneGap = 500) {
    if (!activeSession) throw new Error('No active call to send DTMF');

    activeSession.sendDTMF(tone, { duration, interToneGap });
    console.log('DTMF tone sent:', tone);
    eventListeners['onDTMFSent']?.(tone);
}

/**
 * Returns the current SIP call and registration status.
 */
export function getCallStatus() {
    const status = {
        isInCall: !!activeSession,
        hasIncomingCall: !!incomingSession,
        isInQueue,
        isRegistered: ua?.isRegistered() || false,
        registrationState: ua?.registrationState || 'unregistered',
        connectionState: ua?.connectionState || 'disconnected'
    };

    if (activeSession) {
        status.callDirection = activeSession.direction;
        status.remoteIdentity = activeSession.remote_identity.display_name || activeSession.remote_identity.uri.toString();
        status.startTime = activeSession.start_time;
        status.isMuted = isCallMuted();
    }

    return status;
}

/**
 * Checks if the active call is currently muted.
 */
function isCallMuted() {
    if (!activeSession) return false;
    const audioTrack = activeSession.connection.getSenders()
        .find(sender => sender.track.kind === 'audio');
    return audioTrack ? !audioTrack.track.enabled : false;
}

/**
 * Registers an event listener callback.
 */
export function on(event, callback) {
    if (typeof callback !== 'function') {
        throw new Error('Callback must be a function');
    }
    eventListeners[event] = callback;
}

/**
 * Unregisters an event listener.
 */
export function off(event) {
    delete eventListeners[event];
}

/**
 * Sets up SIP call event listeners on a session.
 */
function setupCallEvents(session) {
    session.on('progress', data => eventListeners['onCallProgress']?.(session, data));
    session.on('accepted', data => eventListeners['onCallAccepted']?.(session, data));
    session.on('confirmed', data => eventListeners['onCallConfirmed']?.(session, data));
    session.on('ended', data => {
        if (session === activeSession) activeSession = null;
        if (session === incomingSession) incomingSession = null;
        eventListeners['onCallEnded']?.(session, data);
    });
    session.on('failed', data => {
        if (session === activeSession) activeSession = null;
        if (session === incomingSession) incomingSession = null;
        eventListeners['onCallFailed']?.(session, data);
    });
    session.on('peerconnection', data => eventListeners['onPeerConnection']?.(session, data));
    session.on('sending', data => eventListeners['onMediaSending']?.(session, data));
    session.on('addstream', data => eventListeners['onRemoteStreamAdded']?.(session, data));
    session.on('icecandidate', data => eventListeners['onIceCandidate']?.(session, data));
    session.on('iceconnectionstatechange', data => eventListeners['onIceStateChange']?.(session, data));
}

/**
 * Transfers the current call to another SIP extension.
 * Supports both blind and attended transfer modes.
 */
export function transferCall(targetExtension, isBlind = true) {
    if (!activeSession || !activeSession.isEstablished()) {
        throw new Error('No active call to transfer');
    }

    const domain = ua.configuration.uri.split('@')[1];
    const targetUri = `sip:${targetExtension}@${domain}`;

    if (isBlind) {
        activeSession.terminate({
            status_code: 302,
            reason_phrase: 'Moved Temporarily',
            extraHeaders: [`Refer-To: <${targetUri}>`]
        });
    } else {
        activeSession.refer(targetUri);
    }

    console.log(`Call transferred to ${targetExtension} (${isBlind ? 'blind' : 'attended'})`);
    eventListeners['onCallTransferred']?.(targetExtension, isBlind);
}

/**
 * Cleans up SIP sessions and unregisters the user agent.
 */
export function cleanup() {
    try {
        if (activeSession) {
            activeSession.terminate();
            activeSession = null;
        }

        if (incomingSession) {
            incomingSession.terminate();
            incomingSession = null;
        }

        if (ua) {
            ua.unregister()
                .then(() => ua.stop())
                .catch(err => console.error('Error during cleanup:', err));
            ua = null;
        }

        isInQueue = false;
        eventListeners = {};
        console.log('SIP client cleaned up successfully');
    } catch (error) {
        console.error('Error during cleanup:', error);
        throw error;
    }
}

/**
 * Initiates a new outgoing SIP call to a given target.
 */
export function makeCall(target, options = {}) {
    if (!ua) throw new Error('SIP client not initialized');

    const domain = ua.configuration.uri.split('@')[1];
    const targetUri = target.includes('@') ? target : `sip:${target}@${domain}`;

    const callOptions = {
        mediaConstraints: { audio: true, video: false },
        pcConfig: { iceServers, iceTransportPolicy: 'all' },
        rtcConstraints: { optional: [{ googDscp: true }] },
        rtcOfferConstraints: { offerToReceiveAudio: true, offerToReceiveVideo: false },
        ...options
    };

    const session = ua.call(targetUri, callOptions);
    activeSession = session;
    setupCallEvents(session);
    console.log('Outgoing call initiated to:', target);
    return session;
}

/**
 * Updates the ICE server list used for WebRTC connections.
 */
export function updateIceServers(newIceServers) {
    if (!Array.isArray(newIceServers)) {
        throw new Error('ICE servers must be an array');
    }
    iceServers = newIceServers;
    console.log('ICE servers updated:', iceServers);
}

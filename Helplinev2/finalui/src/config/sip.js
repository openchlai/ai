/**
 * SIP/WebRTC Configuration Module
 *
 * Centralizes all SIP-related configuration and provides helpers
 * for WebRTC setup including STUN/TURN servers.
 */

// Get environment variables with fallbacks
const SIP_HOST = import.meta.env.VITE_SIP_HOST || 'demo-openchs.bitz-itc.com';
const SIP_WS_URL = import.meta.env.VITE_SIP_WS_URL || `wss://${SIP_HOST}/ws/`;
const SIP_PASSWORD = import.meta.env.VITE_SIP_PASSWORD || '23kdefrtgos09812100';
const SIP_CALL_TIMEOUT = parseInt(import.meta.env.VITE_SIP_CALL_TIMEOUT || '30000', 10);

// AMI WebSocket configuration
const AMI_WS_URL = import.meta.env.VITE_AMI_WS_URL || `wss://${SIP_HOST}:8384/ami/sync`;

// STUN/TURN configuration
const STUN_SERVERS = import.meta.env.VITE_STUN_SERVERS || 'stun:stun.l.google.com:19302,stun:stun1.l.google.com:19302';
const TURN_SERVER = import.meta.env.VITE_TURN_SERVER || '';
const TURN_USERNAME = import.meta.env.VITE_TURN_USERNAME || '';
const TURN_PASSWORD = import.meta.env.VITE_TURN_PASSWORD || '';

/**
 * Parse STUN servers from comma-separated string
 * @returns {Array} Array of STUN server URLs
 */
function parseStunServers() {
  return STUN_SERVERS.split(',')
    .map(s => s.trim())
    .filter(Boolean);
}

/**
 * Get ICE servers configuration for WebRTC
 * @returns {Array} ICE servers array for RTCPeerConnection
 */
export function getIceServers() {
  const iceServers = [];

  // Add STUN servers
  const stunServers = parseStunServers();
  if (stunServers.length > 0) {
    iceServers.push({
      urls: stunServers
    });
  }

  // Add TURN server if configured
  if (TURN_SERVER) {
    const turnConfig = {
      urls: TURN_SERVER
    };

    if (TURN_USERNAME && TURN_PASSWORD) {
      turnConfig.username = TURN_USERNAME;
      turnConfig.credential = TURN_PASSWORD;
    }

    iceServers.push(turnConfig);
  }

  return iceServers;
}

/**
 * Get SIP UserAgent configuration
 * @param {string} extension - User's SIP extension
 * @param {Object} delegates - Callback delegates for SIP events
 * @returns {Object} SIP UserAgent configuration object
 */
export function getSipConfig(extension, delegates = {}) {
  const iceServers = getIceServers();

  return {
    uri: null, // Set by caller using SIP.UserAgent.makeURI
    authorizationUsername: extension,
    authorizationPassword: SIP_PASSWORD,
    displayName: extension,
    userAgentString: 'OPENCHS UA (SIP.js)',
    transportOptions: {
      server: SIP_WS_URL,
      traceSip: import.meta.env.DEV, // Only trace in development
    },
    sessionDescriptionHandlerFactoryOptions: {
      peerConnectionConfiguration: {
        iceServers: iceServers,
        iceTransportPolicy: 'all',
        bundlePolicy: 'balanced',
        rtcpMuxPolicy: 'require'
      }
    },
    log: {
      level: import.meta.env.DEV ? 'debug' : 'warn'
    },
    delegate: delegates
  };
}

/**
 * Get audio constraints for WebRTC
 * @param {boolean} echoCancellation - Enable echo cancellation
 * @param {boolean} noiseSuppression - Enable noise suppression
 * @returns {Object} Audio constraints object
 */
export function getAudioConstraints(echoCancellation = true, noiseSuppression = true) {
  return {
    audio: {
      echoCancellation,
      noiseSuppression,
      autoGainControl: true
    },
    video: false
  };
}

/**
 * Configuration exports
 */
export const config = {
  SIP_HOST,
  SIP_WS_URL,
  AMI_WS_URL,
  SIP_CALL_TIMEOUT,

  // Helper to build SIP URI
  buildSipUri: (extension) => `sip:${extension}@${SIP_HOST}`,

  // Session description handler options
  getSessionOptions: () => ({
    sessionDescriptionHandlerOptions: {
      constraints: getAudioConstraints(),
      peerConnectionConfiguration: {
        iceServers: getIceServers()
      }
    }
  }),

  // Hold options for re-INVITE
  getHoldOptions: (hold) => ({
    sessionDescriptionHandlerOptions: {
      hold,
      constraints: getAudioConstraints()
    },
    requestDelegate: {
      onAccept: () => console.log(`Hold ${hold ? 'activated' : 'deactivated'}`),
      onReject: () => console.warn(`Hold ${hold ? 'activation' : 'deactivation'} rejected`)
    }
  })
};

export default config;

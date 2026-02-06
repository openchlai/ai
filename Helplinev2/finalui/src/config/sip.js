/**
 * SIP/WebRTC Configuration Module
 * 
 * Centralizes all SIP-related configuration and provides dynamic resolvers
 * that adapt to the active country/environment registry.
 */

// Hardcoded fallbacks
const DEFAULT_STUN_SERVERS = 'stun:stun.l.google.com:19302,stun:stun1.l.google.com:19302';
const DEFAULT_HOST = 'demo-openchs.bitz-itc.com';

/**
 * Get the current environment configuration from the registry.
 * Because this is a plain JS module, we use the helper from taxonomyContract.
 */
import { getEnvironmentConfig } from './taxonomyContract';

/**
 * Resolves SIP/VOIP settings dynamically based on current environment
 */
export function getActiveVoipConfig() {
  const env = getEnvironmentConfig();
  const voip = env.VOIP || {};
  const endpoints = env.ENDPOINTS || {};

  const host = voip.SIP_HOST || import.meta.env.VITE_SIP_HOST || DEFAULT_HOST;
  let wsUrl = voip.SIP_WS_URL || import.meta.env.VITE_SIP_WS_URL || `wss://${host}/ws/`;

  // Smart Dev Proxy: If in dev mode, route through registry-defined path to bypass SSL/1006 errors
  if (import.meta.env.DEV && endpoints.SIP_WS_PATH) {
    const targetDomain = endpoints.DEV_TARGET_SIP?.replace('https://', '').replace('http://', '').split(':')[0];
    if (wsUrl.includes(targetDomain) || wsUrl.includes('192.168.10.3')) {
      wsUrl = endpoints.SIP_WS_PATH;
    }
  }

  // If we converted to a relative URL (proxy path), resolve it to the full browser host
  if (wsUrl.startsWith('/')) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    wsUrl = `${protocol}//${window.location.host}${wsUrl}`;
  }

  return {
    SIP_HOST: host,
    SIP_WS_URL: wsUrl,
    SIP_USER_PREFIX: voip.SIP_USER_PREFIX || '',
    SIP_PASS_PREFIX: voip.SIP_PASS_PREFIX || '',
    SIP_PASSWORD: import.meta.env.VITE_VA_SIP_PASS_PREFIX || '23kdefrtgos09812100',
    SIP_CALL_TIMEOUT: parseInt(import.meta.env.VITE_SIP_CALL_TIMEOUT || '30000', 10),
    AMI_WS_URL: endpoints.AMI_HOST || import.meta.env.VITE_AMI_WS_URL || `wss://${host}:8384/ami/sync`,
    ICE_SERVERS: voip.ICE_SERVERS || [
      { urls: DEFAULT_STUN_SERVERS.split(',') }
    ]
  };
}

/**
 * Get SIP UserAgent configuration
 */
export function getSipConfig(extension, delegates = {}, password = null) {
  const config = getActiveVoipConfig();

  // Apply Prefix Logic: 
  // If prefix is short (likely a prefix), append extension.
  // If prefix is long (likely a global secret), use as-is.
  // Ensure prefix is applied correctly to the username
  const authUser = config.SIP_USER_PREFIX ? `${config.SIP_USER_PREFIX}${extension}` : extension;

  // Password recovery: Use provided password, or global secret from config, or fallback to extension
  let authPass = password || config.SIP_PASSWORD || extension;

  // If a short prefix (e.g. '0') is explicitly set, we derive password from it
  if (config.SIP_PASS_PREFIX && config.SIP_PASS_PREFIX.length < 5) {
    authPass = `${config.SIP_PASS_PREFIX}${extension}`;
  }

  return {
    uri: null,
    authorizationUsername: authUser,
    authorizationPassword: authPass,
    displayName: authUser,
    userAgentString: 'OPENCHS UA (SIP.js)',
    transportOptions: {
      server: config.SIP_WS_URL,
      traceSip: false,
    },
    sessionDescriptionHandlerFactoryOptions: {
      peerConnectionConfiguration: {
        iceServers: config.ICE_SERVERS,
        iceTransportPolicy: 'all',
        bundlePolicy: 'balanced',
        rtcpMuxPolicy: 'require'
      }
    },
    logBuiltinEnabled: false,
    logConfiguration: false,
    logLevel: 'error',
    delegate: delegates
  };
}

/**
 * Reusable audio constraints
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
 * Legacy-compatible config object (Proxy-based to remain dynamic)
 */
export const config = {
  get SIP_HOST() { return getActiveVoipConfig().SIP_HOST },
  get SIP_WS_URL() { return getActiveVoipConfig().SIP_WS_URL },
  get AMI_WS_URL() { return getActiveVoipConfig().AMI_WS_URL },
  get SIP_PASSWORD() { return getActiveVoipConfig().SIP_PASSWORD },
  get SIP_CALL_TIMEOUT() { return getActiveVoipConfig().SIP_CALL_TIMEOUT },

  buildSipUri: (extension) => {
    const cfg = getActiveVoipConfig();
    const user = cfg.SIP_USER_PREFIX ? (cfg.SIP_USER_PREFIX + extension) : extension;
    return `sip:${user}@${cfg.SIP_HOST}`;
  },

  getSessionOptions: () => ({
    sessionDescriptionHandlerOptions: {
      constraints: getAudioConstraints(),
      peerConnectionConfiguration: {
        iceServers: getActiveVoipConfig().ICE_SERVERS
      }
    }
  }),

  getHoldOptions: (hold) => ({
    sessionDescriptionHandlerOptions: {
      hold,
      constraints: getAudioConstraints()
    }
  })
};

export default config;

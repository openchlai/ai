// src/stores/realtime.js
// Global real-time store managing AMI (voice) + ATI (text) WebSocket connections.
// Mounted at layout level so all pages can consume live channel/interaction data.
import { defineStore } from 'pinia'
import { useTaxonomyStore } from './taxonomy'

export const useRealtimeStore = defineStore('realtime', {
  state: () => ({
    // AMI (voice channels)
    amiChannels: {},        // Map<uniqueid, channelObj>
    amiReady: 'closed',     // 'closed' | 'connecting' | 'open' | 'error'
    lastAmiUpdate: null,

    // ATI (text interactions)
    atiInteractions: {},    // Map<key, interactionObj>
    atiReady: 'closed',
    lastAtiUpdate: null,

    // Internal (not reactive on purpose — use underscore convention)
    _amiWs: null,
    _atiPollTimer: null,
    _atiUrl: null,
    _reconnectTimers: { ami: null, ati: null },
    _reconnectAttempts: { ami: 0, ati: 0 }
  }),

  getters: {
    amiChannelsList: (state) => Object.values(state.amiChannels),
    atiInteractionsList: (state) => Object.values(state.atiInteractions),

    isAmiConnected: (state) => state.amiReady === 'open',
    isAtiConnected: (state) => state.atiReady === 'open',

    // Counsellor/agent channels (context includes agent/login/internal)
    agentChannels: (state) => {
      return Object.values(state.amiChannels).filter(ch => {
        const ctx = (ch.CHAN_CONTEXT || '').toLowerCase()
        return ctx.includes('agent') || ctx.includes('login') || ctx.includes('internal')
      })
    },

    // External caller channels (context includes trunk/callcenter/external/default)
    callerChannels: (state) => {
      return Object.values(state.amiChannels).filter(ch => {
        const ctx = (ch.CHAN_CONTEXT || '').toLowerCase()
        return ctx.includes('trunk') || ctx.includes('callcenter') || ctx.includes('external') || ctx.includes('default')
      })
    },

    // Count of unread ATI text interactions
    unreadTextCount: (state) => {
      return Object.values(state.atiInteractions).filter(i => {
        return Number(i.ATI_UNREAD) > 0 || (Number(i.ATI_STATE_QUEUE) > 0 && !Number(i.ATI_STATE_CONNECT))
      }).length
    },

    // AI notifications from the ATI text channel (source='aii', context='trunk')
    aiNotifications: (state) => {
      return Object.values(state.atiInteractions).filter(i => {
        return i.ATI_SRC === 'aii' && i.ATI_CONTEXT === 'trunk'
      })
    },

    // Get AI notifications matching a specific bridge_id
    aiNotificationsForCall: (state) => (bridgeId) => {
      if (!bridgeId) return []
      return Object.values(state.atiInteractions).filter(i => {
        return i.ATI_SRC === 'aii' && i.ATI_CONTEXT === 'trunk' && i.ATI_BRIDGE_ID === bridgeId
      })
    },

    // Check if a given extension appears in any AMI channel (queued/active agent)
    isExtensionInQueue: (state) => (extension) => {
      if (!extension) return false
      const ext = String(extension)
      return Object.values(state.amiChannels).some(ch => {
        const chan = ch.CHAN_CHAN || ''
        const exten = ch.CHAN_EXTEN || ''
        return chan.includes(`/${ext}-`) || chan.endsWith(`/${ext}`) || exten === ext
      })
    }
  },

  actions: {
    // ── AMI Field Mapping (from useWebSocketConnection.js) ──────────
    parseAmiChannel(key, arr) {
      if (!Array.isArray(arr)) return { _uid: key, ...arr }
      return {
        _uid: key,
        CHAN_TS: arr[1] || Date.now(),
        CHAN_UNIQUEID: arr[2] || key,
        CHAN_CHAN: arr[3] || '',
        CHAN_CALLERID_NUM: arr[4] || '',
        CHAN_CALLERID_NAME: arr[5] || '',
        CHAN_CONTEXT: arr[6] || '',
        CHAN_EXTEN: arr[7] || '',
        CHAN_ACTION_ID: arr[8] || '',
        CHAN_STATE_UP: arr[13] || 0,
        CHAN_STATE_QUEUE: arr[14] || 0,
        CHAN_STATE_CONNECT: arr[15] || 0,
        CHAN_STATE_HANGUP: arr[16] || 0,
        CHAN_STATE_HOLD: arr[18] || 0,
        CHAN_CBO_TS: arr[20] || '',
        CHAN_CBO: arr[21] || '',
        CHAN_CBO_UNIQUEID: arr[22] || '',
        CHAN_CBO_CID: arr[23] || '',
        CHAN_XFER_TS: arr[24] || '',
        CHAN_XFER: arr[25] || '',
        CHAN_XFER_UNIQUEID: arr[26] || '',
        CHAN_XFER_CID: arr[27] || '',
        CHAN_ORIG: arr[36] || '',
        CHAN_CONTEXT_MASQ: arr[43] || '',
        CHAN_EXTEN_MASQ: arr[44] || '',
        CHAN_UNIQUEID_2: arr[45] || '',
        CHAN_CHAN_2: arr[46] || '',
        CHAN_CID_NUM_2: arr[47] || '',
        CHAN_SIPCALLID: arr[50] || '',
        CHAN_BRIDGE_ID: arr[51] || '',
        CHAN_CAMPAIGN_ID: arr[53] || '',
        CHAN_CAMPAIGN_WRAPUP: arr[54] || '',
        CHAN_PROMPT_TS0: arr[67] || '',
        CHAN_VECTOR: arr[74] || '',
        CHAN_EVENT: arr[76] || '',
        CHAN_EVENT_N: arr[77] || '',
        CHAN_SIPID_JS_: arr[80] || '',
        CHAN_STATUS_: arr[81] || '',
        CHAN_STATUS_TXT_: arr[82] || '',
        CHAN_STATUS_TS_: arr[83] || '',
        CHAN_STATUS_TS_TXT_: arr[84] || '',
        _raw: arr
      }
    },

    // ── ATI Field Mapping (from legacy ati.js ATI constants) ────────
    // NOTE: ATI uses a DIFFERENT schema from AMI at indices 20+.
    // Legacy reference: /Local-Dev-Helpine/app/ati.js lines 49-88
    parseAtiInteraction(key, arr) {
      if (!Array.isArray(arr)) return { _uid: key, ...arr }
      return {
        _uid: key,
        ATI_TS: arr[1] || Date.now(),
        ATI_UNIQUEID: arr[2] || key,
        ATI_CHAN: arr[3] || '',
        ATI_CALLERID_NUM: arr[4] || '',
        ATI_CALLERID_NAME: arr[5] || '',
        ATI_CONTEXT: arr[6] || '',
        ATI_EXTEN: arr[7] || '',
        ATI_ACTION_ID: arr[8] || '',
        ATI_STATE_ORIG: arr[9] || 0,
        ATI_STATE_DOWN: arr[10] || 0,
        ATI_STATE_DIAL: arr[11] || 0,
        ATI_STATE_RING: arr[12] || 0,
        ATI_STATE_UP: arr[13] || 0,
        ATI_STATE_QUEUE: arr[14] || 0,
        ATI_STATE_CONNECT: arr[15] || 0,
        ATI_STATE_HANGUP: arr[16] || 0,
        ATI_STATE_MUTE: arr[17] || 0,
        ATI_STATE_HOLD: arr[18] || 0,
        ATI_HOLD_TIME: arr[19] || 0,
        // ATI-specific fields (different from AMI at indices 20+)
        ATI_BRIDGE_ID: arr[20] || '',      // Call bridge ID for AI matching
        ATI_BRIDGE_COUNT: arr[21] || 0,
        ATI_UNREAD: arr[22] || 0,
        ATI_HANGUP_REASON: arr[23] || '',
        ATI_UID_2: arr[24] || '',
        ATI_CID_2: arr[25] || '',
        ATI_SRC: arr[26] || '',            // Source type: 'aii', 'whatsapp', etc.
        ATI_MSG: arr[27] || '',            // Message content
        ATI_BREAK_REASON: arr[28] || '',
        ATI_VECTOR: arr[29] || '',
        ATI_STATUS_: arr[31] || '',
        ATI_STATUS_TXT_: arr[32] || '',
        ATI_STATUS_TS_: arr[33] || '',
        ATI_STATUS_TS_TXT_: arr[34] || '',
        _raw: arr
      }
    },

    // ── Message Handlers ────────────────────────────────────────────
    handleAmiMessage(payload) {
      this.lastAmiUpdate = new Date().toLocaleString()

      let obj = payload
      if (typeof payload === 'string') {
        try { obj = JSON.parse(payload) } catch { return }
      }

      if (!obj.channels) return

      const parsed = {}
      if (Array.isArray(obj.channels)) {
        obj.channels.forEach(item => {
          if (Array.isArray(item)) {
            const key = item[2] || String(Math.random())
            parsed[key] = this.parseAmiChannel(key, item)
          } else {
            const key = item.CHAN_UNIQUEID || item._uid || String(Math.random())
            parsed[key] = item
          }
        })
      } else if (typeof obj.channels === 'object') {
        for (const [key, arr] of Object.entries(obj.channels)) {
          parsed[key] = this.parseAmiChannel(key, arr)
        }
      }

      this.amiChannels = parsed
    },

    handleAtiMessage(payload) {
      this.lastAtiUpdate = new Date().toLocaleString()

      let obj = payload
      if (typeof payload === 'string') {
        try { obj = JSON.parse(payload) } catch { return }
      }

      // ATI sends data in 'ati' or 'channels' key depending on server version
      const atiData = obj.ati || obj.channels
      if (!atiData) return

      const parsed = {}
      if (Array.isArray(atiData)) {
        atiData.forEach(item => {
          if (Array.isArray(item)) {
            const key = item[2] || String(Math.random())
            parsed[key] = this.parseAtiInteraction(key, item)
          } else {
            const key = item.ATI_UNIQUEID || item._uid || String(Math.random())
            parsed[key] = item
          }
        })
      } else if (typeof atiData === 'object') {
        for (const [key, arr] of Object.entries(atiData)) {
          parsed[key] = this.parseAtiInteraction(key, arr)
        }
      }

      this.atiInteractions = parsed

      const aiCount = Object.values(parsed).filter(i => i.ATI_SRC === 'aii').length
      if (aiCount > 0) {
        console.log(`[Realtime] ATI poll: ${aiCount} AI notification(s) present`)
      }
    },

    // ── Host Resolution ────────────────────────────────────────────
    // In DEV mode, connect directly to the backend WebSocket (bypasses Vite proxy
    // which mangles the Sec-WebSocket-Accept handshake). In production, the URL
    // is already correct (absolute wss:// or relative path resolved by nginx).
    resolveWsHost(host) {
      if (!host) return host

      // If it's already a ws:// or wss:// URL, use it directly
      if (host.startsWith('ws://') || host.startsWith('wss://')) return host

      // Convert relative paths to full WebSocket URLs (production behind nginx)
      if (host.startsWith('/')) {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        return `${protocol}//${window.location.host}${host}`
      }

      return host
    },

    // ── WebSocket Connections ───────────────────────────────────────
    connectAmi() {
      if (this._amiWs && this.amiReady === 'open') return

      const taxonomyStore = useTaxonomyStore()
      const amiEnvUrl = import.meta.env.VITE_AMI_WS_URL
      const amiPath = taxonomyStore.endpoints?.AMI_WS_PATH || '/ami/sync'
      const base = amiEnvUrl || amiPath
      const resolved = this.resolveWsHost(base)
      const url = `${resolved}${resolved.includes('?') ? '&' : '?'}c=-2`

      console.log('[Realtime] Connecting AMI:', url)
      this.amiReady = 'connecting'

      try {
        const ws = new WebSocket(url)

        ws.onopen = () => {
          console.log('[Realtime] AMI connected')
          this._reconnectAttempts.ami = 0
          this.amiReady = 'open'
        }

        ws.onmessage = (ev) => {
          try { this.handleAmiMessage(ev.data) } catch {}
        }

        ws.onclose = (ev) => {
          console.log(`[Realtime] AMI disconnected — code=${ev.code} reason="${ev.reason}" wasClean=${ev.wasClean}`)
          this.amiReady = 'closed'
          this._amiWs = null
          this.scheduleReconnect('ami')
        }

        ws.onerror = (ev) => {
          console.warn('[Realtime] AMI error', ev)
          this.amiReady = 'error'
        }

        this._amiWs = ws
      } catch {
        this.amiReady = 'error'
        this.scheduleReconnect('ami')
      }
    },

    // ATI uses HTTP polling (not WebSocket). The server returns a JSON snapshot
    // of current text interactions. We poll every 3 seconds for near-real-time updates.
    connectAti() {
      if (this._atiPollTimer && this.atiReady === 'open') return

      const taxonomyStore = useTaxonomyStore()

      // Build HTTP URL: use proxy path so requests go through Vite (dev) or nginx (prod)
      // instead of hitting backend IPs directly (which causes CORS failures)
      const baseUrl = taxonomyStore.endpoints?.ATI_WS_PATH || '/ati/sync'
      this._atiUrl = `${baseUrl}${baseUrl.includes('?') ? '&' : '?'}c=-1`

      console.log('[Realtime] Starting ATI poll:', this._atiUrl)
      this.atiReady = 'open'
      this._reconnectAttempts.ati = 0

      // Fetch immediately, then poll every 3 seconds
      this._fetchAti()
      this._atiPollTimer = setInterval(() => this._fetchAti(), 3000)
    },

    async _fetchAti() {
      try {
        const resp = await fetch(this._atiUrl)
        if (!resp.ok) throw new Error(`ATI HTTP ${resp.status}`)
        const data = await resp.json()
        this.handleAtiMessage(data)
        this.atiReady = 'open'
      } catch (err) {
        // Silently retry on next interval — don't spam logs
      }
    },

    // ── Reconnect Logic ─────────────────────────────────────────────
    scheduleReconnect(type) {
      if (this._reconnectTimers[type]) return

      this._reconnectAttempts[type]++
      const attempt = this._reconnectAttempts[type]
      const backoff = Math.min(30000, 1000 * Math.pow(1.8, attempt))

      console.log(`[Realtime] ${type.toUpperCase()} reconnect #${attempt} in ${Math.round(backoff / 1000)}s`)

      this._reconnectTimers[type] = setTimeout(() => {
        this._reconnectTimers[type] = null
        if (type === 'ami') this.connectAmi()
        else this.connectAti()
      }, backoff)
    },

    // ── Public API ──────────────────────────────────────────────────
    connect() {
      this.connectAmi()
      this.connectAti()
    },

    disconnect() {
      // Clear reconnect timers
      for (const type of ['ami', 'ati']) {
        if (this._reconnectTimers[type]) {
          clearTimeout(this._reconnectTimers[type])
          this._reconnectTimers[type] = null
        }
      }

      // Close AMI
      if (this._amiWs) {
        try { this._amiWs.close() } catch {}
        this._amiWs = null
      }
      this.amiReady = 'closed'
      this.amiChannels = {}

      // Close ATI (HTTP poll)
      if (this._atiPollTimer) {
        clearInterval(this._atiPollTimer)
        this._atiPollTimer = null
      }
      this.atiReady = 'closed'
      this.atiInteractions = {}

      this._reconnectAttempts = { ami: 0, ati: 0 }
      console.log('[Realtime] Disconnected all')
    }
  }
})

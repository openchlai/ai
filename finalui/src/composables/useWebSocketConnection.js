import { ref, onBeforeUnmount } from 'vue'

export function useWebSocketConnection(wsHost) {
  const ws = ref(null)
  const wsReady = ref('closed')
  const channels = ref([])
  const lastUpdate = ref(null)
  const reconnectAttempt = ref(0)
  const reconnectTimer = ref(null)

  const handleMessage = (payload, fetchCounsellorName, fetchCounsellorStats) => {
    lastUpdate.value = new Date().toLocaleString()
    
    let obj = payload
    if (typeof payload === 'string') {
      try {
        obj = JSON.parse(payload)
      } catch (err) {
        return
      }
    }

    let chArr = []
    if (Array.isArray(obj.channels)) {
      chArr = obj.channels
    } else if (obj.channels && typeof obj.channels === 'object') {
      chArr = Object.entries(obj.channels).map(([key, arr]) => {
        if (Array.isArray(arr)) {
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
        }
        return { _uid: key, ...arr }
      })
    }
    
    channels.value = chArr

    // Trigger name and stats fetching for new counsellor extensions
    const counsellorChannels = chArr.filter(ch => {
      const context = (ch.CHAN_CONTEXT || '').toLowerCase()
      return context === 'agentlogin'
    })
    
    counsellorChannels.forEach((ch) => {
      const extension = ch.CHAN_EXTEN
      
      if (extension && extension !== '--') {
        if (fetchCounsellorName) {
          fetchCounsellorName(extension)
        }
        if (fetchCounsellorStats) {
          fetchCounsellorStats(extension)
        }
      }
    })
  }

  const connect = (channelsRef, fetchCounsellorName, fetchCounsellorStats) => {
    if (ws.value && wsReady.value === 'open') return
    wsReady.value = 'connecting'

    try {
      ws.value = new WebSocket(wsHost)

      ws.value.onopen = () => {
        reconnectAttempt.value = 0
        wsReady.value = 'open'
      }

      ws.value.onmessage = (ev) => {
        try {
          console.log('WebSocket message received', ev.data)
          handleMessage(ev.data, fetchCounsellorName, fetchCounsellorStats)
        } catch (err) {
          // Handle silently
        }
      }

      ws.value.onclose = (ev) => {
        wsReady.value = 'closed'
        scheduleReconnect(channelsRef, fetchCounsellorName, fetchCounsellorStats)
      }

      ws.value.onerror = (err) => {
        wsReady.value = 'error'
      }
    } catch (err) {
      wsReady.value = 'error'
      scheduleReconnect(channelsRef, fetchCounsellorName, fetchCounsellorStats)
    }
  }

  const scheduleReconnect = (channelsRef, fetchCounsellorName, fetchCounsellorStats) => {
    if (reconnectTimer.value) return
    reconnectAttempt.value++
    const attempt = reconnectAttempt.value
    const backoff = Math.min(30000, 1000 * Math.pow(1.8, attempt))
    reconnectTimer.value = setTimeout(() => {
      reconnectTimer.value = null
      connect(channelsRef, fetchCounsellorName, fetchCounsellorStats)
    }, backoff)
  }

  const disconnect = () => {
    if (reconnectTimer.value) {
      clearTimeout(reconnectTimer.value)
      reconnectTimer.value = null
    }
    if (ws.value) {
      try { 
        ws.value.close() 
      } catch (e) { 
        // ignore cleanup errors
      }
      ws.value = null
    }
    wsReady.value = 'closed'
  }

  onBeforeUnmount(() => {
    disconnect()
  })

  return {
    channels,
    wsReady,
    lastUpdate,
    connect,
    disconnect
  }
}
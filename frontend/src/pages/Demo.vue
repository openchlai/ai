<template>
  <div class="queue-monitor">
    <header class="qm-header">
      <h3>Queue Monitor (Live)</h3>
      <div class="status-row">
        <span :class="['dot', connectionClass]"></span>
        <span>{{ connectionLabel }}</span>
        <small v-if="lastUpdate"> · last update: {{ lastUpdate }}</small>
      </div>
    </header>

    <section class="controls">
      <div class="left">
        <label>
          Filter by queue:
          <select v-model="filter.vector">
            <option value="">— All —</option>
            <option v-for="v in uniqueVectors" :key="v" :value="v">{{ v }}</option>
          </select>
        </label>

        <label>
          Campaign:
          <select v-model="filter.campaign">
            <option value="">— All —</option>
            <option v-for="c in uniqueCampaigns" :key="c" :value="c">{{ c }}</option>
          </select>
        </label>

        <label>
          Search:
          <input v-model="filter.q" placeholder="caller number / name / chan" />
        </label>
      </div>

      <div class="right">
        <button @click="connect" :disabled="isConnected">Connect</button>
        <button @click="disconnect" :disabled="!ws || wsReady === 'closed'">Disconnect</button>
        <button @click="clearList">Clear</button>
      </div>
    </section>

    <section class="summary">
      <div class="stat">
        <div class="num">{{ channels.length }}</div>
        <div class="label">Total Channels</div>
      </div>
      <div class="stat">
        <div class="num">{{ counts.inQueue }}</div>
        <div class="label">In Queue</div>
      </div>
      <div class="stat">
        <div class="num">{{ counts.connected }}</div>
        <div class="label">Connected</div>
      </div>
      <div class="stat">
        <div class="num">{{ counts.onHold }}</div>
        <div class="label">On Hold</div>
      </div>
      <div class="stat">
        <div class="num">{{ counts.hangup }}</div>
        <div class="label">Hangup</div>
      </div>
    </section>

    <section class="table-wrapper">
      <table class="channels-table">
        <thead>
          <tr>
            <th>Time</th>
            <th>Chan</th>
            <th>UniqueID</th>
            <th>Caller #</th>
            <th>Caller Name</th>
            <th>Queue / Vector</th>
            <th>Exten</th>
            <th>State</th>
            <th>Campaign</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="ch in visibleChannels" :key="ch.CHAN_UNIQUEID || ch._uid || chIdxKey(ch)">
            <td>{{ formatTs(ch.CHAN_TS) }}</td>
            <td>{{ safe(ch.CHAN_CHAN) }}</td>
            <td class="mono">{{ safe(ch.CHAN_UNIQUEID) }}</td>
            <td>{{ safe(ch.CHAN_CALLERID_NUM) }}</td>
            <td>{{ safe(ch.CHAN_CALLERID_NAME) }}</td>
            <td>{{ safe(ch.CHAN_VECTOR) }}</td>
            <td>{{ safe(ch.CHAN_EXTEN) }}</td>
            <td>
              <span :class="['status-badge', statusClass(ch)]">{{ statusText(ch) }}</span>
            </td>
            <td>{{ safe(ch.CHAN_CAMPAIGN_ID) }}</td>
            <td>
              <button @click="inspect(ch)">Inspect</button>
            </td>
          </tr>
          <tr v-if="visibleChannels.length === 0">
            <td colspan="10" class="no-data">No channels (matching filters)</td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- Optional debug / raw payload -->
    <details class="debug" v-if="showRaw">
      <summary>Raw (latest payload)</summary>
      <pre>{{ lastPayload }}</pre>
    </details>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch } from 'vue';

/*
  QueueMonitor.vue
  - Connects to websocket and streams JSON objects containing array of channels
  - Fields expected (examples): CHAN_TS, CHAN_UNIQUEID, CHAN_CHAN, CHAN_CALLERID_NUM, CHAN_CALLERID_NAME,
    CHAN_VECTOR, CHAN_EXTEN, CHAN_STATE_QUEUE, CHAN_STATE_CONNECT, CHAN_STATE_HOLD, CHAN_STATE_HANGUP,
    CHAN_CAMPAIGN_ID, etc.
*/

const WSHOST = 'wss://demo-openchs.bitz-itc.com:8384/ami/sync?c=-2&';

// reactive state
const ws = ref(null);
const wsReady = ref('closed'); // 'connecting'|'open'|'closed'|'error'
const reconnectAttempt = ref(0);
const reconnectTimer = ref(null);

const channels = ref([]);         // array of latest channel objects
const lastPayload = ref(null);    // raw last message (string or object)
const lastUpdate = ref(null);     // formatted last update time

const showRaw = ref(false);

// simple filters
const filter = reactive({
  vector: '',
  campaign: '',
  q: '' // search
});

// counts computed from channels
const counts = computed(() => {
  const c = { inQueue: 0, connected: 0, onHold: 0, hangup: 0 };
  for (const ch of channels.value) {
    if (Number(ch.CHAN_STATE_QUEUE) === 1 || Number(ch.CHAN_STATE_QUEUE) === 2 || Number(ch.CHAN_STATE_QUEUE) === 3) {
      c.inQueue++;
    }
    if (Number(ch.CHAN_STATE_CONNECT)) c.connected += Number(ch.CHAN_STATE_CONNECT) ? 1 : 0;
    if (Number(ch.CHAN_STATE_HOLD)) c.onHold += Number(ch.CHAN_STATE_HOLD) ? 1 : 0;
    if (Number(ch.CHAN_STATE_HANGUP)) c.hangup += Number(ch.CHAN_STATE_HANGUP) ? 1 : 0;
  }
  return c;
});

// helper: unique vectors & campaigns for selects
const uniqueVectors = computed(() => {
  const s = new Set();
  channels.value.forEach(c => { if (c.CHAN_VECTOR) s.add(String(c.CHAN_VECTOR)); });
  return Array.from(s).sort();
});
const uniqueCampaigns = computed(() => {
  const s = new Set();
  channels.value.forEach(c => { if (c.CHAN_CAMPAIGN_ID) s.add(String(c.CHAN_CAMPAIGN_ID)); });
  return Array.from(s).sort();
});

// filtered list for table
const visibleChannels = computed(() => {
  const q = filter.q?.trim().toLowerCase();
  return channels.value.filter(ch => {
    if (filter.vector && String(ch.CHAN_VECTOR) !== String(filter.vector)) return false;
    if (filter.campaign && String(ch.CHAN_CAMPAIGN_ID) !== String(filter.campaign)) return false;
    if (!q) return true;
    // search a few columns
    const hay = [
      String(ch.CHAN_CALLERID_NUM || ''),
      String(ch.CHAN_CALLERID_NAME || ''),
      String(ch.CHAN_CHAN || ''),
      String(ch.CHAN_UNIQUEID || ''),
      String(ch.CHAN_EXTEN || '')
    ].join(' ').toLowerCase();
    return hay.includes(q);
  });
});

// connection status
const isConnected = computed(() => wsReady.value === 'open');
const connectionLabel = computed(() => {
  if (wsReady.value === 'connecting') return 'Connecting...';
  if (wsReady.value === 'open') return 'Connected';
  if (wsReady.value === 'error') return 'Error';
  return 'Disconnected';
});
const connectionClass = computed(() => (wsReady.value === 'open' ? 'on' : (wsReady.value === 'connecting' ? 'connecting' : 'off')));

// safe access helper
function safe(v) { return v === undefined || v === null ? '' : String(v); }

// handle incoming JSON message (expects object containing channels array)
function handleMessage(payload) {
  lastPayload.value = payload;
  lastUpdate.value = new Date().toLocaleString();

  let obj = payload;
  if (typeof payload === 'string') {
    try {
      obj = JSON.parse(payload);
    } catch (err) {
      console.error('[QueueMonitor] Failed to parse JSON payload', err);
      return;
    }
  }

  // Handle both array and object keyed by channel IDs
  let chArr = [];
  if (Array.isArray(obj.channels)) {
    chArr = obj.channels;
  } else if (obj.channels && typeof obj.channels === 'object') {
    // Convert object to array with id + values
    chArr = Object.entries(obj.channels).map(([key, arr]) => {
      // If backend sends array of fields, map them to best-effort object
      if (Array.isArray(arr)) {
        return {
          _uid: key,
          CHAN_CHAN: arr[3] || '',
          CHAN_UNIQUEID: arr[1] || key,
          CHAN_CALLERID_NUM: arr[4] || '',
          CHAN_CALLERID_NAME: arr[5] || '',
          CHAN_VECTOR: arr[74] || '',
          CHAN_EXTEN: arr[6] || '',
          CHAN_STATE_QUEUE: arr[14] || 0,
          CHAN_STATE_CONNECT: arr[15] || 0,
          CHAN_STATE_HANGUP: arr[16] || 0,
          CHAN_STATE_HOLD: arr[18] || 0,
          CHAN_CAMPAIGN_ID: arr[53] || '',
          CHAN_TS: arr[0] || Date.now(),
          _raw: arr
        };
      }
      return { _uid: key, ...arr };
    });
  } else {
    console.warn('[QueueMonitor] payload does not contain channels array/object', obj);
    return;
  }

  channels.value = chArr;
}

// WebSocket lifecycle
function connect() {
  if (ws.value && wsReady.value === 'open') return;
  wsReady.value = 'connecting';

  try {
    ws.value = new WebSocket(WSHOST);

    ws.value.onopen = () => {
      reconnectAttempt.value = 0;
      wsReady.value = 'open';
      console.log('[QueueMonitor] WebSocket opened');
    };

    ws.value.onmessage = (ev) => {
      try {
        handleMessage(ev.data);
      } catch (err) {
        console.error('[QueueMonitor] error handling message', err);
      }
    };

    ws.value.onclose = (ev) => {
      console.warn('[QueueMonitor] WebSocket closed', ev.code, ev.reason);
      wsReady.value = 'closed';
      scheduleReconnect();
    };

    ws.value.onerror = (err) => {
      console.error('[QueueMonitor] WebSocket error', err);
      wsReady.value = 'error';
      // allow onclose to handle reconnect
    };
  } catch (err) {
    console.error('[QueueMonitor] WebSocket connect failed', err);
    wsReady.value = 'error';
    scheduleReconnect();
  }
}

function disconnect() {
  if (reconnectTimer.value) {
    clearTimeout(reconnectTimer.value);
    reconnectTimer.value = null;
  }
  if (ws.value) {
    try { ws.value.close(); } catch (e) { /* ignore */ }
    ws.value = null;
  }
  wsReady.value = 'closed';
}

// schedule reconnect with exponential backoff
function scheduleReconnect() {
  if (reconnectTimer.value) return;
  reconnectAttempt.value++;
  const attempt = reconnectAttempt.value;
  const backoff = Math.min(30000, 1000 * Math.pow(1.8, attempt)); // cap 30s
  console.log(`[QueueMonitor] reconnect in ${Math.round(backoff)}ms (attempt ${attempt})`);
  reconnectTimer.value = setTimeout(() => {
    reconnectTimer.value = null;
    connect();
  }, backoff);
}

// format timestamp safely (CHAN_TS)
function toMillis(ts) {
  // ts may be numeric or string, seconds or milliseconds.
  if (ts === undefined || ts === null || ts === '') return null;
  const n = Number(ts);
  if (!Number.isFinite(n)) return null;
  // if value looks like seconds (<= 1e11), multiply by 1000
  if (n < 1e11) return Math.floor(n * 1000);
  return Math.floor(n);
}
function formatTs(ts) {
  const ms = toMillis(ts);
  if (!ms) return '';
  try {
    return new Date(ms).toLocaleString();
  } catch (err) {
    return String(ts);
  }
}

// status helpers
function statusText(ch) {
  // many CHAN_STATE_* fields exist; prefer CHAN_STATUS_TXT_ or state flags
  if (ch.CHAN_STATUS_TXT_) return String(ch.CHAN_STATUS_TXT_);
  if (Number(ch.CHAN_STATE_HANGUP)) return 'Hangup';
  if (Number(ch.CHAN_STATE_CONNECT)) return 'Connected';
  if (Number(ch.CHAN_STATE_HOLD)) return 'Hold';
  if (Number(ch.CHAN_STATE_QUEUE)) return 'Queued';
  if (ch.CHAN_EVENT_N) return String(ch.CHAN_EVENT_N);
  return 'Unknown';
}
function statusClass(ch) {
  if (Number(ch.CHAN_STATE_HANGUP)) return 'st-hangup';
  if (Number(ch.CHAN_STATE_CONNECT)) return 'st-connect';
  if (Number(ch.CHAN_STATE_HOLD)) return 'st-hold';
  if (Number(ch.CHAN_STATE_QUEUE)) return 'st-queue';
  return 'st-unknown';
}

// UI helpers
function clearList() { channels.value = []; lastPayload.value = null; lastUpdate.value = null; }
function inspect(ch) { console.log('inspect channel', ch); alert(JSON.stringify(ch, null, 2)); }
function chIdxKey(ch) { return (ch && ch._uid) ? ch._uid : Math.random().toString(36).slice(2,8); }

// lifecycle
onMounted(() => {
  connect();
});
onBeforeUnmount(() => {
  disconnect();
});

// Expose for debug if needed
window.__QueueMonitor = { channels, connect, disconnect };

</script>

<style scoped>
.queue-monitor { font-family: Inter, Arial, sans-serif; max-width: 1100px; margin: 12px auto; }
.qm-header { display:flex; justify-content:space-between; align-items:center; margin-bottom: 8px; }
.status-row { display:flex; align-items:center; gap:8px; font-size: 0.95rem; color: #333; }
.dot { width:10px; height:10px; border-radius:50%; display:inline-block; }
.dot.on { background: #2ecc71; }
.dot.connecting { background: #f1c40f; }
.dot.off, .dot.error { background: #e74c3c; }

/* controls */
.controls { display:flex; justify-content:space-between; align-items:center; gap:12px; margin-bottom:12px; }
.controls .left { display:flex; gap:12px; align-items:center; }
.controls label { font-size: 0.9rem; display:flex; gap:8px; align-items:center; }
.controls select, .controls input { padding:6px 8px; border:1px solid #ccc; border-radius:6px; }

/* summary */
.summary { display:flex; gap:12px; margin-bottom:12px; }
.stat { background: #fff; padding:12px; border-radius:10px; box-shadow: 0 2px 6px rgba(0,0,0,0.06); width: 140px; text-align:center; }
.stat .num { font-size: 1.6rem; font-weight:700; color:#111; }
.stat .label { font-size:0.85rem; color:#666; }

/* table */
.table-wrapper { overflow:auto; max-height: 420px; border-radius:10px; background:#fff; padding:8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.channels-table { width:100%; border-collapse:collapse; font-size:0.95rem; }
.channels-table th, .channels-table td { text-align:left; padding:8px 10px; border-bottom:1px solid #eee; vertical-align:middle; }
.channels-table th { position: sticky; top:0; background:#fafafa; z-index:2; }
.mono { font-family: monospace; font-size:0.85rem; color:#333; }
.status-badge { padding:6px 8px; border-radius:6px; color:#fff; font-weight:600; font-size:0.85rem; display:inline-block; }
.st-queue { background:#f39c12; }
.st-connect { background:#2ecc71; }
.st-hold { background:#3498db; }
.st-hangup { background:#e74c3c; }
.st-unknown { background:#95a5a6; }
.no-data { text-align:center; padding:18px; color:#777; }

/* debug */
.debug { margin-top:12px; padding:8px; background:#fff; border-radius:8px; }
.debug pre { max-height:300px; overflow:auto; }

/* buttons */
.controls .right { display:flex; gap:8px; }
.controls button { padding:6px 10px; border-radius:6px; border:1px solid #bbb; background:#fff; cursor:pointer; }
.controls button:disabled { opacity:0.5; cursor:not-allowed; }
</style>

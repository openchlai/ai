// Utility functions for formatting data in the wallboard

export function getStatusText(ch) {
  if (Number(ch.CHAN_CAMPAIGN_WRAPUP)) return 'Wrapup'
  if (Number(ch.CHAN_STATE_QUEUE)) return 'In Queue'
  if (Number(ch.CHAN_STATE_HANGUP)) return 'Hangup'
  if (Number(ch.CHAN_STATE_CONNECT)) return 'On Call'
  if (Number(ch.CHAN_STATE_HOLD)) return 'On Hold'

  if (ch.CHAN_STATUS_TXT_) return String(ch.CHAN_STATUS_TXT_)

  // Agents waiting for calls
  if (ch.CHAN_EXTEN && ch.CHAN_EXTEN !== '--') return 'Waiting'

  // Default for anything that isn't an agent or on a call
  return 'IVR'
}

export function getDurationSeconds(ts) {
  if (!ts) return 0
  const now = Date.now()
  // Asterisk timestamps can be in seconds or milliseconds
  // If scientific notation or very small, it's likely seconds
  const start = Number(ts) < 1e11 ? Number(ts) * 1000 : Number(ts)
  return Math.floor(Math.max(0, now - start) / 1000)
}

export function formatDuration(ts) {
  if (!ts || ts === '--') return '--'
  const seconds = getDurationSeconds(ts)
  const h = Math.floor(seconds / 3600)
  const m = Math.floor((seconds % 3600) / 60)
  const s = seconds % 60

  if (h > 0) {
    return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  }
  return `${m}:${s.toString().padStart(2, '0')}`
}

export function formatNumberWithCommas(n) {
  if (n === undefined || n === null || n === '--') return '--'
  return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",")
}

export function getStatusClass(status) {
  const s = (status || 'Available').toString().toLowerCase()
  if (s.includes('on call') || s.includes('connected')) return 'status-oncall'
  if (s.includes('ring')) return 'status-ringing'
  if (s.includes('queue')) return 'status-inqueue'
  if (s.includes('ivr')) return 'status-inqueue' // Reuse queue styling for IVR
  if (s.includes('wrapup')) return 'status-ringing' // Reuse ringing/amber
  if (s.includes('available') || s.includes('waiting')) return 'status-available'
  return 'status-neutral'
}
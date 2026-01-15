// Utility functions for formatting data in the wallboard

export function getStatusText(ch) {
  // 1. Connection states take priority
  if (Number(ch.CHAN_STATE_CONNECT)) return 'On Call'
  if (Number(ch.CHAN_CAMPAIGN_WRAPUP)) return 'Wrapup'
  if (Number(ch.CHAN_STATE_HOLD)) return 'On Hold'
  if (Number(ch.CHAN_STATE_HANGUP)) return 'Hangup'

  // 2. Queue/Vector states (usually for callers)
  if (Number(ch.CHAN_STATE_QUEUE) || (ch.CHAN_VECTOR && ch.CHAN_VECTOR !== '--')) return 'In Queue'

  if (ch.CHAN_STATUS_TXT_) return String(ch.CHAN_STATUS_TXT_)

  // 3. Agents waiting for calls
  if (ch.CHAN_EXTEN && ch.CHAN_EXTEN !== '--') return 'Waiting'

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

export function formatCompactNumber(n) {
  if (n === undefined || n === null || n === '--') return '--'
  const num = Number(n)
  if (Number.isNaN(num)) return n

  if (num >= 1000000) {
    return (num / 1000000).toFixed(1).replace(/\.0$/, '') + 'M+'
  }
  if (num >= 1000) {
    return (num / 1000).toFixed(0) + 'K+' // K usually looks better without decimals for dashboard stats unless very small K
  }
  return formatNumberWithCommas(num)
}

export function getStatusClass(status) {
  const s = (status || 'Available').toString().toLowerCase()
  if (s.includes('on call') || s.includes('connected')) return 'status-oncall'
  if (s.includes('ring')) return 'status-ringing'
  if (s.includes('queue')) return 'status-inqueue'
  if (s.includes('ivr')) return 'status-inqueue'
  if (s.includes('wrapup')) return 'status-wrapup' // High visibility wrapup
  if (s.includes('available') || s.includes('waiting')) return 'status-available'
  return 'status-neutral'
}
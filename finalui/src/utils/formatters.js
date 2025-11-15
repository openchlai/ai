// Utility functions for formatting data in the wallboard

export function getStatusText(ch) {
  if (ch.CHAN_STATUS_TXT_) return String(ch.CHAN_STATUS_TXT_)
  if (Number(ch.CHAN_STATE_HANGUP)) return 'Hangup'
  if (Number(ch.CHAN_STATE_CONNECT)) return 'On Call'
  if (Number(ch.CHAN_STATE_HOLD)) return 'On Hold'
  if (Number(ch.CHAN_STATE_QUEUE)) return 'In Queue'
  return 'Available'
}

export function formatDuration(ts) {
  if (!ts) return '--'
  const now = Date.now()
  const start = Number(ts) < 1e11 ? Number(ts) * 1000 : Number(ts)
  const diff = Math.max(0, now - start)
  const minutes = Math.floor(diff / 60000)
  const seconds = Math.floor((diff % 60000) / 1000)
  return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
}

export function getCallStatusVariant(status) {
  const statusLower = status.toLowerCase()
  switch (statusLower) {
    case 'answered': return 'success'
    case 'abandoned': return 'warning'
    case 'missed': return 'danger'
    case 'noanswer': return 'danger'
    case 'voicemail': return 'info'
    case 'ivr': return 'primary'
    case 'dump': return 'secondary'
    default: return 'secondary'
  }
}

export function getStatusClass(status) {
  const s = (status || 'Available').toString().toLowerCase()
  if (s.includes('on call')) return 'status-oncall'
  if (s.includes('ring')) return 'status-ringing'
  if (s.includes('queue')) return 'status-inqueue'
  if (s.includes('available')) return 'status-available'
  if (s.includes('offline')) return 'status-offline'
  return 'status-neutral'
}

export function formatPhoneNumber(number) {
  if (!number || number === '--') return '--'
  // Basic phone number formatting - can be enhanced based on requirements
  const cleaned = number.replace(/\D/g, '')
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`
  }
  return number
}

export function formatTime(timestamp) {
  if (!timestamp) return '--'
  const date = new Date(timestamp)
  return date.toLocaleTimeString('en-US', { 
    hour: '2-digit', 
    minute: '2-digit', 
    second: '2-digit' 
  })
}

export function formatDate(timestamp) {
  if (!timestamp) return '--'
  const date = new Date(timestamp)
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

export function calculatePercentage(value, total) {
  if (!total || total === 0) return '0%'
  return `${Math.round((value / total) * 100)}%`
}

export function formatBytes(bytes) {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export function truncateText(text, maxLength = 50) {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}
<template>
  <div class="status-strip-inner">
    <!-- CRITICAL METRIC 1: QUEUE PRESSURE -->
    <div :class="['metric-unit', { 'breach': callsInQueue >= 5 }]">
      <div class="unit-label">Calls in Queue</div>
      <div class="unit-value">{{ callsInQueue }}</div>
    </div>

    <!-- CRITICAL METRIC 2: DELAY PRESSURE -->
    <div :class="['metric-unit', { 'breach': longestWaitSeconds >= 300 }]">
      <div class="unit-label">Longest Wait</div>
      <div class="unit-value">{{ formatSeconds(longestWaitSeconds) }}</div>
    </div>

    <!-- CRITICAL METRIC 3: RESOURCE CAPACITY -->
    <div :class="['metric-unit', { 'breach': availableAgents === 0 }]">
      <div class="unit-label">Available Agents</div>
      <div class="unit-value">{{ availableAgents }}</div>
    </div>
  </div>
</template>

<script>
import { formatNumberWithCommas } from '../utils/formatters'

export default {
  name: 'OperationalKPIs',
  props: {
    callsInQueue: { type: Number, default: 0 },
    longestWaitSeconds: { type: Number, default: 0 },
    activeCalls: { type: Number, default: 0 },
    availableAgents: { type: Number, default: 0 },
    hangupCards: { type: Array, default: () => [] },
    serviceLevel: { type: Number, default: 0 },
    voiceLoad: { type: Number, default: 0 },
    waLoad: { type: Number, default: 0 }
  },
  setup() {
    const formatSeconds = (s) => {
      if (!s) return '00:00'
      const mins = Math.floor(s / 60)
      const secs = s % 60
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }

    const calculateOffset = (count) => {
      const circumference = 2 * Math.PI * 40
      const percentage = Math.min(count / 500, 1)
      return circumference * (1 - percentage)
    }

    const getQueueStatus = (n) => {
      if (n >= 5) return 'critical-bg'
      if (n >= 2) return 'warning-bg'
      return 'ok-bg'
    }
    const getQueueLabel = (n) => n >= 5 ? 'CRITICAL BACKLOG' : (n >= 2 ? 'ATTENTION REQUIRED' : 'NORMAL')

    const getWaitStatus = (s) => {
      if (s >= 300) return 'critical-text'
      if (s >= 120) return 'warning-text'
      return 'ok-text'
    }
    const getWaitLabel = (s) => s >= 300 ? 'OVER THRESHOLD' : (s >= 120 ? 'DELAYED' : 'ON TRACK')

    const getAgentsStatus = (n) => {
      if (n === 0) return 'critical-bg'
      if (n === 1) return 'warning-bg'
      return 'ok-bg'
    }
    const getAgentsLabel = (n) => n === 0 ? 'NO CAPACITY' : (n === 1 ? 'LOW CAPACITY' : 'STABLE')

    const getSLColor = (sl) => {
      if (sl < 80) return 'var(--status-critical)'
      if (sl < 90) return 'var(--status-warning)'
      return 'var(--status-ok)'
    }

    return { 
      formatSeconds, calculateOffset,
      getQueueStatus, getQueueLabel,
      getWaitStatus, getWaitLabel,
      getAgentsStatus, getAgentsLabel,
      getSLColor,
      formatNumberWithCommas
    }
  }
}
</script>

<style scoped>
.status-strip-inner {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  width: 100%;
}

.metric-unit {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 10px;
  border-right: 1px solid var(--status-neutral);
}

.metric-unit:last-child { border-right: none; }

.unit-label {
  font-size: 1rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: var(--text-muted);
  margin-bottom: 5px;
}

.unit-value {
  font-size: 8rem;
  font-weight: 900;
  line-height: 1;
  color: var(--text-main);
  font-variant-numeric: tabular-nums;
  letter-spacing: -4px;
}

/* Breach Enforcement: RED only for action-required states */
.metric-unit.breach {
  background: #fffafa; /* Extremely subtle tint to differentiate without neon glow */
}

.metric-unit.breach .unit-value {
  color: var(--brand-red);
}

.metric-unit.breach .unit-label {
  color: var(--brand-red);
}

@media screen and (min-width: 1920px) {
  .unit-value { font-size: 11rem; }
  .unit-label { font-size: 1.2rem; }
  .metric-unit { padding: 40px 10px; }
}
</style>

<template>
  <div class="operational-kpis">
    <!-- Row 1: The Big 4 Situational Metrics -->
    <div class="kpi-grid primary">
      <div :class="['kpi-card', getQueueStatus(callsInQueue)]">
        <div class="kpi-header">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
          <span class="kpi-label">CALLS IN QUEUE</span>
        </div>
        <div class="kpi-value">{{ formatNumberWithCommas(callsInQueue) }}</div>
        <div class="kpi-footer" v-if="callsInQueue > 0">
          <span class="status-badge">{{ getQueueLabel(callsInQueue) }}</span>
        </div>
      </div>

      <div :class="['kpi-card', getWaitStatus(longestWaitSeconds)]">
        <div class="kpi-header">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
          <span class="kpi-label">LONGEST WAIT</span>
        </div>
        <div class="kpi-value">{{ formatSeconds(longestWaitSeconds) }}</div>
        <div class="kpi-footer">
          <span class="status-badge">{{ getWaitLabel(longestWaitSeconds) }}</span>
        </div>
      </div>

      <div class="kpi-card info">
        <div class="kpi-header">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l2.11-2.12a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
          <span class="kpi-label">ACTIVE CALLS</span>
        </div>
        <div class="kpi-value">{{ formatNumberWithCommas(activeCalls) }}</div>
        <div class="kpi-footer">Talking Now</div>
      </div>

      <div :class="['kpi-card', getAgentsStatus(availableAgents)]">
        <div class="kpi-header">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="8.5" cy="7" r="4"></circle><polyline points="17 11 19 13 23 9"></polyline></svg>
          <span class="kpi-label">AVAILABLE AGENTS</span>
        </div>
        <div class="kpi-value">{{ formatNumberWithCommas(availableAgents) }}</div>
        <div class="kpi-footer">
          <span class="status-badge">{{ getAgentsLabel(availableAgents) }}</span>
        </div>
      </div>
    </div>

    <!-- Row 2: Hangup Status & Load Breakdown -->
    <div class="kpi-grid secondary">
      <div class="status-rings-container">
        <div v-for="card in hangupCards" :key="card.id" class="ring-card">
          <svg viewBox="0 0 100 100" class="mini-ring">
            <circle class="ring-track" cx="50" cy="50" r="40"></circle>
            <circle 
              class="ring-fill" 
              cx="50" cy="50" r="40"
              :style="{ 
                strokeDashoffset: calculateOffset(card.count),
                stroke: card.color 
              }"
            ></circle>
          </svg>
          <div class="ring-info">
            <div class="ring-value" :style="{ color: card.color }">{{ formatNumberWithCommas(card.count) }}</div>
            <div class="ring-label">{{ card.label }}</div>
          </div>
        </div>
      </div>

      <div class="kpi-card-sm channel-load">
        <div class="meta-label">CHANNEL LOAD</div>
        <div class="channel-bars">
          <div class="channel-row">
            <span>Voice</span>
            <div class="bar-track"><div class="bar-fill blue" :style="{ width: voiceLoad + '%' }"></div></div>
          </div>
          <div class="channel-row">
            <span>WhatsApp</span>
            <div class="bar-track"><div class="bar-fill green" :style="{ width: waLoad + '%' }"></div></div>
          </div>
        </div>
      </div>
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
.operational-kpis {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  margin: 0 10px;
}

.kpi-grid {
  display: grid;
  gap: var(--spacing-md);
}

.kpi-grid.primary {
  grid-template-columns: repeat(4, 1fr);
}

.kpi-grid.secondary {
  grid-template-columns: 1fr 340px;
}

/* Base Card Styling */
.kpi-card {
  background: var(--card-bg);
  border-radius: var(--border-radius-lg);
  padding: 18px 25px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: var(--shadow-md);
  border: 2px solid var(--border-color);
  min-height: 190px;
  width: 100%;
  box-sizing: border-box;
}

.kpi-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-secondary);
}

.kpi-header svg {
  width: 18px;
  height: 18px;
  stroke: currentColor;
}

.kpi-label {
  font-size: 0.9rem;
  font-weight: 800;
  letter-spacing: 0.5px;
}

.kpi-value {
  font-size: 3.5rem;
  font-weight: 900;
  line-height: 1;
  margin: 5px 0;
  font-variant-numeric: tabular-nums;
}

.kpi-footer {
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
}

/* Status Rings Styles */
.status-rings-container {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  background: var(--card-bg);
  padding: 12px 16px;
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  width: 100%;
  box-sizing: border-box;
}

.ring-card {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mini-ring {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
}

.ring-track {
  fill: none;
  stroke: var(--soft-gray);
  stroke-width: 10;
}

.ring-fill {
  fill: none;
  stroke-width: 10;
  stroke-linecap: round;
  stroke-dasharray: 251.3; /* 2 * PI * 40 */
  transition: stroke-dashoffset 1s ease;
}

.ring-info {
  display: flex;
  flex-direction: column;
}

.ring-value {
  font-size: 1.25rem;
  font-weight: 900;
  line-height: 1;
}

.ring-label {
  font-size: 0.6rem;
  font-weight: 800;
  color: var(--text-secondary);
  text-transform: uppercase;
}

.kpi-card-sm {
  background: var(--card-bg);
  border-radius: var(--border-radius-md);
  padding: 12px 20px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.meta-label {
  font-size: 0.75rem;
  font-weight: 800;
  color: var(--text-secondary);
  margin-bottom: 2px;
}

.channel-bars {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.channel-row {
  display: grid;
  grid-template-columns: 60px 1fr;
  align-items: center;
  gap: 8px;
  font-size: 0.65rem;
  font-weight: 800;
}

.bar-track { height: 6px; }
.bar-fill { height: 100%; }

/* Status variants (re-styled for compact) */
.ok-bg { border-color: var(--status-ok); color: var(--status-ok); }
.warning-bg { background-color: var(--status-warning); border-color: var(--status-warning); color: white; }
.warning-bg .kpi-header, .warning-bg .kpi-label { color: rgba(255,255,255,0.9); }
.critical-bg { background-color: var(--status-critical); border-color: var(--status-critical); color: white; animation: subtle-shake 0.5s infinite alternate; }
.critical-bg .kpi-header, .critical-bg .kpi-label { color: rgba(255,255,255,0.9); }

@keyframes subtle-shake {
  from { transform: translateX(-0.5px); }
  to { transform: translateX(0.5px); }
}

/* TV Optimization */
@media screen and (min-width: 1920px) {
  .kpi-value { font-size: 4.5rem; }
  .ring-value { font-size: 1.5rem; }
  .ring-label { font-size: 0.7rem; }
  .mini-ring { width: 50px; height: 50px; }
}
</style>

<template>
  <div class="top-stats-row">
    <!-- CALLS IN QUEUE -->
    <div :class="['stat-card', getQueueClass(callsInQueue)]">
      <div class="stat-header">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
        <span class="stat-title">CALLS IN QUEUE</span>
      </div>
      <div class="stat-main">
        <div class="stat-value">{{ callsInQueue }}</div>
      </div>
      <div class="stat-footer">
        {{ getQueueLabel(callsInQueue) }}
      </div>
    </div>

    <!-- LONGEST WAIT -->
    <div :class="['stat-card', getWaitClass(longestWaitSeconds)]">
      <div class="stat-header">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
        <span class="stat-title">LONGEST WAIT</span>
      </div>
      <div class="stat-main">
        <div class="stat-value">{{ formatSeconds(longestWaitSeconds) }}</div>
      </div>
      <div class="stat-footer">
        {{ getWaitLabel(longestWaitSeconds) }}
      </div>
    </div>

    <!-- ACTIVE CALLS -->
    <div class="stat-card info">
      <div class="stat-header">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
        <span class="stat-title">ACTIVE CALLS</span>
      </div>
      <div class="stat-main">
        <div class="stat-value">{{ activeCalls }}</div>
      </div>
      <div class="stat-footer">
        TALKING NOW
      </div>
    </div>

    <!-- AVAILABLE AGENTS -->
    <div :class="['stat-card', getAgentsClass(availableAgents)]">
      <div class="stat-header">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><line x1="19" y1="8" x2="19" y2="14"></line><line x1="22" y1="11" x2="16" y2="11"></line></svg>
        <span class="stat-title">AVAILABLE AGENTS</span>
      </div>
      <div class="stat-main">
        <div class="stat-value">{{ availableAgents }}</div>
      </div>
      <div class="stat-footer">
        {{ getAgentsLabel(availableAgents) }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TopStatsRow',
  props: {
    callsInQueue: { type: Number, default: 0 },
    longestWaitSeconds: { type: Number, default: 0 },
    activeCalls: { type: Number, default: 0 },
    availableAgents: { type: Number, default: 0 }
  },
  setup() {
    const formatSeconds = (s) => {
      if (!s) return '00:00'
      const mins = Math.floor(s / 60)
      const secs = s % 60
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }

    const getQueueLabel = (n) => n >= 10 ? 'CRITICAL BACKLOG' : (n >= 5 ? 'HEAVY TRAFFIC' : (n >= 1 ? 'ATTENTION' : 'STABLE'))
    const getWaitLabel = (s) => s >= 300 ? 'OVER THRESHOLD' : (s >= 60 ? 'WARNING' : 'STABLE')
    const getAgentsLabel = (n) => n === 0 ? 'NO CAPACITY' : (n <= 2 ? 'LOW CAPACITY' : 'STABLE')

    const getQueueClass = (n) => n >= 5 ? 'critical' : (n >= 1 ? 'warning' : 'success')
    const getWaitClass = (s) => s >= 300 ? 'critical' : (s >= 60 ? 'warning' : 'success')
    const getAgentsClass = (n) => n === 0 ? 'critical' : (n <= 2 ? 'warning' : 'success')

    return { 
      formatSeconds, 
      getQueueLabel, getWaitLabel, getAgentsLabel,
      getQueueClass, getWaitClass, getAgentsClass 
    }
  }
}
</script>

<style scoped>
.top-stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  width: 100%;
}

.stat-card {
  background: white;
  border-radius: var(--border-radius-md);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 160px;
  transition: all 0.3s ease;
  border: 1px solid var(--border-color);
}

.stat-header {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--text-muted);
}

.stat-title {
  font-size: 0.8rem;
  font-weight: 800;
  letter-spacing: 0.05em;
}

.stat-main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px 0;
}

.stat-value {
  font-size: clamp(2rem, 5vw, 4rem);
  font-weight: 900;
  color: var(--text-main);
  line-height: 1;
}

.stat-footer {
  font-size: clamp(0.65rem, 1.25vw, 0.85rem);
  font-weight: 700;
  color: var(--text-muted);
  letter-spacing: 0.02em;
}

/* Dynamic State Styling - Ensuring high-vibrancy alerts */
.stat-card.critical { background: var(--danger-color); border-color: var(--danger-color); }
.stat-card.warning { background: var(--secondary-color); border-color: var(--secondary-color); }
.stat-card.success { background: var(--success-color); border-color: var(--success-color); }
.stat-card.info { background: var(--primary-color); border-color: var(--primary-color); }

.stat-card.critical .stat-header, .stat-card.critical .stat-value, .stat-card.critical .stat-footer,
.stat-card.warning .stat-header, .stat-card.warning .stat-value, .stat-card.warning .stat-footer,
.stat-card.success .stat-header, .stat-card.success .stat-value, .stat-card.success .stat-footer,
.stat-card.info .stat-header, .stat-card.info .stat-value, .stat-card.info .stat-footer {
  color: white !important;
}

/* Dark Mode Overrides - Only for neutral cards */
.dark-mode .stat-card:not(.critical):not(.warning):not(.success):not(.info) {
  background: var(--card-bg);
  border-color: var(--border-color);
}

.dark-mode .stat-card:not(.critical):not(.warning):not(.success):not(.info) .stat-value { color: white; }
.dark-mode .stat-card:not(.critical):not(.warning):not(.success):not(.info) .stat-title { color: #9ca3af; }

@media (max-width: 1280px) {
  .stat-value { font-size: 2.8rem; }
  .stat-card { padding: 16px; min-height: 140px; }
}
</style>
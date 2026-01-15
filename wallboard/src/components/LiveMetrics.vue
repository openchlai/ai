<template>
  <div class="live-metrics-container">
    <div class="metric-card incoming">
      <div class="metric-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l2.11-2.12a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
        <div class="status-dot pulsing"></div>
      </div>
      <div class="metric-info">
        <div class="metric-value">{{ incomingCalls }}</div>
        <div class="metric-label">INCOMING CALLS</div>
      </div>
    </div>

    <div class="metric-card active">
      <div class="metric-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
      </div>
      <div class="metric-info">
        <div class="metric-value">{{ counselorsOnline }}</div>
        <div class="metric-label">COUNSELLORS ONLINE</div>
      </div>
    </div>

    <div class="metric-card busy">
      <div class="metric-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M15.05 5A5 5 0 0 1 19 8.95M15.05 1A9 9 0 0 1 23 8.94m-1 7.98v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l2.11-2.12a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
      </div>
      <div class="metric-info">
        <div class="metric-value">{{ counselorsOnCall }}</div>
        <div class="metric-label">COUNSELLORS ON CALL</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LiveMetrics',
  props: {
    incomingCalls: { type: Number, default: 0 },
    counselorsOnline: { type: Number, default: 0 },
    counselorsOnCall: { type: Number, default: 0 }
  }
}
</script>

<style scoped>
.live-metrics-container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-sm);
}

.metric-card {
  background: var(--card-bg);
  border-radius: var(--border-radius-lg);
  padding: 16px 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  border: 1px solid var(--border-color);
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
}

.metric-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
}

.incoming::before { background: var(--secondary-color); }
.active::before { background: var(--primary-color); }
.busy::before { background: var(--success-color); }

.metric-icon {
  width: 48px;
  height: 48px;
  background: var(--light-blue);
  color: var(--primary-color);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  flex-shrink: 0;
}

.metric-icon svg {
  width: 24px;
  height: 24px;
}

.status-dot {
  position: absolute;
  top: -4px;
  right: -4px;
  width: 12px;
  height: 12px;
  background: #ef4444;
  border-radius: 50%;
  border: 2px solid white;
}

.pulsing {
  animation: pulse-red 2s infinite;
}

@keyframes pulse-red {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}

.metric-info {
  display: flex;
  flex-direction: column;
}

.metric-value {
  font-size: 2.5rem;
  font-weight: 900;
  line-height: 1;
  color: var(--text-primary);
}

.metric-label {
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 1px;
  color: var(--text-secondary);
  text-transform: uppercase;
  margin-top: 4px;
}

/* TV Optimization */
@media screen and (min-width: 1920px) {
  .metric-value { font-size: 3.25rem; }
  .metric-label { font-size: 0.9rem; }
  .metric-card { padding: 24px 30px; }
}
</style>

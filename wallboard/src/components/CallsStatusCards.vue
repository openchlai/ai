<template>
  <div class="calls-stats-section">
    <div v-if="loading && cards.length === 0" class="loading-state">
      <div class="skeleton-card" v-for="i in 8" :key="i"></div>
    </div>
    
    <div v-else-if="error && cards.length === 0" class="error-state">
      <p>Error loading call statistics: {{ error }}</p>
    </div>
    
    <div 
      v-else
      class="calls-cards-grid"
    >
      <div 
        v-for="card in cards" 
        :key="card.id"
        class="status-card-horizontal"
      >
        <div class="card-icon-side" :style="{ backgroundColor: card.color }">
          <div class="status-icon" v-html="getIcon(card.status)"></div>
        </div>
        <div class="card-content-side">
          <div class="card-label">{{ card.label }}</div>
          <div class="card-count">{{ card.count }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CallsStatusCards',
  props: {
    loading: { type: Boolean, default: false },
    error: { type: String, default: null },
    cards: { type: Array, required: true, default: () => [] }
  },
  setup() {
    const getIcon = (status) => {
      const s = String(status).toUpperCase()
      const icons = {
        'ANSWERED': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M9 11l3 3L22 4m-2 16H4a2 2 0 01-2-2V4a2 2 0 012-2h9l-3 3H4v14h14v-7l3-3v10a2 2 0 01-2 2z"></path></svg>`,
        'ABANDONED': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M16 8l-4 4m0 0l-4 4m4-4l4 4m-4-4l-4-4M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
        'DUMP': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18.36 6.64a9 9 0 11-12.73 0M12 2v10"></path></svg>`,
        'IVR': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"></path></svg>`,
        'MISSED': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
        'NOANSWER': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`,
        'VOICEMAIL': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"></path></svg>`,
        'TOTAL': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M4 6h16M4 10h16M4 14h16M4 18h16"></path></svg>`
      }
      return icons[s] || `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path></svg>` // Fallback phone
    }
    return { getIcon }
  }
}
</script>

<style scoped>
.calls-stats-section {
  width: 100%;
}

.calls-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}

.status-card-horizontal {
  display: flex;
  background: var(--card-bg);
  border-radius: var(--border-radius-sm);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  height: 60px;
  transition: transform 0.2s ease;
}

.status-card-horizontal:hover {
  transform: translateY(-1px);
}

.card-icon-side {
  width: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}

.phone-icon {
  width: 18px;
  height: 18px;
}

.card-content-side {
  flex-grow: 1;
  padding: 8px 12px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.card-label {
  font-size: 0.65rem;
  font-weight: 800;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 2px;
}

.card-count {
  font-size: clamp(1rem, 2.5vw, 1.8rem);
  font-weight: 900;
  color: var(--text-main);
  line-height: 1;
}

@media screen and (min-width: 1440px) {
  .calls-cards-grid {
    grid-template-columns: repeat(7, 1fr);
  }
}

@media screen and (min-width: 1920px) {
  .status-card-horizontal { height: clamp(60px, 6vh, 80px); }
  .card-icon-side { width: clamp(42px, 5vw, 60px); }
  .phone-icon { width: clamp(18px, 2vw, 24px); height: clamp(18px, 2vw, 24px); }
}

.loading-state {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 12px;
}

.skeleton-card {
  height: 60px;
  background: var(--border-color);
  opacity: 0.2;
  border-radius: var(--border-radius-sm);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}
</style>
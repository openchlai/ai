<template>
  <div class="calls-stats-section">
    <div class="section-header">
      <h2 class="section-title">TODAY'S CALL STATUS</h2>
    </div>
    
    <div v-if="loading" class="loading-state">
      <div class="skeleton-ring" v-for="i in 6" :key="i"></div>
    </div>
    
    <div v-else-if="error" class="error-state">
      <p>Error loading call statistics: {{ error }}</p>
    </div>
    
    <div 
      v-else
      class="calls-cards-grid"
    >
      <div 
        v-for="card in cards" 
        :key="card.id"
        :class="['call-status-infographic', `card-${card.variant}`]"
      >
        <div class="infographic-container">
          <svg viewBox="0 0 100 100" class="progress-ring">
            <circle class="ring-track" cx="50" cy="50" r="45"></circle>
            <circle 
              class="ring-fill" 
              cx="50" cy="50" r="45"
              :style="{ 
                strokeDashoffset: calculateOffset(card.count),
                stroke: getVariantColor(card.variant) 
              }"
            ></circle>
          </svg>
          <div class="infographic-content">
            <div class="card-count" :style="{ color: getVariantColor(card.variant) }">{{ card.count }}</div>
            <div class="card-label">{{ card.label }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CallsStatusCards',
  props: {
    loading: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: null
    },
    cards: {
      type: Array,
      required: true,
      default: () => []
    }
  },
  setup() {
    const calculateOffset = (count) => {
      // Normalize count for visualization (max 500 for full ring for better visual impact)
      const circumference = 2 * Math.PI * 45
      const percentage = Math.min(count / 500, 1)
      return circumference * (1 - percentage)
    }

    const getVariantColor = (variant) => {
      const colors = {
        'success': 'var(--success-color)',
        'warning': 'var(--warning-color)',
        'danger': 'var(--danger-color)',
        'info': '#06b6d4',
        'primary': 'var(--primary-color)',
        'secondary': 'var(--dark-gray)'
      }
      return colors[variant] || 'var(--primary-color)'
    }

    return { calculateOffset, getVariantColor }
  }
}
</script>

<style scoped>
.calls-stats-section {
  width: 100%;
}

.section-header {
  margin-bottom: var(--spacing-sm);
}

.section-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--primary-color);
  margin: 0;
}

.calls-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--spacing-md);
  margin-top: var(--spacing-sm);
}

.call-status-infographic {
  background: var(--card-bg);
  border-radius: var(--border-radius-lg);
  padding: 16px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  transition: var(--transition-smooth);
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.infographic-container {
  position: relative;
  width: 100%;
  aspect-ratio: 1 / 1;
}

.progress-ring {
  width: 100%;
  height: 100%;
}

.ring-track {
  fill: none;
  stroke: var(--light-blue);
  stroke-width: 8;
}

.ring-fill {
  fill: none;
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 282.7; /* 2 * PI * 45 */
  transition: stroke-dashoffset 1.5s cubic-bezier(0.4, 0, 0.2, 1);
}

.infographic-content {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.card-count {
  font-size: 2rem;
  font-weight: 800;
  line-height: 1;
  margin-bottom: 2px;
}

.card-label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-secondary);
  max-width: 80px;
}

.loading-state {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--spacing-md);
}

.skeleton-ring {
  aspect-ratio: 1 / 1;
  border-radius: 50%;
  background: var(--soft-gray);
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

/* TV Optimization */
@media screen and (min-width: 1920px) {
  .card-count {
    font-size: 2.5rem;
  }
  .card-label {
    font-size: 0.85rem;
  }
}
</style>
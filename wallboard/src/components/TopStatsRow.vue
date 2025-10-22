<template>
  <div class="top-stats-row">
    <div 
      v-for="stat in stats" 
      :key="stat.id" 
      :class="['stat-card', stat.variant]"
    >
      <div class="stat-content">
        <div class="stat-label">{{ stat.title.toUpperCase() }}</div>
        <div class="stat-value">{{ stat.value }}</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TopStatsRow',
  props: {
    stats: {
      type: Array,
      required: true,
      default: () => []
    }
  }
}
</script>

<style scoped>
.top-stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
  margin: 20px 0;
}

.stat-card {
  background: #ffffff;
  border-radius: 10px;
  padding: 16px;
  text-align: center;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  border-left: 4px solid transparent;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.dark-mode .stat-card {
  background: #2d3748;
  color: #e2e8f0;
}

.stat-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.5px;
  opacity: 0.8;
  color: #6b7280;
}

.dark-mode .stat-label {
  color: #9ca3af;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  line-height: 1;
}

/* Stat variants with color themes */
.stat-card.total {
  border-left-color: #6b7280;
}

.stat-card.total .stat-value {
  color: #6b7280;
}

.stat-card.answered {
  border-left-color: #10b981;
}

.stat-card.answered .stat-value {
  color: #10b981;
}

.stat-card.abandoned {
  border-left-color: #f59e0b;
}

.stat-card.abandoned .stat-value {
  color: #f59e0b;
}

.stat-card.discarded {
  border-left-color: #ef4444;
}

.stat-card.discarded .stat-value {
  color: #ef4444;
}

.stat-card.missed {
  border-left-color: #dc2626;
}

.stat-card.missed .stat-value {
  color: #dc2626;
}

.stat-card.ivr {
  border-left-color: #3b82f6;
}

.stat-card.ivr .stat-value {
  color: #3b82f6;
}

.stat-card.beep {
  border-left-color: #8b5cf6;
}

.stat-card.beep .stat-value {
  color: #8b5cf6;
}

/* Pulse animation for active stats */
.stat-card.answered,
.stat-card.ivr {
  animation: subtle-pulse 3s ease-in-out infinite;
}

@keyframes subtle-pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
}

/* Responsive design */
@media (max-width: 768px) {
  .top-stats-row {
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
    gap: 12px;
  }
  
  .stat-card {
    padding: 12px;
  }
  
  .stat-label {
    font-size: 0.7rem;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
}

@media (max-width: 480px) {
  .top-stats-row {
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
  }
  
  .stat-card {
    padding: 10px;
  }
  
  .stat-label {
    font-size: 0.65rem;
  }
  
  .stat-value {
    font-size: 1.25rem;
  }
}
</style>
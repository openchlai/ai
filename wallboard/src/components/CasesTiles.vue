<template>
  <div class="cases-grid">
    <div 
      v-for="tile in tiles" 
      :key="tile.id" 
      :class="['case-card', tile.variant]"
    >
      <div class="case-inner">
        <div v-if="tile.value" class="case-value">{{ tile.value }}</div>
        <div class="case-label">{{ tile.label }}</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CasesTiles',
  props: {
    tiles: {
      type: Array,
      required: true,
      default: () => []
    }
  }
}
</script>

<style scoped>
.cases-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.case-card {
  background: #ffffff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.case-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.dark-mode .case-card {
  background: #2d3748;
  color: #e2e8f0;
}

.case-inner {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.case-value {
  font-size: 2.5rem;
  font-weight: 700;
  line-height: 1;
}

.case-label {
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  opacity: 0.8;
}

/* Variant colors */
.case-card.c-blue .case-value {
  color: #3b82f6;
}

.case-card.c-amber .case-value {
  color: #f59e0b;
}

.case-card.c-red .case-value {
  color: #ef4444;
}

.case-card.c-green .case-value {
  color: #10b981;
}

.case-card.c-black .case-value {
  color: #1f2937;
}

.dark-mode .case-card.c-black .case-value {
  color: #f9fafb;
}

/* Variant background accents */
.case-card.c-blue::before {
  background: linear-gradient(45deg, #3b82f6, #60a5fa);
}

.case-card.c-amber::before {
  background: linear-gradient(45deg, #f59e0b, #fbbf24);
}

.case-card.c-red::before {
  background: linear-gradient(45deg, #ef4444, #f87171);
}

.case-card.c-green::before {
  background: linear-gradient(45deg, #10b981, #34d399);
}

.case-card.c-black::before {
  background: linear-gradient(45deg, #1f2937, #374151);
}

.case-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  opacity: 0.8;
}

/* Responsive design */
@media (max-width: 768px) {
  .cases-grid {
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 15px;
    margin: 15px 0;
  }
  
  .case-card {
    padding: 20px;
  }
  
  .case-value {
    font-size: 2rem;
  }
  
  .case-label {
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .cases-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .case-card {
    padding: 16px;
  }
  
  .case-value {
    font-size: 1.8rem;
  }
}
</style>
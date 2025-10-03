<template>
  <div class="cases-container">
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
.cases-container {
  height: 100%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
}

.cases-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(3, 1fr);
  gap: 12px;
  height: 100%;
  width: 100%;
  max-width: 100%;
}

.case-card {
  background: #ffffff;
  border-radius: 8px;
  padding: 16px 12px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 0;
}

.dark-mode .case-card {
  background: #2d3748;
  color: #e2e8f0;
}

.case-inner {
  display: flex;
  flex-direction: column;
  gap: 4px;
  text-align: center;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.case-value {
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 4px;
  color: #ffffff !important;
}

.case-label {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  opacity: 0.9;
  line-height: 1.2;
  text-align: center;
  word-wrap: break-word;
  hyphens: auto;
  max-width: 100%;
  color: #ffffff !important;
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
  height: 2px;
  opacity: 0.8;
}

/* TV Screen optimizations */
@media screen and (min-width: 1920px) {
  .cases-container {
    padding: 15px;
  }
  
  .cases-grid {
    gap: 15px;
  }
  
  .case-card {
    padding: 20px 16px;
    border-radius: 10px;
  }
  
  .case-value {
    font-size: 2.25rem;
  }
  
  .case-label {
    font-size: 0.8rem;
  }
}

/* 4K TV optimization */
@media screen and (min-width: 3840px) {
  .cases-container {
    padding: 20px;
  }
  
  .cases-grid {
    gap: 20px;
  }
  
  .case-card {
    padding: 25px 20px;
    border-radius: 12px;
  }
  
  .case-inner {
    gap: 6px;
  }
  
  .case-value {
    font-size: 3rem;
    margin-bottom: 6px;
  }
  
  .case-label {
    font-size: 1rem;
    letter-spacing: 0.5px;
  }
  
  .case-card::before {
    height: 4px;
  }
}

/* Smaller TV screens */
@media screen and (max-width: 1600px) {
  .cases-container {
    padding: 10px;
  }
  
  .cases-grid {
    gap: 10px;
  }
  
  .case-card {
    padding: 14px 10px;
  }
  
  .case-value {
    font-size: 1.5rem;
  }
  
  .case-label {
    font-size: 0.65rem;
  }
}

/* Very small screens */
@media screen and (max-width: 1200px) {
  .case-card {
    padding: 12px 8px;
  }
  
  .case-value {
    font-size: 1.3rem;
  }
  
  .case-label {
    font-size: 0.6rem;
  }
}

/* Mobile fallback - stack vertically */
@media screen and (max-width: 768px) {
  .cases-grid {
    grid-template-columns: 1fr;
    grid-template-rows: repeat(6, 1fr);
    gap: 8px;
  }
  
  .case-card {
    padding: 12px 8px;
  }
  
  .case-value {
    font-size: 1.4rem;
  }
  
  .case-label {
    font-size: 0.65rem;
  }
}

/* Animation for smooth tile updates - reduced for TV */
@keyframes tileUpdate {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.01);
  }
  100% {
    transform: scale(1);
  }
}

.case-card {
  animation: tileUpdate 0.2s ease-in-out;
}
</style>
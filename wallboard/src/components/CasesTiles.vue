<template>
  <div class="cases-container">
    <div class="cases-grid">
      <div
        v-for="tile in tiles"
        :key="tile.id"
        :class="['case-card', tile.variant]"
      >
        <div class="case-icon-wrapper" v-html="getIcon(tile.id)"></div>
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
  },
  setup() {
    const getIcon = (id) => {
      const icons = {
        'ct1': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l2.11-2.12a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>`,
        'ct2': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>`,
        'ct3': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>`,
        'ct4': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>`,
        'ct5': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 18v-6a9 9 0 0 1 18 0v6"></path><path d="M21 19a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3zM3 19a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H3z"></path></svg>`,
        'ct6': `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="9" y1="21" x2="9" y2="9"></line></svg>`
      }
      return icons[id] || icons['ct1']
    }

    return { getIcon }
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
  background: var(--card-bg);
  border-radius: var(--border-radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-md);
  transition: var(--transition-smooth);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 0;
  border: 1px solid var(--border-color);
  gap: 12px;
}

.case-icon-wrapper {
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  margin-bottom: 4px;
}

.case-icon-wrapper svg {
  width: 24px;
  height: 24px;
}

.case-inner {
  display: flex;
  flex-direction: column;
  gap: 2px;
  text-align: center;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.case-value {
  font-size: 3.5rem; /* Increased from 2.5rem */
  font-weight: 900;
  line-height: 1;
  color: #ffffff; 
}

.case-label {
  font-size: 1.1rem; /* Increased from 0.95rem */
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  line-height: 1.2;
  text-align: center;
  color: rgba(255, 255, 255, 0.9);
}

/* Base white text for all variant-accented cards */
.case-card .case-value,
.case-card .case-label {
  color: #ffffff;
}

.case-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
}

.case-card.c-blue::before { background: #1D3E8A; }
.case-card.c-amber::before { background: #F47C20; }
.case-card.c-red::before { background: #dc2626; }
.case-card.c-green::before { background: #15803d; }
.case-card.c-black::before { background: #4A4A4A; }

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
  /* animation removed for stability */
}
</style>
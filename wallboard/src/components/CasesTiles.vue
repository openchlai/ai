<template>
  <div class="cases-tiles-grid">
    <div
      v-for="tile in tiles"
      :key="tile.id"
      :class="['case-tile', tile.variant]"
    >
      <div class="tile-icon" v-html="getIcon(tile.id)"></div>
      <div class="tile-content">
        <div class="tile-value">{{ tile.value }}</div>
        <div class="tile-label">{{ tile.label }}</div>
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
.cases-tiles-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-auto-rows: 1fr;
  gap: 16px;
  height: 100%;
}

.case-tile {
  border-radius: var(--border-radius-lg);
  padding: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: white;
  box-shadow: var(--shadow-md);
  transition: transform 0.2s ease;
}

.case-tile:hover {
  transform: translateY(-2px);
}

.tile-icon {
  margin-bottom: 8px;
  opacity: 0.9;
}

.tile-icon :deep(svg) {
  width: 32px;
  height: 32px;
}

.tile-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tile-value {
  font-size: clamp(1.2rem, 2.5vw, 3rem);
  font-weight: 900;
  line-height: 1;
}

.tile-label {
  font-size: clamp(0.55rem, 1vw, 0.85rem);
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.9;
}

/* Fluid Scaling for TV & Varying Viewports */
.tile-icon :deep(svg) {
  width: clamp(24px, 4vw, 48px);
  height: clamp(24px, 4vw, 48px);
}

.case-tile {
  padding: clamp(12px, 2vw, 24px);
  border-radius: var(--border-radius-lg);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: white;
  box-shadow: var(--shadow-md);
  transition: transform 0.2s ease;
  min-height: 0;
}

/* Variant Backgrounds - Restoring Brand Gradients */
.case-tile.c-blue { background: linear-gradient(135deg, #1D3E8A, #2a52be); }
.case-tile.c-amber { background: linear-gradient(135deg, #D35400, #f47c20); }
.case-tile.c-red { background: linear-gradient(135deg, #C0392B, #ef4444); }
.case-tile.c-green { background: linear-gradient(135deg, #0E7337, #10b981); }
.case-tile.c-black { background: linear-gradient(135deg, #4A4A4A, #333333); }

.dark-mode .case-tile {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.4);
}
</style>
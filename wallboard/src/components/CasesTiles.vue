<template>
  <div class="cases-container" ref="casesContainer">
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
      
      <!-- Add duplicate tiles for smooth scrolling if needed -->
      <div
        v-if="shouldDuplicate"
        v-for="tile in tiles"
        :key="`dup-${tile.id}`"
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
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'

export default {
  name: 'CasesTiles',
  props: {
    tiles: {
      type: Array,
      required: true,
      default: () => []
    }
  },
  setup(props) {
    const casesContainer = ref(null)
    let scrollInterval = null

    // Check if we need to duplicate tiles for smooth scrolling
    const shouldDuplicate = computed(() => {
      return props.tiles.length <= 8 // Always duplicate to ensure scrollable content
    })

    // Auto-scroll functionality for vertical scrolling
    const setupAutoScroll = (container, scrollSpeed = 1.5, pauseDuration = 2500) => {
      if (!container) return null
      
      let direction = 1 // 1 for down, -1 for up
      let isPaused = false
      
      return setInterval(() => {
        if (isPaused || !container) return
        
        const { scrollTop, scrollHeight, clientHeight } = container
        const maxScroll = scrollHeight - clientHeight
        
        // Force scrolling even with minimal content
        if (maxScroll <= 2) return
        
        // Check if we've reached the bottom or top
        if (scrollTop >= maxScroll - 2) {
          direction = -1
          isPaused = true
          setTimeout(() => { isPaused = false }, pauseDuration)
        } else if (scrollTop <= 2) {
          direction = 1
          isPaused = true
          setTimeout(() => { isPaused = false }, pauseDuration)
        }
        
        container.scrollBy(0, direction * scrollSpeed)
      }, 25)
    }

    // Start auto-scroll
    const startAutoScroll = () => {
      nextTick(() => {
        if (casesContainer.value) {
          scrollInterval = setupAutoScroll(casesContainer.value, 1.5, 2500)
        }
      })
    }

    // Stop auto-scroll
    const stopAutoScroll = () => {
      if (scrollInterval) {
        clearInterval(scrollInterval)
        scrollInterval = null
      }
    }

    // Watch for data changes to restart auto-scroll
    watch(() => props.tiles, () => {
      stopAutoScroll()
      setTimeout(startAutoScroll, 1000)
    }, { deep: true })

    // Lifecycle
    onMounted(() => {
      setTimeout(startAutoScroll, 1200)
    })

    onBeforeUnmount(() => {
      stopAutoScroll()
    })

    return {
      casesContainer,
      shouldDuplicate
    }
  }
}
</script>

<style scoped>
.cases-container {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  scroll-behavior: smooth;
  pointer-events: none;
}

/* Ultra-slim scrollbar for TV */
.cases-container::-webkit-scrollbar {
  width: 1px;
}

.cases-container::-webkit-scrollbar-track {
  background: transparent;
}

.cases-container::-webkit-scrollbar-thumb {
  background: rgba(203, 213, 225, 0.2);
  border-radius: 1px;
}

.dark-mode .cases-container::-webkit-scrollbar-thumb {
  background: rgba(107, 114, 128, 0.2);
}

.cases-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
  padding: 0 4px;
}

.case-card {
  background: #ffffff;
  border-radius: 6px;
  padding: 12px 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
  height: 70px;
}

.dark-mode .case-card {
  background: #2d3748;
  color: #e2e8f0;
}

.case-inner {
  display: flex;
  flex-direction: column;
  gap: 3px;
  text-align: center;
  height: 100%;
  justify-content: center;
}

.case-value {
  font-size: 1.5rem;
  font-weight: 700;
  line-height: 1;
}

.case-label {
  font-size: 0.6rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  opacity: 0.8;
  line-height: 1.1;
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

/* Variant background accents - thinner for TV */
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
  .cases-grid {
    gap: 10px;
    padding: 0 6px;
  }
  
  .case-card {
    height: 80px;
    padding: 14px 10px;
  }
  
  .case-value {
    font-size: 1.75rem;
  }
  
  .case-label {
    font-size: 0.65rem;
  }
}

/* 4K TV optimization */
@media screen and (min-width: 3840px) {
  .cases-grid {
    gap: 15px;
    padding: 0 10px;
  }
  
  .case-card {
    height: 120px;
    padding: 20px 15px;
    border-radius: 10px;
  }
  
  .case-inner {
    gap: 6px;
  }
  
  .case-value {
    font-size: 2.5rem;
  }
  
  .case-label {
    font-size: 0.8rem;
    letter-spacing: 0.5px;
  }
  
  .case-card::before {
    height: 4px;
  }
}

/* Smaller TV screens */
@media screen and (max-width: 1600px) {
  .cases-grid {
    gap: 6px;
    padding: 0 2px;
  }
  
  .case-card {
    height: 60px;
    padding: 8px 6px;
  }
  
  .case-value {
    font-size: 1.25rem;
  }
  
  .case-label {
    font-size: 0.55rem;
  }
}

/* Very small screens */
@media screen and (max-width: 1200px) {
  .case-card {
    height: 55px;
    padding: 6px 4px;
  }
  
  .case-value {
    font-size: 1.1rem;
  }
  
  .case-label {
    font-size: 0.5rem;
  }
}

/* Mobile fallback */
@media screen and (max-width: 768px) {
  .cases-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    padding: 0 4px;
  }
  
  .case-card {
    height: 65px;
    padding: 8px 6px;
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
<template>
  <div class="header">
    <div class="title-section">
      <h1>Helpline Wallboard</h1>
      <p>Real-time counselling and support</p>
    </div>
    <div class="header-controls">
      <div class="connection-status">
        <span :class="['dot', connectionStatus]"></span>
        <span class="status-text">{{ connectionLabel }}</span>
        <small v-if="lastUpdate" class="last-update">{{ lastUpdate }}</small>
      </div>
      <button 
        class="theme-toggle" 
        @click="$emit('toggle-theme')" 
        :title="isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
      >
        <span class="theme-icon">{{ isDarkMode ? '☀️' : '🌙' }}</span>
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'WallboardHeader',
  props: {
    connectionStatus: {
      type: String,
      required: true
    },
    connectionLabel: {
      type: String,
      required: true
    },
    lastUpdate: {
      type: String,
      default: null
    },
    isDarkMode: {
      type: Boolean,
      required: true
    }
  },
  emits: ['toggle-theme']
}
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0 6px 0;
  border-bottom: 1px solid #e5e7eb;
  width: 100%;
  height: 50px;
  flex-shrink: 0;
}

.dark-mode .header {
  border-bottom-color: #4b5563;
}

.title-section {
  flex: 1;
  min-width: 0;
}

.title-section h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 2px 0;
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.title-section p {
  color: #6b7280;
  margin: 0;
  font-size: 0.75rem;
  line-height: 1.2;
  font-weight: 400;
}

.dark-mode .title-section h1 {
  color: #f9fafb;
}

.dark-mode .title-section p {
  color: #9ca3af;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.75rem;
  color: #374151;
  padding: 4px 8px;
  background: rgba(249, 250, 251, 0.8);
  border-radius: 8px;
  min-width: 120px;
  height: 28px;
}

.dark-mode .connection-status {
  color: #e5e7eb;
  background: rgba(55, 65, 81, 0.8);
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}

.dot.on {
  background-color: #10b981;
  box-shadow: 0 0 4px rgba(16, 185, 129, 0.4);
  animation: pulse 2s infinite;
}

.dot.connecting {
  background-color: #f59e0b;
  box-shadow: 0 0 4px rgba(245, 158, 11, 0.4);
  animation: blink 1s infinite;
}

.dot.off {
  background-color: #ef4444;
  box-shadow: 0 0 4px rgba(239, 68, 68, 0.4);
}

.status-text {
  font-weight: 600;
  white-space: nowrap;
}

.last-update {
  color: #9ca3af;
  font-size: 0.65rem;
  white-space: nowrap;
  margin-left: auto;
}

.dark-mode .last-update {
  color: #6b7280;
}

.theme-toggle {
  padding: 6px;
  border: none;
  background: #f3f4f6;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid #e5e7eb;
}

.theme-toggle:hover {
  background: #e5e7eb;
  transform: scale(1.05);
}

.dark-mode .theme-toggle {
  background: #374151;
  border-color: #4b5563;
}

.dark-mode .theme-toggle:hover {
  background: #4b5563;
}

.theme-icon {
  font-size: 0.9rem;
  display: block;
  line-height: 1;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.1);
  }
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0.4;
  }
}

/* TV Screen optimizations */
@media screen and (min-width: 1920px) {
  .header {
    height: 55px;
    padding: 10px 0 8px 0;
  }
  
  .title-section h1 {
    font-size: 1.75rem;
  }
  
  .title-section p {
    font-size: 0.85rem;
  }
  
  .connection-status {
    font-size: 0.8rem;
    padding: 6px 10px;
    min-width: 140px;
    height: 32px;
  }
  
  .theme-toggle {
    width: 36px;
    height: 36px;
  }
}

/* 4K TV optimization */
@media screen and (min-width: 3840px) {
  .header {
    height: 80px;
    padding: 15px 0 12px 0;
  }
  
  .title-section h1 {
    font-size: 2.5rem;
  }
  
  .title-section p {
    font-size: 1.1rem;
  }
  
  .header-controls {
    gap: 20px;
  }
  
  .connection-status {
    font-size: 1rem;
    padding: 8px 15px;
    min-width: 180px;
    height: 40px;
    gap: 8px;
  }
  
  .dot {
    width: 8px;
    height: 8px;
  }
  
  .theme-toggle {
    width: 48px;
    height: 48px;
    padding: 10px;
  }
  
  .theme-icon {
    font-size: 1.2rem;
  }
}

/* Smaller screens */
@media screen and (max-width: 1200px) {
  .header {
    height: 45px;
    padding: 6px 0 4px 0;
  }
  
  .title-section h1 {
    font-size: 1.25rem;
  }
  
  .title-section p {
    font-size: 0.7rem;
  }
  
  .connection-status {
    font-size: 0.7rem;
    min-width: 100px;
    height: 24px;
    padding: 3px 6px;
  }
  
  .theme-toggle {
    width: 28px;
    height: 28px;
  }
  
  .theme-icon {
    font-size: 0.8rem;
  }
  
  .last-update {
    display: none;
  }
}
</style>
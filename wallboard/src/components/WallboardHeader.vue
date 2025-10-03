<template>
  <div class="header">
    <div class="title-section">
      <h1>Sauti Helpline Wallboard</h1>
      <p>Real-time counselling and support</p>
    </div>
    <div class="header-controls">
      <div class="connection-status">
        <span :class="['dot', connectionStatus]"></span>
        <span class="status-text">{{ connectionLabel }}</span>
        <small v-if="lastUpdate"> · last update: {{ lastUpdate }}</small>
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
  padding: 20px 0;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 20px;
}

.dark-mode .header {
  border-bottom-color: #4b5563;
}

.title-section h1 {
  font-size: 2rem;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
}

.title-section p {
  color: #6b7280;
  margin: 4px 0 0 0;
  font-size: 0.9rem;
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
  gap: 20px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: #6b7280;
}

.dark-mode .connection-status {
  color: #9ca3af;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.dot.on {
  background-color: #10b981;
  animation: pulse 2s infinite;
}

.dot.connecting {
  background-color: #f59e0b;
  animation: blink 1s infinite;
}

.dot.off {
  background-color: #ef4444;
}

.theme-toggle {
  padding: 8px;
  border: none;
  background: #f3f4f6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.theme-toggle:hover {
  background: #e5e7eb;
  transform: scale(1.05);
}

.dark-mode .theme-toggle {
  background: #374151;
}

.dark-mode .theme-toggle:hover {
  background: #4b5563;
}

.theme-icon {
  font-size: 1.2rem;
  display: block;
}

.status-text {
  font-weight: 600;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

@keyframes blink {
  0%, 50% {
    opacity: 1;
  }
  51%, 100% {
    opacity: 0.3;
  }
}

/* Responsive design */
@media (max-width: 768px) {
  .header {
    flex-direction: column;
    gap: 15px;
    align-items: flex-start;
  }
  
  .title-section h1 {
    font-size: 1.5rem;
  }
  
  .header-controls {
    width: 100%;
    justify-content: space-between;
  }
}
</style>
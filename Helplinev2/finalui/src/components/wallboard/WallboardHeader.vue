<template>
  <div 
    class="rounded-lg shadow-xl border px-6 py-4"
    :class="isDarkMode 
      ? 'bg-black border-transparent' 
      : 'bg-white border-transparent'"
  >
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <!-- Title Section -->
      <!-- Connection Status Move to Left on Mobile, Right on Desktop -->
      <div 
        class="flex items-center gap-3"
      >
        <div 
          class="flex items-center gap-2 px-4 py-2 rounded-xl border transition-all duration-300 shadow-sm"
          :class="isDarkMode 
            ? 'bg-black/40 border-gray-800' 
            : 'bg-gray-50 border-gray-200'"
        >
        <span :class="['w-2 h-2 rounded-full flex-shrink-0', dotClass]"></span>
        <div class="flex flex-col">
          <span 
            class="text-xs font-semibold"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            {{ connectionLabel }}
          </span>
          <span 
            v-if="lastUpdate" 
            class="text-[0.65rem]"
            :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
          >
            {{ lastUpdate }}
          </span>
      </div>
    </div>
  </div>
</div>
</div>
</template>

<script>
import { inject } from 'vue'

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
    }
  },
  setup() {
    const isDarkMode = inject('isDarkMode')
    
    return {
      isDarkMode
    }
  },
  computed: {
    dotClass() {
      if (this.connectionStatus === 'on') return 'bg-emerald-500 animate-pulse-dot'
      if (this.connectionStatus === 'connecting') return 'bg-amber-500 animate-blink-dot'
      if (this.connectionStatus === 'off') return 'bg-red-500'
      return 'bg-gray-500'
    }
  }
}
</script>

<style scoped>
@keyframes pulse-dot {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.7;
    transform: scale(1.2);
  }
}

@keyframes blink-dot {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0.4; }
}

.animate-pulse-dot {
  animation: pulse-dot 2s infinite;
  box-shadow: 0 0 6px rgba(16, 185, 129, 0.5);
}

.animate-blink-dot {
  animation: blink-dot 1s infinite;
  box-shadow: 0 0 6px rgba(245, 158, 11, 0.5);
}

.bg-red-500 {
  box-shadow: 0 0 6px rgba(239, 68, 68, 0.5);
}
</style>
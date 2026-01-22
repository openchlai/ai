<template>
  <div 
    class="rounded-lg shadow-xl p-6 sticky top-4 border"
    :class="isDarkMode 
      ? 'bg-gray-800 border-transparent' 
      : 'bg-white border-transparent'"
  >
    <!-- Header -->
    <div 
      class="flex items-center justify-between mb-6 pb-4 border-b"
      :class="isDarkMode ? 'border-transparent' : 'border-transparent'"
    >
      <h2 
        class="text-xl font-bold flex items-center gap-2"
        :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
      >
        <i-mdi-phone 
          class="w-5 h-5"
          :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
        />
        Call Details
      </h2>
    </div>

    <!-- Date/Time & Reporter -->
    <div class="mb-6">
      <div class="flex items-center justify-between mb-3">
        <span 
          class="text-sm font-medium"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          {{ formatDateTime(callData.callDateTime) }}
        </span>
        <span 
          class="px-3 py-1 text-xs font-bold rounded-full border"
          :class="isDarkMode 
            ? 'bg-amber-600/20 text-amber-500 border-amber-600/30' 
            : 'bg-amber-100 text-amber-700 border-amber-300'"
        >
          {{ callData.reporter || 'N/A' }}
        </span>
      </div>
    </div>

    <!-- Call Information -->
    <div class="space-y-3 mb-6">
      <div 
        class="flex items-center justify-between py-2 px-3 rounded-lg"
        :class="isDarkMode ? 'bg-gray-900/60' : 'bg-gray-50'"
      >
        <span 
          class="text-sm font-semibold"
          :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
        >
          Direction:
        </span>
        <span 
          class="text-sm font-bold"
          :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
        >
          {{ callData.direction || 'N/A' }}
        </span>
      </div>

      <div 
        class="flex items-center justify-between py-2 px-3 rounded-lg"
        :class="isDarkMode ? 'bg-gray-900/60' : 'bg-gray-50'"
      >
        <span 
          class="text-sm font-semibold"
          :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
        >
          Phone:
        </span>
        <span 
          class="text-sm font-bold"
          :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
        >
          {{ callData.phone || 'N/A' }}
        </span>
      </div>

      <div 
        class="flex items-center justify-between py-2 px-3 rounded-lg"
        :class="isDarkMode ? 'bg-gray-900/60' : 'bg-gray-50'"
      >
        <span 
          class="text-sm font-semibold"
          :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
        >
          Extension:
        </span>
        <span 
          class="text-sm font-bold"
          :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
        >
          {{ callData.extension || 'N/A' }}
        </span>
      </div>

      <div 
        class="flex items-center justify-between py-2 px-3 rounded-lg"
        :class="isDarkMode ? 'bg-gray-900/60' : 'bg-gray-50'"
      >
        <span 
          class="text-sm font-semibold"
          :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
        >
          Wait Time:
        </span>
        <span 
          class="text-sm font-bold"
          :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
        >
          {{ callData.waitTime || 'N/A' }}
        </span>
      </div>

      <div 
        class="flex items-center justify-between py-2 px-3 rounded-lg"
        :class="isDarkMode ? 'bg-gray-900/60' : 'bg-gray-50'"
      >
        <span 
          class="text-sm font-semibold"
          :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
        >
          Hangup Status:
        </span>
        <span 
          class="text-sm font-bold"
          :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
        >
          {{ callData.hangupStatus || 'N/A' }}
        </span>
      </div>

      <div 
        class="flex items-center justify-between py-2 px-3 rounded-lg"
        :class="isDarkMode ? 'bg-gray-900/60' : 'bg-gray-50'"
      >
        <span 
          class="text-sm font-semibold"
          :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
        >
          Talk Time:
        </span>
        <div class="flex items-center gap-2">
          <button 
            @click="togglePlayback"
            class="w-7 h-7 flex items-center justify-center rounded-full transition-all shadow-lg"
            :class="isDarkMode 
              ? 'bg-amber-600 hover:bg-amber-700' 
              : 'bg-amber-700 hover:bg-amber-800'"
          >
            <i-mdi-play v-if="!isPlaying" class="w-4 h-4 text-white" />
            <i-mdi-pause v-else class="w-4 h-4 text-white" />
          </button>
          <span 
            class="text-sm font-bold"
            :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
          >
            {{ callData.talkTime || 'N/A' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'

const isDarkMode = inject('isDarkMode')

const props = defineProps({
  callData: {
    type: Object,
    default: () => ({
      callDateTime: '',
      reporter: '',
      direction: '',
      phone: '',
      extension: '',
      waitTime: '',
      hangupStatus: '',
      talkTime: ''
    })
  }
})

const isPlaying = ref(false)

const formatDateTime = (timestamp) => {
  if (!timestamp || timestamp === '0') return 'N/A'
  
  // Handle Unix timestamp (convert to milliseconds)
  const date = new Date(parseInt(timestamp) * 1000)
  
  return date.toLocaleString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  })
}

const togglePlayback = () => {
  isPlaying.value = !isPlaying.value
  // Add actual playback logic here
}
</script>
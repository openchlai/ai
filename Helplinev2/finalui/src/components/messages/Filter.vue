<template>
  <div class="flex flex-wrap gap-3 mb-6">
    <button
      v-for="platform in channelFilters"
      :key="platform.id"
      :class="getFilterButtonClass(activePlatform === platform.id)"
      @click="$emit('update:activePlatform', platform.id)"
    >
      <!-- All -->
      <i-mdi-apps v-if="platform.id === 'all'" class="w-5 h-5" />
      
      <!-- WhatsApp -->
      <i-mdi-whatsapp v-else-if="platform.id === 'whatsapp'" class="w-5 h-5" />
      
      <!-- SafePal -->
      <i-mdi-shield-check v-else-if="platform.id === 'safepal'" class="w-5 h-5" />
      
      <!-- Email -->
      <i-mdi-email-outline v-else-if="platform.id === 'email'" class="w-5 h-5" />
      
      <!-- Walk-In -->
      <i-mdi-walk v-else-if="platform.id === 'walkin'" class="w-5 h-5" />
      
      <!-- AI -->
      <i-mdi-robot-outline v-else-if="platform.id === 'ai'" class="w-5 h-5" />
      
      <!-- Call -->
      <i-mdi-phone-outline v-else-if="platform.id === 'call'" class="w-5 h-5" />
      
      <!-- Default fallback -->
      <i-mdi-message-text-outline v-else class="w-5 h-5" />
      
      {{ platform.name }}
    </button>
  </div>
</template>

<script setup>
import { inject } from 'vue'

defineProps({
  channelFilters: {
    type: Array,
    required: true
  },
  activePlatform: {
    type: String,
    required: true
  }
})

defineEmits(['update:activePlatform'])

// Inject theme
const isDarkMode = inject('isDarkMode')

// Dynamic button class for filter pills
const getFilterButtonClass = (isActive) => {
  const baseClasses = 'px-5 py-2.5 rounded-lg font-medium transition-all duration-200 text-sm flex items-center gap-2'
  
  if (isActive) {
    return isDarkMode.value
      ? `${baseClasses} bg-amber-600 text-white shadow-lg shadow-amber-900/50`
      : `${baseClasses} bg-amber-700 text-white shadow-lg shadow-amber-900/30`
  } else {
    return isDarkMode.value
      ? `${baseClasses} bg-neutral-900 text-gray-300 border border-transparent hover:border-amber-600 hover:text-amber-500`
      : `${baseClasses} bg-white text-gray-700 border border-transparent hover:border-amber-600 hover:text-amber-700`
  }
}
</script>
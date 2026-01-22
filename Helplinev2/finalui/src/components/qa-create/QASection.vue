<template>
  <div 
    :class="[
      'mb-6 p-6 rounded-lg border',
      containerClass,
      isDarkMode 
        ? 'bg-gray-900/40 border-transparent' 
        : 'bg-gray-50 border-transparent'
    ]"
  >
    <div class="flex items-center justify-between mb-4">
      <h2 
        class="text-xl font-bold"
        :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
      >
        {{ title }}
      </h2>
      <span 
        v-if="badge" 
        class="px-3 py-1 text-xs font-bold rounded-full border"
        :class="isDarkMode 
          ? 'bg-amber-600/20 text-amber-500 border-amber-600/30' 
          : 'bg-amber-100 text-amber-700 border-amber-300'"
      >
        {{ badge }}
      </span>
    </div>
    
    <p 
      v-if="description" 
      class="text-sm mb-4"
      :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
    >
      {{ description }}
    </p>

    <slot />
  </div>
</template>

<script setup>
import { inject } from 'vue'

const isDarkMode = inject('isDarkMode')

defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  badge: {
    type: String,
    default: ''
  },
  containerClass: {
    type: String,
    default: ''
  }
})
</script>
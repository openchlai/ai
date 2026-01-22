<template>
  <div 
    class="border rounded-lg overflow-hidden transition-all"
    :class="isDarkMode 
      ? 'border-transparent' 
      : 'border-transparent'"
  >
    <!-- Header (always visible) -->
    <button
      @click="$emit('toggle')"
      class="w-full flex items-center justify-between p-4 text-left transition-colors"
      :class="[
        isDarkMode 
          ? isOpen 
            ? 'bg-gray-800 hover:bg-gray-750' 
            : 'bg-gray-800/50 hover:bg-gray-800'
          : isOpen
            ? 'bg-gray-50 hover:bg-gray-100'
            : 'bg-white hover:bg-gray-50'
      ]"
    >
      <div class="flex items-center gap-3">
        <!-- Chevron Icon -->
        <svg 
          width="20" 
          height="20" 
          viewBox="0 0 24 24" 
          fill="none" 
          stroke="currentColor" 
          stroke-width="2"
          class="transition-transform duration-200"
          :class="[
            isOpen ? 'rotate-90' : '',
            isDarkMode ? 'text-gray-400' : 'text-gray-600'
          ]"
        >
          <polyline points="9 18 15 12 9 6"/>
        </svg>

        <!-- Title -->
        <span 
          class="font-semibold text-base"
          :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
        >
          {{ title }}
        </span>

        <!-- Badge (optional) -->
        <span 
          v-if="badge !== null && badge !== undefined"
          class="px-2 py-0.5 rounded-full text-xs font-medium"
          :class="isDarkMode 
            ? badge > 0 
              ? 'bg-amber-600 text-white' 
              : 'bg-gray-700 text-gray-400'
            : badge > 0
              ? 'bg-amber-100 text-amber-700'
              : 'bg-gray-200 text-gray-600'"
        >
          {{ badge }}
        </span>
      </div>

      <!-- Optional actions slot -->
      <slot name="actions"></slot>
    </button>

    <!-- Content (collapsible) -->
    <div
      v-show="isOpen"
      class="transition-all duration-200"
      :class="isDarkMode ? 'bg-gray-900' : 'bg-white'"
    >
      <div class="p-4 border-t" :class="isDarkMode ? 'border-transparent' : 'border-transparent'">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { inject } from 'vue'

defineProps({
  title: { type: String, required: true },
  isOpen: { type: Boolean, default: false },
  badge: { type: Number, default: null }
})

defineEmits(['toggle'])

const isDarkMode = inject('isDarkMode')
</script>
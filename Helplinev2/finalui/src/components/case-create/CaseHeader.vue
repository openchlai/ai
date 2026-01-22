<template>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-6">
      <div class="flex-1">
        <h1 
          class="text-xl sm:text-2xl font-black tracking-tight mb-1"
          :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
        >
          Create New Case
          <span 
            class="block w-12 h-0.5 rounded-full mt-1.5"
            :class="isDarkMode ? 'bg-amber-600' : 'bg-amber-700'"
          ></span>
        </h1>
        <p 
          class="text-sm mt-1.5"
          :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
        >
          {{ currentDescription }}
        </p>
      </div>

      <!-- AI Toggle in Header -->
      <div 
        class="flex items-center gap-4 px-4 py-3 rounded-2xl border transition-all duration-300"
        :class="isDarkMode ? 'bg-neutral-900/50 border-neutral-800' : 'bg-white border-gray-100 shadow-sm'"
      >
        <div class="text-right">
          <h3 
            class="text-xs font-bold leading-none mb-1"
            :class="aiEnabled ? (isDarkMode ? 'text-amber-500' : 'text-amber-600') : (isDarkMode ? 'text-gray-400' : 'text-gray-500')"
          >
            AI Intelligence
          </h3>
          <p class="text-[10px] font-medium text-gray-500 leading-none">
            {{ aiEnabled ? 'Features Active' : 'Enable Analysis' }}
          </p>
        </div>
        
        <button
          @click="$emit('update:aiEnabled', !aiEnabled)"
          class="relative inline-flex h-6 w-11 items-center rounded-full transition-colors duration-300 focus:outline-none"
          :class="aiEnabled 
            ? (isDarkMode ? 'bg-amber-500' : 'bg-amber-600') 
            : (isDarkMode ? 'bg-neutral-700' : 'bg-gray-200')"
        >
          <span
            class="inline-block h-4 w-4 transform rounded-full bg-white transition-transform duration-300 shadow-sm"
            :class="aiEnabled ? 'translate-x-6' : 'translate-x-1'"
          />
        </button>
      </div>
    </div>
</template>

<script setup>
import { computed, inject } from "vue"

// Inject theme
const isDarkMode = inject('isDarkMode')

const props = defineProps({
  currentStep: {
    type: Number,
    default: 1
  },
  stepDescriptions: {
    type: Array,
    default: () => []
  },
  aiEnabled: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update:aiEnabled'])

const currentDescription = computed(() => {
  if (!props.stepDescriptions.length) return ""
  return props.stepDescriptions[props.currentStep - 1] || ""
})
</script>
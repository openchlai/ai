<template>
  <div class="flex items-center justify-between gap-3 mb-6">
    <div>
      <h1 class="text-2xl font-black tracking-tight text-gray-900 mb-1.5">
        Create New Case
        <span class="block w-12 h-0.5 bg-blue-600 rounded-full mt-1.5"></span>
      </h1>
      <p class="text-sm text-gray-600 mt-1.5">
        {{ currentDescription }}
      </p>
    </div>

    <div class="flex items-center gap-3">
      <span class="flex items-center gap-2 text-sm font-medium text-gray-700">
        <span class="text-blue-600">
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M12 2L2 7L12 12L22 7L12 2Z"
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
            />
            <path
              d="M2 17L12 22L22 17"
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
            />
            <path
              d="M2 12L12 17L22 12"
              stroke="currentColor"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
            />
          </svg>
        </span>
        AI Enabled
      </span>

      <label class="relative inline-block w-11 h-6 cursor-pointer">
        <input
          type="checkbox"
          :checked="isAIEnabled"
          @change="toggleAI"
          class="sr-only peer"
        />
        <span class="absolute inset-0 bg-gray-300 rounded-full transition-colors peer-checked:bg-blue-600"></span>
        <span class="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5"></span>
      </label>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue"

const props = defineProps({
  currentStep: {
    type: Number,
    default: 1
  },
  stepDescriptions: {
    type: Array,
    default: () => []
  },
  isAIEnabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(["toggle-ai"])

const currentDescription = computed(() => {
  if (!props.stepDescriptions.length) return ""
  return props.stepDescriptions[props.currentStep - 1] || ""
})

const toggleAI = (event) => {
  emit("toggle-ai", event.target.checked)
}
</script>
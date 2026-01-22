<template>
  <div class="py-2 pb-4">
    <div class="relative flex justify-between items-start gap-6 pt-7">
      <!-- Connecting Line -->
      <div 
        class="absolute top-10 left-0 right-0 h-0.5 -z-10"
        :class="isDarkMode ? 'bg-gray-700' : 'bg-gray-300'"
        style="top: 2.75rem;"
      >
        <div 
          class="h-full transition-all duration-300"
          :class="isDarkMode ? 'bg-green-500' : 'bg-green-600'"
          :style="{ width: `${((currentStep - 1) / (totalSteps - 1)) * 100}%` }"
        ></div>
      </div>

      <!-- Steps -->
      <div
        v-for="step in totalSteps"
        :key="step"
        class="flex flex-col items-center gap-1.5 flex-1"
        :class="{
          'opacity-50': stepStatus[step] === 'pending' && currentStep !== step,
          'cursor-pointer': stepStatus[step] === 'completed' || currentStep === step,
          'cursor-not-allowed': stepStatus[step] === 'pending' && currentStep !== step
        }"
        @click="canNavigate(step) && navigateToStep(step)"
      >
        <!-- Step Circle -->
        <div
          class="relative flex items-center justify-center w-7 h-7 sm:w-9 sm:h-9 text-[10px] sm:text-sm font-extrabold leading-none transition-all rounded-full border-2"
          :class="getStepCircleClass(step)"
        >
          <span v-if="stepStatus[step] === 'completed'">✓</span>
          <span v-else>{{ step }}</span>
        </div>

        <!-- Step Label -->
        <div
          class="text-[9px] sm:text-xs font-bold text-center transition-colors max-w-[60px] sm:max-w-[100px]"
          :class="getStepLabelClass(step)"
        >
          {{ stepLabels[step - 1] }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { inject, computed } from 'vue'

// Inject theme
const isDarkMode = inject('isDarkMode')

const props = defineProps({
  currentStep: {
    type: Number,
    required: true,
  },
  totalSteps: {
    type: Number,
    required: true,
  },
  stepLabels: {
    type: Array,
    required: true,
  },
  stepStatus: {
    type: Object,
    required: true,
  },
})

const emit = defineEmits(["step-change"])

const canNavigate = (step) => {
  // Allow navigation to completed steps or current step
  return props.stepStatus[step] === 'completed' || step === props.currentStep
}

const navigateToStep = (step) => {
  emit("step-change", step)
}

const getStepCircleClass = (step) => {
  const status = props.stepStatus[step]
  const isCurrent = props.currentStep === step
  
  if (isDarkMode.value) {
    // Dark mode classes
    if (status === 'pending' && !isCurrent) {
      return 'bg-gray-900 border-transparent text-gray-500'
    } else if (isCurrent && status !== 'completed') {
      return 'bg-gray-900 border-amber-600 text-amber-500'
    } else if (status === 'completed') {
      return 'border-green-500 bg-green-500 text-white'
    } else if (status === 'error') {
      return 'border-red-600 text-red-400 bg-gray-900'
    }
  } else {
    // Light mode classes
    if (status === 'pending' && !isCurrent) {
      return 'bg-white border-transparent text-gray-400'
    } else if (isCurrent && status !== 'completed') {
      return 'bg-white border-amber-600 text-amber-700'
    } else if (status === 'completed') {
      return 'border-green-600 bg-green-600 text-white'
    } else if (status === 'error') {
      return 'border-red-600 text-red-600 bg-white'
    }
  }
  
  return ''
}

const getStepLabelClass = (step) => {
  const status = props.stepStatus[step]
  const isCurrent = props.currentStep === step
  
  if (isDarkMode.value) {
    // Dark mode classes
    if (status === 'pending' && !isCurrent) {
      return 'text-gray-500'
    } else if (isCurrent && status !== 'completed') {
      return 'text-amber-500'
    } else if (status === 'completed') {
      return 'text-green-400'
    } else if (status === 'error') {
      return 'text-red-400'
    }
  } else {
    // Light mode classes
    if (status === 'pending' && !isCurrent) {
      return 'text-gray-500'
    } else if (isCurrent && status !== 'completed') {
      return 'text-amber-700'
    } else if (status === 'completed') {
      return 'text-green-600'
    } else if (status === 'error') {
      return 'text-red-600'
    }
  }
  
  return ''
}
</script>
<template>
  <div class="py-2 pb-4">
    <div class="relative flex justify-between items-start gap-6 pt-7">
      <div
        v-for="step in totalSteps"
        :key="step"
        class="flex flex-col items-center gap-1.5 cursor-pointer flex-1"
        :class="{
          'opacity-50': stepStatus[step] === 'pending' && currentStep !== step
        }"
        @click="navigateToStep(step)"
      >
        <div
          class="flex items-center justify-center text-sm font-extrabold leading-none transition-all"
          :class="{
            'text-gray-400': stepStatus[step] === 'pending' && currentStep !== step,
            'text-gray-900': currentStep === step && stepStatus[step] !== 'completed',
            'text-white bg-green-500 w-6 h-6 rounded-full': stepStatus[step] === 'completed',
            'text-red-600': stepStatus[step] === 'error'
          }"
        >
          {{ stepStatus[step] === "completed" ? "✓" : step }}
        </div>
        <div
          class="text-xs font-bold text-center transition-colors"
          :class="{
            'text-gray-400': stepStatus[step] === 'pending' && currentStep !== step,
            'text-gray-900': currentStep === step && stepStatus[step] !== 'completed',
            'text-green-600': stepStatus[step] === 'completed',
            'text-red-600': stepStatus[step] === 'error'
          }"
        >
          {{ stepLabels[step - 1] }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
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

const navigateToStep = (step) => {
  emit("step-change", step)
}
</script>
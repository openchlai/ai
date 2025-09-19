<template>
  <div class="progress-container">
    <div class="progress-steps">
      <div
        v-for="step in totalSteps"
        :key="step"
        class="progress-step clickable-step"
        :class="{
          active: currentStep === step,
          completed: stepStatus(step) === 'completed',
          error: stepStatus(step) === 'error'
        }"
        @click="$emit('navigate', step)"
      >
        <div
          class="step-circle"
          :class="{
            active: currentStep === step,
            completed: stepStatus(step) === 'completed',
            error: stepStatus(step) === 'error'
          }"
        >
          {{ stepStatus(step) === 'completed' ? '✓' : step }}
        </div>
        <div class="step-label" :class="{ active: currentStep === step }">
          {{ stepLabels[step - 1] }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  totalSteps: { type: Number, required: true },
  currentStep: { type: Number, required: true },
  stepLabels: { type: Array, required: true },
  stepStatus: { type: Function, required: true }
})
</script>

<style scoped>
.progress-steps{ display:flex; gap:10px; flex-wrap:wrap; }
.progress-step{ display:flex; align-items:center; gap:8px; cursor:pointer; }
.step-circle{ width:28px; height:28px; border-radius:50%; display:flex; align-items:center; justify-content:center; border:1px solid var(--color-border); }
.progress-step.active .step-circle{ border-color: var(--color-primary); color: var(--color-primary); }
.step-label{ font-size:12px; color: var(--color-muted); }
.step-label.active{ color: var(--text-color); font-weight:700; }
</style>



<template>
  <div class="progress-container">
    <div class="progress-steps">
      <div
        v-for="step in totalSteps"
        :key="step"
        class="progress-step clickable-step"
        :class="{
          active: currentStep === step,
          completed: stepStatus[step] === 'completed',
          error: stepStatus[step] === 'error',
        }"
        @click="navigateToStep(step)"
      >
        <div
          class="step-circle"
          :class="{
            active: currentStep === step,
            completed: stepStatus[step] === 'completed',
            error: stepStatus[step] === 'error',
          }"
        >
          {{ stepStatus[step] === "completed" ? "✓" : step }}
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
  // now it's an object, not a function
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

<style scoped>
/* Stepper */
.progress-container {
  padding: 6px 0 12px;
}
.progress-steps {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  padding-top: 28px;
}
.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  flex: 1;
}
.progress-step .step-circle {
  font-weight: 800;
  font-size: 14px;
  color: var(--color-muted);
  line-height: 1;
}
.progress-step .step-label {
  font-weight: 700;
  color: var(--color-muted);
  font-size: 12px;
  text-align: center;
}
.progress-step.active .step-circle {
  color: var(--text-color);
}
.progress-step.active .step-label {
  color: var(--text-color);
}
.progress-step.completed .step-circle {
  color: #fff;
  background: var(--success-color);
  width: 24px;
  height: 24px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.progress-step.completed .step-label {
  color: var(--success-color);
}
.progress-step.error .step-circle {
  color: var(--color-primary);
  background: transparent;
}
.progress-step.error .step-label {
  color: var(--color-primary);
}
.progress-steps::before {
  content: none;
}
.progress-steps::after {
  content: none;
}
</style>

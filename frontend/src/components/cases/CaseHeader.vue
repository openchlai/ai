<template>
  <div class="case-header">
    <div>
      <h1>Create New Case</h1>
      <p>{{ currentDescription }}</p>
    </div>

    <div class="toggle-container">
      <span class="toggle-label">
        <span class="ai-icon">
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

      <label class="toggle-switch">
        <input
          type="checkbox"
          :checked="isAIEnabled"
          @change="toggleAI"
        />
        <span class="toggle-slider"></span>
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

const emit = defineEmits(["ai-toggle"])

const currentDescription = computed(() => {
  if (!props.stepDescriptions.length) return ""
  return props.stepDescriptions[props.currentStep - 1] || ""
})

const toggleAI = (event) => {
  emit("ai-toggle", event.target.checked)
}
</script>

<style scoped>
.case-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.case-header h1 {
  margin: 0;
  font-size: 26px;
  font-weight: 900;
  letter-spacing: -0.2px;
  color: var(--text-color);
}
.case-header h1::after {
  content: "";
  display: block;
  width: 48px;
  height: 3px;
  border-radius: 2px;
  background: var(--color-primary);
  margin-top: 6px;
}
.case-header p {
  margin: 6px 0 0;
  color: var(--color-muted);
  font-size: 13px;
}
</style>

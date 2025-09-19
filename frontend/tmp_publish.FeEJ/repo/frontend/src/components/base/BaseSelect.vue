<template>
  <div class="form-group">
    <label v-if="label" class="form-label" :for="id">{{ label }}</label>
    <select
      :id="id"
      class="input"
      :class="{ 'is-error': !!error }"
      v-model="model"
      :disabled="disabled"
      :aria-invalid="!!error"
    >
      <option v-if="placeholder" disabled value="">{{ placeholder }}</option>
      <slot />
    </select>
    <div v-if="hint && !error" class="form-hint">{{ hint }}</div>
    <div v-if="error" class="form-error">{{ error }}</div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  modelValue: [String, Number],
  label: String,
  hint: String,
  error: String,
  id: String,
  placeholder: String,
  disabled: Boolean
})
const emit = defineEmits(['update:modelValue'])
const model = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})
</script>



<template>
  <div class="form-group">
    <label v-if="label" class="form-label" :for="id">{{ label }}</label>
    <input
      :id="id"
      class="input"
      :class="{ 'is-error': !!error }"
      :type="type"
      :placeholder="placeholder"
      v-model="model"
      :disabled="disabled"
      :readonly="readonly"
      :aria-invalid="!!error"
    />
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
  type: { type: String, default: 'text' },
  placeholder: String,
  disabled: Boolean,
  readonly: Boolean
})
const emit = defineEmits(['update:modelValue'])
const model = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})
</script>



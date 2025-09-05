<template>
  <div class="form-group">
    <label v-if="label" class="form-label" :for="id">{{ label }}</label>
    <textarea
      :id="id"
      class="input"
      :class="{ 'is-error': !!error }"
      :rows="rows"
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
  modelValue: String,
  label: String,
  hint: String,
  error: String,
  id: String,
  placeholder: String,
  rows: { type: Number, default: 4 },
  disabled: Boolean,
  readonly: Boolean
})
const emit = defineEmits(['update:modelValue'])
const model = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v)
})
</script>



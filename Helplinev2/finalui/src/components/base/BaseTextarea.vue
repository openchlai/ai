<template>
  <div class="flex flex-col gap-2">
    <label 
      v-if="label" 
      class="block text-sm font-semibold" 
      :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
      :for="id"
    >
      {{ label }}
    </label>
    <textarea
      :id="id"
      :class="[
        'px-4 py-3 border rounded-lg text-sm placeholder-gray-500 transition-all resize-y',
        'focus:outline-none focus:ring-2',
        error 
          ? 'border-red-600 focus:border-red-600 focus:ring-red-600/50' 
          : (isDarkMode
            ? 'border-transparent focus:border-amber-500 focus:ring-amber-500/50 hover:border-amber-500'
            : 'border-transparent focus:border-amber-600 focus:ring-amber-600/50 hover:border-amber-600'),
        disabled 
          ? (isDarkMode 
            ? 'bg-gray-800 text-gray-500 cursor-not-allowed' 
            : 'bg-gray-200 text-gray-500 cursor-not-allowed')
          : (isDarkMode 
            ? 'bg-gray-700 text-gray-100' 
            : 'bg-gray-50 text-gray-900'),
        readonly 
          ? (isDarkMode 
            ? 'bg-gray-800/50 cursor-default' 
            : 'bg-gray-100 cursor-default')
          : ''
      ]"
      :rows="rows"
      :placeholder="placeholder"
      v-model="model"
      :disabled="disabled"
      :readonly="readonly"
      :aria-invalid="!!error"
    />
    <div 
      v-if="hint && !error" 
      class="text-xs"
      :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
    >
      {{ hint }}
    </div>
    <div v-if="error" class="text-xs text-red-400">{{ error }}</div>
  </div>
</template>

<script setup>
import { computed, inject } from 'vue'

const isDarkMode = inject('isDarkMode')

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
<template>
  <div :class="containerClass">
    <label 
      class="block text-sm font-semibold mb-2"
      :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
    >
      {{ label }}
      <span v-if="required" class="text-red-400 font-bold">*</span>
    </label>
    <textarea
      v-model="model"
      :rows="rows"
      :placeholder="placeholder"
      :disabled="disabled"
      :maxlength="maxlength"
      :required="required"
      class="px-4 py-3 border rounded-lg text-sm w-full focus:outline-none focus:ring-2 transition-all resize-y disabled:cursor-not-allowed"
      :class="isDarkMode 
        ? 'bg-gray-700 border-transparent text-gray-100 placeholder-gray-500 focus:border-amber-500 focus:ring-amber-500/50 disabled:bg-gray-800' 
        : 'bg-gray-50 border-transparent text-gray-900 placeholder-gray-400 focus:border-amber-600 focus:ring-amber-600/50 disabled:bg-gray-200'"
    ></textarea>
    <div v-if="hint || (maxlength && showCharCount)" class="flex justify-between items-center mt-2">
      <p 
        v-if="hint" 
        class="text-xs"
        :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
      >
        {{ hint }}
      </p>
      <p 
        v-if="maxlength && showCharCount" 
        class="text-xs font-semibold"
        :class="model?.length > maxlength * 0.9 
          ? 'text-red-400' 
          : (isDarkMode ? 'text-gray-400' : 'text-gray-600')"
      >
        {{ model?.length || 0 }} / {{ maxlength }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { computed, inject } from 'vue'

const isDarkMode = inject('isDarkMode')

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    required: true
  },
  placeholder: {
    type: String,
    default: 'Enter comments...'
  },
  rows: {
    type: Number,
    default: 3
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  hint: {
    type: String,
    default: ''
  },
  maxlength: {
    type: Number,
    default: null
  },
  showCharCount: {
    type: Boolean,
    default: false
  },
  containerClass: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const model = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})
</script>
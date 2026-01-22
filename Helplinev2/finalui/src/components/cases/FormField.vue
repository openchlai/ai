<template>
  <div>
    <label
      class="block text-sm font-semibold mb-2"
      :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
    >
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>

    <!-- Text Input -->
    <input
      v-if="type === 'text'"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :placeholder="placeholder"
      class="w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-offset-0 transition-all"
      :class="[
        isDarkMode
          ? 'bg-gray-800 border-transparent text-gray-300 placeholder-gray-500 focus:ring-amber-500'
          : 'bg-white border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-500',
        error ? 'border-red-500' : ''
      ]"
    />

    <!-- Textarea -->
    <textarea
      v-else-if="type === 'textarea'"
      :value="modelValue"
      @input="$emit('update:modelValue', $event.target.value)"
      :rows="rows"
      :placeholder="placeholder"
      class="w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-offset-0 transition-all resize-none"
      :class="[
        isDarkMode
          ? 'bg-gray-800 border-transparent text-gray-300 placeholder-gray-500 focus:ring-amber-500'
          : 'bg-white border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-500',
        error ? 'border-red-500' : ''
      ]"
    ></textarea>

    <!-- Select Dropdown -->
    <select
      v-else-if="type === 'select'"
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value)"
      class="w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-offset-0 transition-all"
      :class="[
        isDarkMode
          ? 'bg-gray-800 border-transparent text-gray-300 focus:ring-amber-500'
          : 'bg-white border-transparent text-gray-900 focus:ring-amber-500',
        error ? 'border-red-500' : ''
      ]"
    >
      <option value="" disabled>{{ placeholder || 'Select an option' }}</option>
      <option
        v-for="option in options"
        :key="option.value"
        :value="option.value"
      >
        {{ option.label }}
      </option>
    </select>

    <!-- Error Message -->
    <p
      v-if="error"
      class="mt-1 text-sm text-red-500"
    >
      {{ error }}
    </p>
  </div>
</template>

<script setup>
import { inject } from 'vue'

defineProps({
  label: {
    type: String,
    required: true
  },
  modelValue: {
    type: [String, Number],
    default: ''
  },
  type: {
    type: String,
    default: 'text',
    validator: (value) => ['text', 'textarea', 'select'].includes(value)
  },
  placeholder: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  },
  rows: {
    type: Number,
    default: 4
  },
  options: {
    type: Array,
    default: () => []
  },
  error: {
    type: String,
    default: ''
  }
})

defineEmits(['update:modelValue'])

const isDarkMode = inject('isDarkMode')
</script>
<template>
  <div :class="containerClass">
    <label 
      class="block text-sm font-semibold mb-3"
      :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
    >
      {{ label }}
      <span v-if="required" class="text-red-400 font-bold">*</span>
    </label>
    <div class="flex gap-3">
      <label 
        class="flex items-center gap-2 cursor-pointer px-4 py-2 rounded-lg border transition-all hover:shadow-md"
        :class="model === '0' 
          ? (isDarkMode 
            ? 'bg-red-600/20 border-red-600/50 shadow-md' 
            : 'bg-red-100 border-red-300 shadow-md')
          : (isDarkMode 
            ? 'bg-gray-700 border-transparent' 
            : 'bg-white border-transparent')"
      >
        <input 
          type="radio" 
          :name="name"
          value="0" 
          v-model="model"
          class="w-4 h-4 text-red-600 cursor-pointer" 
        />
        <span 
          class="text-sm font-semibold"
          :class="model === '0' 
            ? (isDarkMode ? 'text-red-400' : 'text-red-700')
            : (isDarkMode ? 'text-gray-300' : 'text-gray-700')"
        >
          No (0)
        </span>
      </label>
      
      <label 
        class="flex items-center gap-2 cursor-pointer px-4 py-2 rounded-lg border transition-all hover:shadow-md"
        :class="model === '1' 
          ? (isDarkMode 
            ? 'bg-amber-600/20 border-amber-600/50 shadow-md' 
            : 'bg-amber-100 border-amber-300 shadow-md')
          : (isDarkMode 
            ? 'bg-gray-700 border-transparent' 
            : 'bg-white border-transparent')"
      >
        <input 
          type="radio" 
          :name="name"
          value="1" 
          v-model="model"
          class="w-4 h-4 text-amber-600 cursor-pointer" 
        />
        <span 
          class="text-sm font-semibold"
          :class="model === '1' 
            ? (isDarkMode ? 'text-amber-400' : 'text-amber-700')
            : (isDarkMode ? 'text-gray-300' : 'text-gray-700')"
        >
          Partially (0.5)
        </span>
      </label>
      
      <label 
        class="flex items-center gap-2 cursor-pointer px-4 py-2 rounded-lg border transition-all hover:shadow-md"
        :class="model === '2' 
          ? (isDarkMode 
            ? 'bg-green-600/20 border-green-600/50 shadow-md' 
            : 'bg-green-100 border-green-300 shadow-md')
          : (isDarkMode 
            ? 'bg-gray-700 border-transparent' 
            : 'bg-white border-transparent')"
      >
        <input 
          type="radio" 
          :name="name"
          value="2" 
          v-model="model"
          class="w-4 h-4 text-green-600 cursor-pointer" 
        />
        <span 
          class="text-sm font-semibold"
          :class="model === '2' 
            ? (isDarkMode ? 'text-green-400' : 'text-green-700')
            : (isDarkMode ? 'text-gray-300' : 'text-gray-700')"
        >
          Yes (1)
        </span>
      </label>
    </div>
    <p 
      v-if="hint" 
      class="text-xs mt-2"
      :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
    >
      {{ hint }}
    </p>
  </div>
</template>

<script setup>
import { computed, inject } from 'vue'

const isDarkMode = inject('isDarkMode')

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  label: {
    type: String,
    required: true
  },
  name: {
    type: String,
    required: true
  },
  required: {
    type: Boolean,
    default: false
  },
  hint: {
    type: String,
    default: ''
  },
  containerClass: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const model = computed({
  get: () => String(props.modelValue),
  set: (value) => emit('update:modelValue', String(value))
})
</script>
<template>
  <div 
    class="rounded-lg shadow-xl p-4 border"
    :class="isDarkMode 
      ? 'bg-gray-800 border-transparent' 
      : 'bg-white border-transparent'"
  >
    <div class="flex flex-wrap gap-2">
      <button
        v-for="(section, index) in sections"
        :key="index"
        @click="$emit('change-section', index)"
        :class="[
          'px-4 py-3 rounded-lg font-medium text-sm transition-all duration-200 flex items-center gap-2',
          activeSection === index 
            ? (isDarkMode 
              ? 'bg-amber-600 text-white shadow-lg shadow-blue-900/50 transform scale-105' 
              : 'bg-amber-700 text-white shadow-lg shadow-amber-900/30 transform scale-105')
            : (isDarkMode 
              ? 'bg-gray-700 text-gray-300 border border-transparent hover:border-amber-500 hover:text-amber-500' 
              : 'bg-white text-gray-700 border border-transparent hover:border-amber-600 hover:text-amber-700')
        ]"
      >
        <span>{{ section.name }}</span>
        <span 
          v-if="index < sections.length - 1"
          :class="[
            'px-2 py-0.5 rounded-full text-xs font-bold',
            getScoreColor(section.score)
          ]"
        >
          {{ section.score }}%
        </span>
      </button>

      <!-- Submit Section -->
      <button
        @click="$emit('change-section', sections.length - 1)"
        :class="[
          'px-6 py-3 rounded-lg font-bold text-sm transition-all duration-200 flex items-center gap-2',
          activeSection === sections.length - 1
            ? 'bg-green-600 text-white shadow-lg shadow-green-900/50 transform scale-105'
            : 'bg-green-600/80 text-white hover:bg-green-600'
        ]"
      >
        <i-mdi-check class="w-4 h-4" />
        <span>Submit</span>
        <span class="px-2 py-0.5 bg-white/20 rounded-full text-xs font-bold">
          Total: {{ totalScore }}%
        </span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, inject } from 'vue'

const isDarkMode = inject('isDarkMode')

const props = defineProps({
  sections: {
    type: Array,
    required: true
  },
  activeSection: {
    type: Number,
    default: 0
  }
})

defineEmits(['change-section'])

const totalScore = computed(() => {
  const scores = props.sections.slice(0, -1).map(s => s.score)
  const average = scores.reduce((sum, score) => sum + score, 0) / scores.length
  return Math.round(average)
})

const getScoreColor = (score) => {
  if (score >= 90) return 'bg-green-500 text-white'
  if (score >= 75) return isDarkMode.value ? 'bg-amber-500 text-white' : 'bg-amber-500 text-white'
  if (score >= 50) return 'bg-amber-500 text-white'
  return 'bg-red-500 text-white'
}
</script>
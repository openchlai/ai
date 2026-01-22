<script setup>
import { watch, ref, computed, inject } from "vue"
import { useCaseStore } from "@/stores/cases"

// Inject theme
const isDarkMode = inject('isDarkMode')

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({})
  }
})

const store = useCaseStore()
const localData = ref([])

const fetchData = async () => {
  await store.listCases({
    xaxis: "reporter_location_0",
    yaxis: "-",
    metrics: "case_count",
    ...props.filters
  })
  localData.value = [...store.cases]
}

// Theme-aware color palettes
const colorPalettes = {
  dark: [
    '#3B82F6', // Blue
    '#10B981', // Green
    '#F59E0B', // Amber
    '#EF4444', // Red
    '#8B5CF6', // Purple
    '#EC4899', // Pink
    '#14B8A6', // Teal
    '#F97316'  // Orange
  ],
  light: [
    '#B45309', // Amber-700
    '#059669', // Emerald-600
    '#DC2626', // Red-600
    '#7C3AED', // Violet-600
    '#DB2777', // Pink-600
    '#0D9488', // Teal-600
    '#EA580C', // Orange-600
    '#CA8A04'  // Yellow-600
  ]
}

// Compute chart data with theme-aware colors
const chartData = computed(() => {
  if (!localData.value || localData.value.length === 0) return []
  
  const total = localData.value.reduce((sum, row) => sum + parseInt(row[1]), 0)
  let currentAngle = 0
  
  const colors = isDarkMode.value ? colorPalettes.dark : colorPalettes.light
  
  return localData.value.map((row, index) => {
    const value = parseInt(row[1])
    const percentage = (value / total) * 100
    const angle = (value / total) * 360
    
    const slice = {
      label: row[0] || 'Not Specified',
      value: value,
      percentage: percentage.toFixed(1),
      color: colors[index % colors.length],
      startAngle: currentAngle,
      endAngle: currentAngle + angle
    }
    
    currentAngle += angle
    return slice
  })
})

// Calculate total cases
const totalCases = computed(() => {
  if (!localData.value || localData.value.length === 0) return 0
  return localData.value.reduce((sum, row) => sum + parseInt(row[1]), 0)
})

// Generate SVG path for pie slice
const getSlicePath = (startAngle, endAngle) => {
  const cx = 100
  const cy = 100
  const radius = 80
  
  const startRad = (startAngle - 90) * Math.PI / 180
  const endRad = (endAngle - 90) * Math.PI / 180
  
  const x1 = cx + radius * Math.cos(startRad)
  const y1 = cy + radius * Math.sin(startRad)
  const x2 = cx + radius * Math.cos(endRad)
  const y2 = cy + radius * Math.sin(endRad)
  
  const largeArc = endAngle - startAngle > 180 ? 1 : 0
  
  return `M ${cx} ${cy} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z`
}

// Watch filters and refetch when they change
watch(() => props.filters, () => {
  fetchData()
}, { deep: true, immediate: true })
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 
        class="font-semibold text-base"
        :class="isDarkMode ? 'text-gray-200' : 'text-gray-800'"
      >
        Cases by Reporter Location
      </h2>
      <div 
        class="text-3xl font-bold"
        :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
      >
        {{ totalCases }} 
        <span 
          class="text-sm font-normal"
          :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
        >
          Total
        </span>
      </div>
    </div>

    <div 
      v-if="!localData || localData.length === 0" 
      class="text-center py-12"
      :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
    >
      No data available
    </div>

    <div v-else class="space-y-6">
      <!-- SVG Pie Chart -->
      <div class="flex justify-center py-4">
        <svg viewBox="0 0 200 200" class="w-72 h-72">
          <g v-for="(slice, index) in chartData" :key="index">
            <path
              :d="getSlicePath(slice.startAngle, slice.endAngle)"
              :fill="slice.color"
              class="hover:opacity-90 transition-opacity cursor-pointer"
              :stroke="isDarkMode ? '#1F2937' : '#F3F4F6'"
              stroke-width="3"
            >
              <title>{{ slice.label }}: {{ slice.value }} ({{ slice.percentage }}%)</title>
            </path>
          </g>
        </svg>
      </div>

      <!-- Legend -->
      <div class="grid grid-cols-2 gap-3 text-sm">
        <div 
          v-for="(slice, index) in chartData" 
          :key="index"
          class="flex items-center gap-3 px-3 py-2 rounded"
          :class="isDarkMode ? 'bg-gray-900/40' : 'bg-gray-50'"
        >
          <div 
            class="w-3 h-3 rounded-sm flex-shrink-0"
            :style="{ backgroundColor: slice.color }"
          ></div>
          <span 
            class="truncate flex-1"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            {{ slice.label }}
          </span>
          <span 
            class="font-medium"
            :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
          >
            {{ slice.value }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
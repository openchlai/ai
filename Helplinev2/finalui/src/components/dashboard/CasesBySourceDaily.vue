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
    xaxis: "src",
    yaxis: "dt",
    metrics: "case_count",
    ...props.filters
  })
  localData.value = [...store.cases]
}

// Convert unix timestamp to readable date
const formatDate = (unixTimestamp) => {
  const date = new Date(parseInt(unixTimestamp) * 1000)
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

// Theme-aware color mappings for sources
const sourceColors = computed(() => {
  if (isDarkMode.value) {
    return {
      'call': '#3B82F6',     // Blue
      'ceemis': '#10B981',   // Green
      'chat': '#F59E0B',     // Amber
      'safepal': '#EF4444',  // Red
      'walkin': '#8B5CF6',   // Purple
      'webform': '#EC4899',  // Pink
      'sms': '#14B8A6',      // Teal
      'email': '#F97316',    // Orange
      'social': '#6366F1'    // Indigo
    }
  } else {
    return {
      'call': '#B45309',     // Amber-700
      'ceemis': '#059669',   // Emerald-600
      'chat': '#EA580C',     // Orange-600
      'safepal': '#DC2626',  // Red-600
      'walkin': '#7C3AED',   // Violet-600
      'webform': '#DB2777',  // Pink-600
      'sms': '#0D9488',      // Teal-600
      'email': '#CA8A04',    // Yellow-600
      'social': '#0891B2'    // Cyan-600
    }
  }
})

// Process data for chart
const chartData = computed(() => {
  if (!localData.value || localData.value.length === 0) return { sources: [], dates: [], series: [] }
  
  // Group data by source and date
  const sourceMap = {}
  const datesSet = new Set()
  
  localData.value.forEach(row => {
    const source = row[0]
    const timestamp = row[1]
    const cases = parseInt(row[2])
    
    if (!sourceMap[source]) {
      sourceMap[source] = {}
    }
    sourceMap[source][timestamp] = cases
    datesSet.add(timestamp)
  })
  
  // Sort dates
  const sortedDates = Array.from(datesSet).sort((a, b) => parseInt(a) - parseInt(b))
  
  // Create series data for each source
  const series = Object.keys(sourceMap).map(source => ({
    name: source,
    color: sourceColors.value[source] || (isDarkMode.value ? '#6B7280' : '#78716C'),
    data: sortedDates.map(date => sourceMap[source][date] || 0)
  }))
  
  return {
    sources: Object.keys(sourceMap),
    dates: sortedDates,
    series
  }
})

// Calculate total cases
const totalCases = computed(() => {
  if (!localData.value || localData.value.length === 0) return 0
  return localData.value.reduce((sum, row) => sum + parseInt(row[2]), 0)
})

// Get max value for scaling
const maxValue = computed(() => {
  if (chartData.value.series.length === 0) return 0
  return Math.max(...chartData.value.series.flatMap(s => s.data))
})

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
        Cases by Source Per Day
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
      <!-- Bar Chart -->
      <div 
        class="w-full overflow-x-auto rounded-lg p-4"
        :class="isDarkMode ? 'bg-gray-900/40' : 'bg-gray-50'"
      >
        <svg :viewBox="`0 0 ${Math.max(600, chartData.dates.length * 100)} 280`" class="w-full" :style="`min-width: ${Math.max(600, chartData.dates.length * 100)}px;`">
          <!-- Grid lines -->
          <g v-for="i in 5" :key="'grid-' + i">
            <line
              :x1="60"
              :y1="40 + (i - 1) * 40"
              :x2="Math.max(600, chartData.dates.length * 100) - 40"
              :y2="40 + (i - 1) * 40"
              :stroke="isDarkMode ? '#374151' : '#E5E7EB'"
              stroke-width="1"
              opacity="0.5"
            />
            <!-- Y-axis labels -->
            <text
              :x="50"
              :y="44 + (i - 1) * 40"
              text-anchor="end"
              :class="isDarkMode ? 'fill-gray-500' : 'fill-gray-500'"
              class="text-xs"
              font-size="11"
            >
              {{ Math.round(maxValue - (i - 1) * (maxValue / 4)) }}
            </text>
          </g>
          
          <!-- Bars grouped by date -->
          <g v-for="(date, dateIndex) in chartData.dates" :key="'date-group-' + dateIndex">
            <g v-for="(serie, serieIndex) in chartData.series" :key="serie.name">
              <rect
                v-if="serie.data[dateIndex] > 0"
                :x="60 + dateIndex * 100 + serieIndex * (80 / chartData.series.length)"
                :y="240 - 40 - ((serie.data[dateIndex] / maxValue) * 160)"
                :width="80 / chartData.series.length - 2"
                :height="(serie.data[dateIndex] / maxValue) * 160"
                :fill="serie.color"
                class="hover:opacity-90 transition-opacity"
                rx="2"
              >
                <title>{{ serie.name }}: {{ serie.data[dateIndex] }} on {{ formatDate(date) }}</title>
              </rect>
            </g>
            
            <!-- X-axis labels (dates) -->
            <text
              :x="60 + dateIndex * 100 + 40"
              y="265"
              text-anchor="middle"
              :class="isDarkMode ? 'fill-gray-500' : 'fill-gray-500'"
              class="text-xs"
              font-size="11"
            >
              {{ formatDate(date) }}
            </text>
          </g>
        </svg>
      </div>

      <!-- Legend -->
      <div class="flex flex-wrap gap-3 text-sm">
        <div 
          v-for="serie in chartData.series" 
          :key="serie.name"
          class="flex items-center gap-2 px-3 py-1.5 rounded"
          :class="isDarkMode ? 'bg-gray-900/40' : 'bg-gray-50'"
        >
          <div 
            class="w-3 h-3 rounded-sm flex-shrink-0"
            :style="{ backgroundColor: serie.color }"
          ></div>
          <span 
            class="capitalize"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            {{ serie.name }}
          </span>
          <span 
            class="font-medium"
            :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
          >
            ({{ serie.data.reduce((a, b) => a + b, 0) }})
          </span>
        </div>
      </div>
    </div>
  </div>
</template>
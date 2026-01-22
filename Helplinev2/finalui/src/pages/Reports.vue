<template>
  <div 
    class="min-h-screen p-6"
    :class="isDarkMode ? 'bg-black' : 'bg-gray-50'"
  >
    <div class="max-w-7xl mx-auto">
      <!-- Page Header -->
      <div class="mb-6">
        <h1 
          class="text-3xl font-bold flex items-center gap-3"
          :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
        >
          <i-mdi-chart-bar 
            class="w-8 h-8"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
          />
          Reports & Analytics
        </h1>
        <p 
          class="mt-2"
          :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
        >
          Visualize and analyze your data
        </p>
      </div>

      <!-- Controls Section -->
      <div 
        class="rounded-lg shadow-xl p-6 mb-6 border"
        :class="isDarkMode 
          ? 'bg-neutral-900 border-transparent' 
          : 'bg-white border-transparent'"
      >
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
         <!-- Endpoint Selection -->
<div>
  <label 
    class="block text-sm font-semibold mb-3"
    :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
  >
    Data Source
  </label>
  <select 
    v-model="selectedEndpoint" 
    class="w-full px-4 py-3 rounded-lg text-sm font-medium cursor-pointer transition-all duration-300 focus:outline-none focus:ring-2 focus:border-transparent"
    :class="isDarkMode 
      ? 'bg-gray-700 border border-transparent text-gray-100 hover:border-amber-600 focus:ring-amber-500' 
      : 'bg-gray-50 border border-transparent text-gray-900 hover:border-amber-600 focus:ring-amber-600'"
  >
    <option value="qa">QA Results</option>
    <option value="cases">Cases</option>
    <option value="calls">Call History</option>
    <!-- <option value="users">Users</option> -->  <!-- ✅ Just commented out -->
  </select>
</div>

          <!-- X-Axis (Time Duration) -->
          <div>
            <label 
              class="block text-sm font-semibold mb-3"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Time Period (X-Axis)
            </label>
            <div class="flex gap-2">
              <button
                v-for="period in timePeriods"
                :key="period.value"
                @click="selectTimePeriod(period.value)"
                :class="getTimePeriodButtonClass(xAxis === period.value)"
              >
                {{ period.label }}
              </button>
            </div>
          </div>
        </div>

        <!-- Y-Axis Filter Selection -->
        <div class="mt-6">
          <label 
            class="block text-sm font-semibold mb-3"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            Filter By (Y-Axis)
          </label>
          
          <!-- Available Options -->
          <div 
            class="rounded-lg p-4 mb-4 border"
            :class="isDarkMode 
              ? 'bg-black/60 border-transparent' 
              : 'bg-gray-100 border-transparent'"
          >
            <div class="flex flex-wrap gap-2">
              <button
                v-for="field in availableYAxisFields"
                :key="field"
                @click="toggleYAxis(field)"
                :disabled="selectedYAxis.includes(field)"
                :class="getYAxisButtonClass(selectedYAxis.includes(field))"
              >
                {{ formatFieldName(field) }}
              </button>
            </div>
          </div>

          <!-- Selected Filters -->
          <div 
            v-if="selectedYAxis.length > 0" 
            class="rounded-lg p-4 border"
            :class="isDarkMode 
              ? 'bg-amber-900/20 border-amber-600/30' 
              : 'bg-amber-50 border-amber-300'"
          >
            <div class="flex items-center justify-between mb-2">
              <span 
                class="text-sm font-semibold"
                :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
              >
                Selected Filters
              </span>
              <button
                @click="clearAllFilters"
                class="text-xs font-medium flex items-center gap-1"
                :class="isDarkMode 
                  ? 'text-amber-500 hover:text-blue-300' 
                  : 'text-amber-700 hover:text-amber-600'"
              >
                <i-mdi-close class="w-3 h-3" />
                Clear All
              </button>
            </div>
            <div class="flex flex-wrap gap-2">
              <div
                v-for="(field, index) in selectedYAxis"
                :key="field"
                class="flex items-center gap-2 px-3 py-2 text-white rounded-lg text-sm font-medium shadow-sm"
                :class="isDarkMode ? 'bg-amber-600' : 'bg-amber-700'"
              >
                <span>{{ formatFieldName(field) }}</span>
                <button
                  @click="removeYAxis(index)"
                  class="rounded p-0.5 transition-colors"
                  :class="isDarkMode 
                    ? 'hover:bg-amber-700' 
                    : 'hover:bg-amber-800'"
                >
                  <i-mdi-close class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          <p 
            v-else 
            class="text-sm italic"
            :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
          >
            No filters selected. Click on options above to add filters.
          </p>
        </div>
      </div>

      <!-- Graph Section -->
      <div 
        class="rounded-lg shadow-xl p-6 mb-6 border"
        :class="isDarkMode 
          ? 'bg-neutral-900 border-transparent' 
          : 'bg-white border-transparent'"
      >
        <div class="flex items-center justify-between mb-6">
          <h2 
            class="text-2xl font-bold flex items-center gap-2"
            :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
          >
            <i-mdi-chart-line 
              class="w-6 h-6"
              :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
            />
            {{ formatFieldName(selectedEndpoint) }} Analytics
          </h2>
          <div 
            class="px-4 py-2 rounded-lg text-sm font-medium border"
            :class="isDarkMode 
              ? 'bg-amber-600/20 text-amber-500 border-amber-600/30' 
              : 'bg-amber-100 text-amber-700 border-amber-300'"
          >
            {{ formatFieldName(currentMetric) }}
          </div>
        </div>

        <div 
          v-if="loading" 
          class="flex items-center justify-center h-96"
        >
          <div class="flex flex-col items-center gap-4">
            <div 
              class="animate-spin rounded-full h-12 w-12 border-4"
              :class="isDarkMode 
                ? 'border-amber-900/30 border-t-amber-500' 
                : 'border-amber-900/30 border-t-amber-600'"
            ></div>
            <div 
              class="font-medium"
              :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
            >
              Loading data...
            </div>
          </div>
        </div>

        <div 
          v-else-if="chartData.length === 0" 
          class="flex items-center justify-center h-96"
        >
          <div class="text-center">
            <i-mdi-chart-bar 
              class="mx-auto h-16 w-16"
              :class="isDarkMode ? 'text-gray-600' : 'text-gray-400'"
            />
            <p 
              class="mt-4 font-medium"
              :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
            >
              No data available
            </p>
            <p 
              class="mt-2 text-sm"
              :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
            >
              Select time period and filters to view analytics
            </p>
          </div>
        </div>

        <!-- Bar Chart -->
        <div 
          v-else 
          class="overflow-x-auto rounded-lg p-4 border"
          :class="isDarkMode 
            ? 'bg-gray-900/40 border-transparent' 
            : 'bg-gray-50 border-transparent'"
        >
          <div class="inline-block min-w-full">
            <svg :width="svgWidth" :height="svgHeight">
              <!-- Horizontal gridlines -->
              <g v-for="tick in yTicks" :key="'grid-' + tick">
                <line
                  :x1="margin.left"
                  :x2="svgWidth - margin.right"
                  :y1="yScale(tick)"
                  :y2="yScale(tick)"
                  :stroke="isDarkMode ? '#374151' : '#d1d5db'"
                  stroke-width="1"
                  stroke-dasharray="4"
                />
              </g>

              <!-- Bars -->
              <g v-for="(bar, index) in chartData" :key="'bar-' + index">
                <rect
                  :x="margin.left + index * (barWidth + barSpacing)"
                  :y="yScale(bar.value)"
                  :width="barWidth"
                  :height="svgHeight - margin.bottom - yScale(bar.value)"
                  :fill="isDarkMode ? 'url(#barGradientDark)' : 'url(#barGradientLight)'"
                  class="cursor-pointer hover:opacity-80 transition-opacity"
                  rx="4"
                />
                <!-- Value labels on bars -->
                <text
                  :x="margin.left + index * (barWidth + barSpacing) + barWidth / 2"
                  :y="yScale(bar.value) - 8"
                  text-anchor="middle"
                  font-size="11"
                  font-weight="600"
                  :class="isDarkMode ? 'fill-amber-500' : 'fill-amber-700'"
                >
                  {{ bar.value }}
                </text>
                <!-- X-axis labels -->
                <text
                  :x="margin.left + index * (barWidth + barSpacing) + barWidth / 2"
                  :y="svgHeight - margin.bottom + 20"
                  text-anchor="middle"
                  font-size="11"
                  font-weight="500"
                  :class="isDarkMode ? 'fill-gray-400' : 'fill-gray-600'"
                >
                  {{ bar.label }}
                </text>
              </g>

              <!-- Y-axis labels -->
              <g v-for="tick in yTicks" :key="'label-' + tick">
                <text
                  :x="margin.left - 8"
                  :y="yScale(tick) + 4"
                  text-anchor="end"
                  font-size="11"
                  font-weight="500"
                  :class="isDarkMode ? 'fill-gray-400' : 'fill-gray-600'"
                >
                  {{ tick }}
                </text>
              </g>

              <!-- X-axis line -->
              <line
                :x1="margin.left"
                :x2="svgWidth - margin.right"
                :y1="svgHeight - margin.bottom"
                :y2="svgHeight - margin.bottom"
                :stroke="isDarkMode ? '#6b7280' : '#9ca3af'"
                stroke-width="2"
              />

              <!-- Y-axis line -->
              <line
                :x1="margin.left"
                :x2="margin.left"
                :y1="margin.top"
                :y2="svgHeight - margin.bottom"
                :stroke="isDarkMode ? '#6b7280' : '#9ca3af'"
                stroke-width="2"
              />

              <!-- Gradients for bars -->
              <defs>
                <!-- Dark mode gradient -->
                <linearGradient id="barGradientDark" x1="0" y1="1" x2="0" y2="0">
                  <stop offset="0%" stop-color="#d97706" />
                  <stop offset="100%" stop-color="#fbbf24" />
                </linearGradient>
                <!-- Light mode gradient -->
                <linearGradient id="barGradientLight" x1="0" y1="1" x2="0" y2="0">
                  <stop offset="0%" stop-color="#b45309" />
                  <stop offset="100%" stop-color="#f59e0b" />
                </linearGradient>
              </defs>
            </svg>
          </div>
        </div>
      </div>

      <!-- Table Section -->
      <div 
        class="rounded-lg shadow-xl p-6 border"
        :class="isDarkMode 
          ? 'bg-neutral-900 border-transparent' 
          : 'bg-white border-transparent'"
      >
        <h2 
          class="text-2xl font-bold mb-6 flex items-center gap-2"
          :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
        >
          <i-mdi-table 
            class="w-6 h-6"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
          />
          Data Table
        </h2>
        
        <div 
          v-if="loading" 
          class="flex items-center justify-center h-64"
        >
          <div class="flex flex-col items-center gap-4">
            <div 
              class="animate-spin rounded-full h-12 w-12 border-4"
              :class="isDarkMode 
                ? 'border-amber-900/30 border-t-amber-500' 
                : 'border-amber-900/30 border-t-amber-600'"
            ></div>
            <div 
              class="font-medium"
              :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
            >
              Loading data...
            </div>
          </div>
        </div>

        <div 
          v-else-if="tableData.length === 0" 
          class="flex items-center justify-center h-64"
        >
          <div class="text-center">
            <i-mdi-table 
              class="mx-auto h-16 w-16"
              :class="isDarkMode ? 'text-gray-600' : 'text-gray-400'"
            />
            <p 
              class="mt-4 font-medium"
              :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
            >
              No data available
            </p>
            <p 
              class="mt-2 text-sm"
              :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
            >
              Select time period and filters to view data
            </p>
          </div>
        </div>

        <div 
          v-else 
          class="overflow-x-auto rounded-lg border"
          :class="isDarkMode ? 'border-transparent' : 'border-transparent'"
        >
          <table 
            class="min-w-full divide-y"
            :class="isDarkMode ? 'divide-gray-700' : 'divide-gray-200'"
          >
            <thead 
              :class="isDarkMode ? 'bg-gray-900/60' : 'bg-gray-50'"
            >
              <tr>
                <!-- Dynamic filter columns -->
                <th 
                  v-for="(filter, idx) in selectedYAxis" 
                  :key="'filter-' + idx"
                  class="px-6 py-4 text-left text-xs font-bold uppercase tracking-wider"
                  :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                >
                  {{ formatFieldName(filter) }}
                </th>
                <!-- Time period columns -->
                <th 
                  v-for="period in tableTimePeriods" 
                  :key="'period-' + period"
                  class="px-6 py-4 text-center text-xs font-bold uppercase tracking-wider"
                  :class="isDarkMode 
                    ? 'text-gray-300 bg-amber-900/20' 
                    : 'text-gray-700 bg-amber-50'"
                >
                  {{ period }}
                </th>
                <th 
                  class="px-6 py-4 text-center text-xs font-bold uppercase tracking-wider"
                  :class="isDarkMode 
                    ? 'text-amber-500 bg-amber-900/30' 
                    : 'text-amber-700 bg-amber-100'"
                >
                  Total
                </th>
              </tr>
            </thead>
            <tbody 
              class="divide-y"
              :class="isDarkMode 
                ? 'bg-gray-800 divide-gray-700' 
                : 'bg-white divide-gray-200'"
            >
              <tr 
                v-for="(row, rowIdx) in tableData" 
                :key="'row-' + rowIdx" 
                class="transition-colors"
                :class="isDarkMode 
                  ? 'hover:bg-gray-700/30' 
                  : 'hover:bg-gray-50'"
              >
                <!-- Filter value cells -->
                <td 
                  v-for="(filter, filterIdx) in selectedYAxis" 
                  :key="'cell-filter-' + filterIdx"
                  class="px-6 py-4 whitespace-nowrap text-sm font-medium"
                >
                  <span 
                    class="inline-flex items-center px-3 py-1 rounded-lg"
                    :class="isDarkMode 
                      ? 'bg-gray-700 text-gray-300' 
                      : 'bg-gray-100 text-gray-700'"
                  >
                    {{ row.filters[filterIdx] || '-' }}
                  </span>
                </td>
                <!-- Count cells for each period -->
                <td 
                  v-for="(count, periodIdx) in row.counts" 
                  :key="'cell-count-' + periodIdx"
                  class="px-6 py-4 whitespace-nowrap text-sm text-center font-medium"
                  :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                >
                  {{ count }}
                </td>
                <!-- Total cell -->
                <td 
                  class="px-6 py-4 whitespace-nowrap text-sm text-center font-bold"
                  :class="isDarkMode 
                    ? 'text-amber-500 bg-amber-900/20' 
                    : 'text-amber-700 bg-amber-50'"
                >
                  {{ row.total }}
                </td>
              </tr>
              <!-- Total row -->
              <tr 
                class="font-bold"
                :class="isDarkMode ? 'bg-gray-900/60' : 'bg-gray-100'"
              >
                <td 
                  :colspan="selectedYAxis.length"
                  class="px-6 py-4 whitespace-nowrap text-sm uppercase"
                  :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
                >
                  Total
                </td>
                <td 
                  v-for="(total, idx) in columnTotals" 
                  :key="'total-' + idx"
                  class="px-6 py-4 whitespace-nowrap text-sm text-center"
                  :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
                >
                  {{ total }}
                </td>
                <td 
                  class="px-6 py-4 whitespace-nowrap text-sm text-center"
                  :class="isDarkMode 
                    ? 'text-amber-500 bg-amber-900/30' 
                    : 'text-amber-700 bg-amber-100'"
                >
                  {{ grandTotal }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, inject } from 'vue'
import { useCaseStore } from '@/stores/cases'
import { useCallStore } from '@/stores/calls'
import { useQAStore } from '@/stores/qas'
import { useUserStore } from '@/stores/users'

// Inject theme
const isDarkMode = inject('isDarkMode')

// Dynamic button class for time period selection
const getTimePeriodButtonClass = (isActive) => {
  const baseClasses = 'flex-1 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200'
  
  if (isActive) {
    return isDarkMode.value
      ? `${baseClasses} bg-amber-600 text-white shadow-lg shadow-amber-900/50`
      : `${baseClasses} bg-amber-700 text-white shadow-lg shadow-amber-900/30`
  } else {
    return isDarkMode.value
      ? `${baseClasses} bg-gray-700 text-gray-300 border border-transparent hover:border-amber-600 hover:text-amber-500`
      : `${baseClasses} bg-gray-100 text-gray-700 border border-transparent hover:border-amber-600 hover:text-amber-700`
  }
}

// Dynamic button class for Y-axis selection
const getYAxisButtonClass = (isDisabled) => {
  const baseClasses = 'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200'
  
  if (isDisabled) {
    return isDarkMode.value
      ? `${baseClasses} bg-gray-700 text-gray-500 cursor-not-allowed`
      : `${baseClasses} bg-gray-200 text-gray-400 cursor-not-allowed`
  } else {
    return isDarkMode.value
      ? `${baseClasses} bg-gray-800 text-gray-300 border border-transparent hover:border-amber-600 hover:bg-amber-900/20 cursor-pointer`
      : `${baseClasses} bg-white text-gray-700 border border-transparent hover:border-amber-600 hover:bg-amber-50 cursor-pointer`
  }
}

// Store instances
const caseStore = useCaseStore()
const callStore = useCallStore()
const qaStore = useQAStore()
const userStore = useUserStore()

// State
const selectedEndpoint = ref('qa')
const xAxis = ref('')
const selectedYAxis = ref([])
const loading = ref(false)
const rawData = ref([])

// Time periods for button selection
const timePeriods = [
  { label: 'Hour', value: 'h' },
  { label: 'Day', value: 'dt' },
  { label: 'Week', value: 'wk' },
  { label: 'Month', value: 'mn' },
  { label: 'Year', value: 'yr' }
]

// Chart dimensions & spacing - UPDATED
const margin = { top: 20, right: 20, bottom: 50, left: 50 }

// Dynamic bar width and spacing based on time period
const barWidth = computed(() => {
  // For day view, use wider spacing since dates take more space
  if (xAxis.value === 'dt') return 60
  // For week view, also needs more space
  if (xAxis.value === 'wk') return 55
  // For month view
  if (xAxis.value === 'mn') return 50
  // For hour and year, normal spacing is fine
  return 35
})

const barSpacing = computed(() => {
  // For day view, add more spacing between bars
  if (xAxis.value === 'dt') return 30
  // For week view
  if (xAxis.value === 'wk') return 25
  // For month view
  if (xAxis.value === 'mn') return 20
  // For hour and year
  return 20
})

const svgHeight = 400

// Endpoint configurations
const endpointConfig = {
  qa: {
    store: qaStore,
    method: 'listQA',
    yAxisFields: ['Extension'],
    metric: 'qa_count',
    storeKey: 'qas'  // ✅ Changed from 'qaResults' to 'qas'
  },
  cases: {
    store: caseStore,
    method: 'listCases',
    yAxisFields: ['Case', 'Reporter', 'Client', 'Perpetrator', 'Services', 'Referrals', 'Main Category', 'SubCategory 1', 'SubCategory 2', 'SubCategory 3', 'GBV Related', 'Case Source', 'Priority', 'Status', 'Created By', 'Escalated To', 'Escalated By', 'Case Assessment', 'Status in the Justice System'],
    metric: 'case_count',
    storeKey: 'cases'
  },
  calls: {
    store: callStore,
    method: 'listCalls',
    yAxisFields: ['Direction', 'Extension', 'Hangup Status', 'SLA Band', 'Disposition'],
    metric: 'call_count',
    storeKey: 'calls'
  },
  users: {
    store: userStore,
    method: 'listUsers',
    yAxisFields: ['Role', 'Department', 'Status', 'Team'],
    metric: 'user_count',
    storeKey: 'users'
  }
}

// Available fields based on selected endpoint
const availableYAxisFields = computed(() => {
  return endpointConfig[selectedEndpoint.value]?.yAxisFields || []
})

const currentMetric = computed(() => {
  return endpointConfig[selectedEndpoint.value]?.metric || ''
})

// Select time period and fetch data
function selectTimePeriod(period) {
  xAxis.value = period
  if (selectedYAxis.value.length > 0) {
    fetchData()
  }
}

// Toggle Y-Axis selection and fetch data if time period is set
function toggleYAxis(field) {
  if (!selectedYAxis.value.includes(field)) {
    selectedYAxis.value.push(field)
    if (xAxis.value) {
      fetchData()
    }
  }
}

// Remove Y-Axis selection
function removeYAxis(index) {
  selectedYAxis.value.splice(index, 1)
  if (selectedYAxis.value.length > 0 && xAxis.value) {
    fetchData()
  } else {
    rawData.value = []
    chartData.value = []
  }
}

// Clear all filters
function clearAllFilters() {
  selectedYAxis.value = []
  rawData.value = []
  chartData.value = []
}

// Watch endpoint changes and reset selections
watch(selectedEndpoint, () => {
  selectedYAxis.value = []
  xAxis.value = ''
  rawData.value = []
  chartData.value = []
})

// Fetch data from appropriate store
async function fetchData() {
  if (selectedYAxis.value.length === 0 || !xAxis.value) {
    return
  }

  loading.value = true
  try {
    const config = endpointConfig[selectedEndpoint.value]
    const store = config.store
    const method = config.method

    const params = {
      xaxis: xAxis.value,
      yaxis: selectedYAxis.value.join(','),
      metrics: config.metric
    }

    await store[method](params)
    rawData.value = store[config.storeKey] || []
    processData()
  } catch (err) {
    console.error('[Reports] fetchData error', err)
    rawData.value = []
  } finally {
    loading.value = false
  }
}

// Process raw data for chart
const chartData = ref([])

function processData() {
  if (!rawData.value || rawData.value.length === 0) {
    chartData.value = []
    return
  }

  const grouped = {}
  
  rawData.value.forEach(row => {
    if (!Array.isArray(row) || row.length === 0) return
    
    const timePeriod = String(row[0])
    const value = Number(row[row.length - 1]) || 0
    
    grouped[timePeriod] = (grouped[timePeriod] || 0) + value
  })

  const entries = Object.entries(grouped)
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => {
      const na = Number(a.label), nb = Number(b.label)
      if (!isNaN(na) && !isNaN(nb)) return na - nb
      return String(a.label).localeCompare(String(b.label))
    })

  chartData.value = entries.map(e => ({
    label: formatLabel(e.label),
    value: e.value
  }))
}

// Process data for table
const tableData = computed(() => {
  if (!rawData.value || rawData.value.length === 0) return []

  const groups = {}
  const periods = new Set()

  rawData.value.forEach(row => {
    if (!Array.isArray(row) || row.length === 0) return

    const timePeriod = String(row[0])
    const count = Number(row[row.length - 1]) || 0
    
    const filterValues = []
    for (let i = 1; i < row.length - 1; i++) {
      filterValues.push(String(row[i] || ''))
    }

    const filterKey = filterValues.join('|')
    periods.add(timePeriod)

    if (!groups[filterKey]) {
      groups[filterKey] = {
        filters: filterValues,
        periodCounts: {}
      }
    }

    groups[filterKey].periodCounts[timePeriod] = 
      (groups[filterKey].periodCounts[timePeriod] || 0) + count
  })

  const sortedPeriods = Array.from(periods).sort((a, b) => {
    const na = Number(a), nb = Number(b)
    if (!isNaN(na) && !isNaN(nb)) return na - nb
    return a.localeCompare(b)
  })

  return Object.values(groups).map(group => {
    const counts = sortedPeriods.map(period => group.periodCounts[period] || 0)
    const total = counts.reduce((sum, val) => sum + val, 0)
    
    return {
      filters: group.filters,
      counts,
      total
    }
  })
})

// Time periods for table headers - use formatted labels
const tableTimePeriods = computed(() => {
  if (!rawData.value || rawData.value.length === 0) return []

  const periods = new Set()
  rawData.value.forEach(row => {
    if (Array.isArray(row) && row.length > 0) {
      periods.add(String(row[0]))
    }
  })

  return Array.from(periods).sort((a, b) => {
    const na = Number(a), nb = Number(b)
    if (!isNaN(na) && !isNaN(nb)) return na - nb
    return a.localeCompare(b)
  }).map(period => formatLabel(period))
})

// Column totals for table
const columnTotals = computed(() => {
  if (tableData.value.length === 0) return []
  
  const numColumns = tableData.value[0]?.counts.length || 0
  const totals = new Array(numColumns).fill(0)
  
  tableData.value.forEach(row => {
    row.counts.forEach((count, idx) => {
      totals[idx] += count
    })
  })
  
  return totals
})

const grandTotal = computed(() => {
  return columnTotals.value.reduce((sum, val) => sum + val, 0)
})

// Chart calculations
const svgWidth = computed(() =>
  Math.max(
    chartData.value.length * (barWidth.value + barSpacing.value) + margin.left + margin.right, 
    500
  )
)

const maxValue = computed(() => Math.max(...chartData.value.map(d => d.value), 1))

const yScale = (value) =>
  svgHeight - margin.bottom - (value / maxValue.value) * (svgHeight - margin.top - margin.bottom)

const yTicks = computed(() => {
  const steps = 5
  const stepValue = Math.ceil(maxValue.value / steps)
  return Array.from({ length: steps + 1 }, (_, i) => i * stepValue)
})

// Format label based on timeframe
function formatLabel(label) {
  if (xAxis.value === 'h') {
    return label
  }

  const timestamp = Number(label) * 1000
  const date = new Date(timestamp)

  switch (xAxis.value) {
    case 'dt':
      return date.toLocaleDateString('en-US', {
        day: '2-digit', month: 'short', year: 'numeric'
      })

    case 'wk':
      const weekStart = new Date(date)
      weekStart.setDate(date.getDate() - date.getDay())
      return `W${getWeekNumber(date)} (${weekStart.toLocaleDateString('en-US', {
        month: 'short', day: '2-digit'
      })})`

    case 'mn':
      return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })

    case 'yr':
      return date.getFullYear()

    default:
      return label
  }
}

function getWeekNumber(d) {
  const date = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()))
  const dayNum = date.getUTCDay() || 7
  date.setUTCDate(date.getUTCDate() + 4 - dayNum)
  const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1))
  return Math.ceil((((date - yearStart) / 86400000) + 1) / 7)
}

function formatFieldName(field) {
  return field
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ')
}
</script>
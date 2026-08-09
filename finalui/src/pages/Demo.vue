<template>
  <div class="analytics-card">
    <div class="card-header">
      <div class="section-title">Case Analytics</div>
      <select class="time-filter" v-model="selectedTimeframe">
        <option value="h">Hourly</option>
        <option value="dt">Daily</option>
        <option value="wk">Weekly</option>
        <option value="mn">Monthly</option>
        <option value="yr">Yearly</option>
      </select>
    </div>

    <div class="chart-container">
      <div class="chart-scroll">
        <svg :width="svgWidth" :height="svgHeight">
          <!-- Horizontal gridlines -->
          <g v-for="tick in yTicks" :key="'grid-' + tick">
            <line
              :x1="margin.left"
              :x2="svgWidth - margin.right"
              :y1="yScale(tick)"
              :y2="yScale(tick)"
              stroke="#ddd"
              stroke-width="1"
            />
          </g>

          <!-- Bars -->
          <g v-for="(bar, index) in chartData" :key="'bar-' + index">
            <rect
              :x="margin.left + index * (barWidth + barSpacing)"
              :y="yScale(bar.rawValue)"
              :width="barWidth"
              :height="svgHeight - margin.bottom - yScale(bar.rawValue)"
              fill="url(#barGradient)"
            />
            <!-- X-axis labels (timestamps) -->
            <text
              :x="margin.left + index * (barWidth + barSpacing) + barWidth / 2"
              :y="svgHeight - margin.bottom + 15"
              text-anchor="middle"
              font-size="10"
            >
              {{ formatLabel(bar.label) }}
            </text>
          </g>

          <!-- Y-axis labels -->
          <g v-for="tick in yTicks" :key="'label-' + tick">
            <text
              :x="margin.left - 5"
              :y="yScale(tick) + 3"
              text-anchor="end"
              font-size="10"
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
            stroke="#333"
            stroke-width="1.2"
          />

          <!-- Y-axis line -->
          <line
            :x1="margin.left"
            :x2="margin.left"
            :y1="margin.top"
            :y2="svgHeight - margin.bottom"
            stroke="#333"
            stroke-width="1.2"
          />

          <!-- Gradient for bars -->
          <defs>
            <linearGradient id="barGradient" x1="0" y1="1" x2="0" y2="0">
              <stop offset="0%" stop-color="var(--accent-color)" />
              <stop offset="100%" stop-color="#ff7700" />
            </linearGradient>
          </defs>
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import { useCaseStore } from '@/stores/cases'

const casesStore = useCaseStore()
const selectedTimeframe = ref('dt') // default daily
const chartData = ref([])

// Chart dimensions & spacing
const margin = { top: 20, right: 20, bottom: 40, left: 40 }
const barWidth = 30
const barSpacing = 15
const svgHeight = 300

// Dynamic width based on data count
const svgWidth = computed(() =>
  Math.max(chartData.value.length * (barWidth + barSpacing) + margin.left + margin.right, 400)
)

// Fetch data
async function fetchCases() {
  console.log('[Analytics] fetching cases with xaxis=', selectedTimeframe.value)
  try {
    await casesStore.listCases({
      xaxis: selectedTimeframe.value,
      yaxis: 'status',
      metrics: 'case_count'
    })
    processCases(casesStore.cases)
  } catch (err) {
    console.error('[Analytics] fetchCases error', err)
    chartData.value = []
  }
}

// Process data
function processCases(rawRows = []) {
  const grouped = {}
  rawRows.forEach(row => {
    if (!Array.isArray(row)) return
    let xVal, count
    if (row.length === 3) {
      xVal = String(row[0])
      count = Number(row[2]) || 0
    } else if (row.length === 2) {
      xVal = String(row[0])
      count = Number(row[1]) || 0
    } else {
      xVal = String(row[0])
      count = Number(row[row.length - 1]) || 0
    }
    grouped[xVal] = (grouped[xVal] || 0) + count
  })

  const entries = Object.entries(grouped)
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => {
      const na = Number(a.label), nb = Number(b.label)
      if (!isNaN(na) && !isNaN(nb)) return na - nb
      return String(a.label).localeCompare(String(b.label))
    })

  chartData.value = entries.map(e => ({
    label: e.label,
    rawValue: e.value
  }))
}

// Y scale & ticks
const maxValue = computed(() => Math.max(...chartData.value.map(d => d.rawValue), 1))
const yScale = (value) =>
  svgHeight - margin.bottom - (value / maxValue.value) * (svgHeight - margin.top - margin.bottom)

// Generate 5 ticks including 0
const yTicks = computed(() => {
  const steps = 5
  const stepValue = Math.ceil(maxValue.value / steps)
  return Array.from({ length: steps + 1 }, (_, i) => i * stepValue)
})

// Format label based on timeframe
function formatLabel(label) {
  const timestamp = Number(label) * 1000 // convert seconds → milliseconds
  const date = new Date(timestamp)

  switch (selectedTimeframe.value) {
    case 'h': // Hourly
      return `${date.getHours()}:00`

    case 'dt': // Daily
      return date.toLocaleDateString('en-US', {
        day: '2-digit', month: 'short', year: 'numeric'
      })

    case 'wk': // Weekly
      // Show starting week date (or use ISO week)
      const weekStart = new Date(date)
      weekStart.setDate(date.getDate() - date.getDay()) // Sunday start
      return `W${getWeekNumber(date)} (${weekStart.toLocaleDateString('en-US', {
        month: 'short', day: '2-digit'
      })})`

    case 'mn': // Monthly
      return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' })

    case 'yr': // Yearly
      return date.getFullYear()

    default:
      return label
  }
}

// Helper: ISO Week number
function getWeekNumber(d) {
  const date = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()))
  const dayNum = date.getUTCDay() || 7
  date.setUTCDate(date.getUTCDate() + 4 - dayNum)
  const yearStart = new Date(Date.UTC(date.getUTCFullYear(), 0, 1))
  return Math.ceil((((date - yearStart) / 86400000) + 1) / 7)
}


onMounted(fetchCases)
watch(selectedTimeframe, fetchCases)
</script>

<style scoped>
.analytics-card {
  background-color: var(--card-bg);
  border-radius: 30px;
  padding: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: background-color 0.3s;
}

.time-filter {
  padding: 8px 12px;
  background: var(--background-color);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.3s ease;
}

.chart-container {
  margin-top: 20px;
  overflow-x: auto;
}

.chart-scroll {
  display: inline-block;
  min-width: 100%;
}
</style>

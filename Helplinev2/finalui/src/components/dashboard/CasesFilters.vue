<template>
  <div 
    class="w-full rounded-lg p-4 shadow-xl border mb-4 flex flex-wrap gap-4"
    :class="isDarkMode 
      ? 'bg-neutral-900 border-transparent' 
      : 'bg-white border-transparent'"
  >

    <!-- Duration Filter -->
    <div class="flex flex-col">
      <label 
        class="text-sm font-medium mb-1"
        :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
      >
        Duration
      </label>
      <select 
        v-model="filters.period" 
        class="rounded px-3 py-2 text-sm focus:ring-1 outline-none"
        :class="isDarkMode 
          ? 'bg-neutral-800 border border-transparent text-gray-100 focus:border-amber-600 focus:ring-amber-500' 
          : 'bg-gray-50 border border-transparent text-gray-900 focus:border-amber-600 focus:ring-amber-600'"
      >
        <option value="all">All</option>
        <option value="today">Today</option>
        <option value="this_week">This Week</option>
        <option value="this_month">This Month</option>
        <option value="last_3_month">Last 3 Months</option>
        <option value="last_6_month">Last 6 Months</option>
        <option value="last_9_month">Last 9 Months</option>
        <option value="this_year">This Year</option>
      </select>
    </div>

    <!-- GBV Filter -->
    <div class="flex flex-col">
      <label 
        class="text-sm font-medium mb-1"
        :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
      >
        GBV
      </label>
      <select 
        v-model="filters.gbv" 
        class="rounded px-3 py-2 text-sm focus:ring-1 outline-none"
        :class="isDarkMode 
          ? 'bg-neutral-800 border border-transparent text-gray-100 focus:border-amber-600 focus:ring-amber-500' 
          : 'bg-gray-50 border border-transparent text-gray-900 focus:border-amber-600 focus:ring-amber-600'"
      >
        <option value="both">Both</option>
        <option value="vac">VAC</option>
        <option value="gbv">GBV</option>
      </select>
    </div>

    <!-- Source Filter -->
    <div class="flex flex-col">
      <label 
        class="text-sm font-medium mb-1"
        :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
      >
        Source
      </label>
      <select 
        v-model="filters.source" 
        class="rounded px-3 py-2 text-sm focus:ring-1 outline-none"
        :class="isDarkMode 
          ? 'bg-neutral-800 border border-transparent text-gray-100 focus:border-amber-600 focus:ring-amber-500' 
          : 'bg-gray-50 border border-transparent text-gray-900 focus:border-amber-600 focus:ring-amber-600'"
      >
        <option value="all">All</option>
        <option value="call">Call</option>
        <option value="sms">SMS</option>
        <option value="email">Email</option>
        <option value="walkin">Walk-in</option>
        <option value="social">Social</option>
      </select>
    </div>

    <!-- Apply and Reset Buttons -->
    <div class="flex items-end gap-2">
      <button
        @click="emitFilters"
        class="text-white px-4 py-2 rounded transition-all duration-200 text-sm shadow-lg flex items-center gap-2 active:scale-95 active:shadow-md"
        :class="isDarkMode 
          ? 'bg-amber-600 hover:bg-amber-700' 
          : 'bg-amber-700 hover:bg-amber-800'"
      >
        <i-mdi-filter class="w-4 h-4" />
        Apply Filters
      </button>
      <button
        @click="resetFilters"
        class="text-white px-4 py-2 rounded transition-all duration-200 text-sm shadow-lg flex items-center gap-2 active:scale-95 active:shadow-md"
        :class="isDarkMode 
          ? 'bg-gray-600 hover:bg-gray-500' 
          : 'bg-gray-500 hover:bg-gray-600'"
      >
        <i-mdi-refresh class="w-4 h-4" />
        Reset
      </button>
    </div>

  </div>
</template>

<script setup>
import { reactive, onMounted, inject } from 'vue'

// Inject theme
const isDarkMode = inject('isDarkMode')

const emit = defineEmits(['update:filters'])

const filters = reactive({
  period: 'all',
  gbv: 'both',
  source: 'all'
})

// Helper function to get unix timestamp
function getUnixTimestamp(date) {
  return Math.floor(date.getTime() / 1000)
}

// Helper function to get start of day
function getStartOfDay(date) {
  const d = new Date(date)
  d.setHours(0, 0, 0, 0)
  return d
}

// Helper function to get end of day
function getEndOfDay(date) {
  const d = new Date(date)
  d.setHours(23, 59, 59, 999)
  return d
}

// Convert period to created_on timestamp range
function getPeriodTimestamp(period) {
  const now = new Date()
  
  switch(period) {
    case 'all':
      return null // No filter
    
    case 'today': {
      const start = getStartOfDay(now)
      const end = getEndOfDay(now)
      return `${getUnixTimestamp(start)};${getUnixTimestamp(end)}`
    }
    
    case 'this_week': {
      const start = getStartOfDay(now)
      start.setDate(now.getDate() - now.getDay()) // Start of week (Sunday)
      const end = getEndOfDay(now)
      return `${getUnixTimestamp(start)};${getUnixTimestamp(end)}`
    }
    
    case 'this_month': {
      const start = new Date(now.getFullYear(), now.getMonth(), 1)
      start.setHours(0, 0, 0, 0)
      const end = getEndOfDay(now)
      return `${getUnixTimestamp(start)};${getUnixTimestamp(end)}`
    }
    
    case 'last_3_month': {
      const start = new Date(now.getFullYear(), now.getMonth() - 3, 1)
      start.setHours(0, 0, 0, 0)
      const end = getEndOfDay(now)
      return `${getUnixTimestamp(start)};${getUnixTimestamp(end)}`
    }
    
    case 'last_6_month': {
      const start = new Date(now.getFullYear(), now.getMonth() - 6, 1)
      start.setHours(0, 0, 0, 0)
      const end = getEndOfDay(now)
      return `${getUnixTimestamp(start)};${getUnixTimestamp(end)}`
    }
    
    case 'last_9_month': {
      const start = new Date(now.getFullYear(), now.getMonth() - 9, 1)
      start.setHours(0, 0, 0, 0)
      const end = getEndOfDay(now)
      return `${getUnixTimestamp(start)};${getUnixTimestamp(end)}`
    }
    
    case 'this_year': {
      const start = new Date(now.getFullYear(), 0, 1)
      start.setHours(0, 0, 0, 0)
      const end = getEndOfDay(now)
      return `${getUnixTimestamp(start)};${getUnixTimestamp(end)}`
    }
    
    default:
      return null
  }
}

// Convert GBV to gbv_related values
function getGbvRelated(gbv) {
  switch(gbv) {
    case 'both':
      return '1,2'
    case 'vac':
      return '1'
    case 'gbv':
      return '2'
    default:
      return '1,2'
  }
}

// Convert source to src values
function getSourceValue(source) {
  switch(source) {
    case 'all':
      return null // No filter
    case 'call':
      return 'call'
    case 'sms':
      return 'sms'
    case 'email':
      return 'email'
    case 'walkin':
      return 'walkin'
    case 'social':
      return 'twitter,facebook,whatsapp' // Adjust based on your actual social sources
    default:
      return null
  }
}

function emitFilters() {
  const backendFilters = {}
  
  // Add created_on if period is not 'all'
  const createdOn = getPeriodTimestamp(filters.period)
  if (createdOn) {
    backendFilters.created_on = createdOn
  }
  
  // Add gbv_related
  backendFilters.gbv_related = getGbvRelated(filters.gbv)
  
  // Add src if source is not 'all'
  const src = getSourceValue(filters.source)
  if (src) {
    backendFilters.src = src
  }
  
  emit('update:filters', backendFilters)
}

function resetFilters() {
  // Reset all filters to default values
  filters.period = 'all'
  filters.gbv = 'both'
  filters.source = 'all'
  
  // Emit the default filters
  emitFilters()
}

// Emit default filters on mount so widgets load immediately
onMounted(() => {
  emitFilters()
})
</script>
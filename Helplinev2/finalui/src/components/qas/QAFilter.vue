<template>
  <div 
    class="w-full rounded-lg p-4 shadow-xl border mb-4"
    :class="isDarkMode 
      ? 'bg-neutral-900 border-transparent' 
      : 'bg-white border-transparent'"
  >
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

      <!-- Call Date From -->
      <div class="flex flex-col">
        <label 
          class="text-sm font-medium mb-1"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          Call Date From
        </label>
        <input 
          type="date" 
          v-model="filters.callDateFrom" 
          class="rounded-lg px-3 py-2 focus:outline-none focus:ring-2"
          :class="isDarkMode 
            ? 'bg-neutral-800 border border-transparent text-gray-100 focus:ring-amber-500' 
            : 'bg-gray-50 border border-transparent text-gray-900 focus:ring-amber-600'"
        />
      </div>

      <!-- Call Date To -->
      <div class="flex flex-col">
        <label 
          class="text-sm font-medium mb-1"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          Call Date To
        </label>
        <input 
          type="date" 
          v-model="filters.callDateTo" 
          class="rounded-lg px-3 py-2 focus:outline-none focus:ring-2"
          :class="isDarkMode 
            ? 'bg-neutral-800 border border-transparent text-gray-100 focus:ring-amber-500' 
            : 'bg-gray-50 border border-transparent text-gray-900 focus:ring-amber-600'"
        />
      </div>

      <!-- User -->
      <div class="flex flex-col">
        <label 
          class="text-sm font-medium mb-1"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          User
        </label>
        <input 
          type="text" 
          v-model="filters.user" 
          placeholder="Enter user name"
          class="rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:border-transparent"
          :class="isDarkMode 
            ? 'bg-neutral-800 border border-transparent text-gray-100 placeholder-gray-500 focus:ring-amber-500' 
            : 'bg-gray-50 border border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'"
        />
      </div>

      <!-- Supervisor -->
      <div class="flex flex-col">
        <label 
          class="text-sm font-medium mb-1"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          Supervisor
        </label>
        <input 
          type="text" 
          v-model="filters.supervisor" 
          placeholder="Enter supervisor name"
          class="rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:border-transparent"
          :class="isDarkMode 
            ? 'bg-neutral-800 border border-transparent text-gray-100 placeholder-gray-500 focus:ring-amber-500' 
            : 'bg-gray-50 border border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'"
        />
      </div>

      <!-- Minimum Total Score -->
      <div class="flex flex-col">
        <label 
          class="text-sm font-medium mb-1"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          Min Total Score (%)
        </label>
        <input 
          type="number" 
          v-model="filters.minScore" 
          placeholder="0-100"
          min="0"
          max="100"
          class="rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:border-transparent"
          :class="isDarkMode 
            ? 'bg-neutral-800 border border-transparent text-gray-100 placeholder-gray-500 focus:ring-amber-500' 
            : 'bg-gray-50 border border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'"
        />
      </div>

      <!-- Created Date From -->
      <div class="flex flex-col">
        <label 
          class="text-sm font-medium mb-1"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          Created Date From
        </label>
        <input 
          type="date" 
          v-model="filters.createdDateFrom" 
          class="rounded-lg px-3 py-2 focus:outline-none focus:ring-2"
          :class="isDarkMode 
            ? 'bg-neutral-800 border border-transparent text-gray-100 focus:ring-amber-500' 
            : 'bg-gray-50 border border-transparent text-gray-900 focus:ring-amber-600'"
        />
      </div>

      <!-- Created Date To -->
      <div class="flex flex-col">
        <label 
          class="text-sm font-medium mb-1"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          Created Date To
        </label>
        <input 
          type="date" 
          v-model="filters.createdDateTo" 
          class="rounded-lg px-3 py-2 focus:outline-none focus:ring-2"
          :class="isDarkMode 
            ? 'bg-neutral-800 border border-transparent text-gray-100 focus:ring-amber-500' 
            : 'bg-gray-50 border border-transparent text-gray-900 focus:ring-amber-600'"
        />
      </div>

    </div>

    <!-- Action Buttons -->
    <div class="flex gap-2 mt-4">
      <button
        @click="applyFilters"
        class="text-white px-6 py-2 rounded-lg transition-all duration-200 font-medium flex items-center gap-2"
        :class="isDarkMode 
          ? 'bg-amber-600 hover:bg-amber-700' 
          : 'bg-amber-700 hover:bg-amber-800'"
      >
        <i-mdi-filter class="w-4 h-4" />
        Apply Filters
      </button>
      
      <button
        @click="resetFilters"
        class="px-6 py-2 rounded-lg transition-all duration-200 font-medium border"
        :class="isDarkMode 
          ? 'bg-gray-700 text-gray-300 border-transparent hover:bg-gray-600' 
          : 'bg-gray-200 text-gray-700 border-transparent hover:bg-gray-300'"
      >
        Reset
      </button>
    </div>
  </div>
</template>

<script setup>
import { reactive, defineEmits, inject } from 'vue'

const emit = defineEmits(['update:filters'])

// Inject theme
const isDarkMode = inject('isDarkMode')

const filters = reactive({
  callDateFrom: '',
  callDateTo: '',
  user: '',
  supervisor: '',
  minScore: '',
  createdDateFrom: '',
  createdDateTo: ''
})

// Helper to get unix timestamp from date string
function getUnixTimestamp(dateString) {
  if (!dateString) return null
  const date = new Date(dateString)
  date.setHours(0, 0, 0, 0)
  return Math.floor(date.getTime() / 1000)
}

// Helper to get end of day timestamp
function getEndOfDayTimestamp(dateString) {
  if (!dateString) return null
  const date = new Date(dateString)
  date.setHours(23, 59, 59, 999)
  return Math.floor(date.getTime() / 1000)
}

function applyFilters() {
  const params = {}

  // Call Date Range - using chan_chan_ts field
  if (filters.callDateFrom || filters.callDateTo) {
    const fromTs = filters.callDateFrom ? getUnixTimestamp(filters.callDateFrom) : 0
    const toTs = filters.callDateTo ? getEndOfDayTimestamp(filters.callDateTo) : Math.floor(Date.now() / 1000)
    params.chan_chan_ts = `${fromTs};${toTs}`
  }

  // User - using chan_user_name field
  if (filters.user) {
    params.chan_user_name = filters.user.trim()
  }

  // Supervisor - using created_by field
  if (filters.supervisor) {
    params.created_by = filters.supervisor.trim()
  }

  // Minimum Total Score - using total_score_p field
  if (filters.minScore) {
    params.total_score_p = filters.minScore
  }

  // Created Date Range - using created_on field
  if (filters.createdDateFrom || filters.createdDateTo) {
    const fromTs = filters.createdDateFrom ? getUnixTimestamp(filters.createdDateFrom) : 0
    const toTs = filters.createdDateTo ? getEndOfDayTimestamp(filters.createdDateTo) : Math.floor(Date.now() / 1000)
    params.created_on = `${fromTs};${toTs}`
  }

  emit('update:filters', params)
}

function resetFilters() {
  filters.callDateFrom = ''
  filters.callDateTo = ''
  filters.user = ''
  filters.supervisor = ''
  filters.minScore = ''
  filters.createdDateFrom = ''
  filters.createdDateTo = ''
  
  emit('update:filters', {})
}
</script>
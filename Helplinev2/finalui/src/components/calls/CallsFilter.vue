<template>
  <div 
    class="w-full rounded-lg p-4 shadow-xl border mb-4"
    :class="isDarkMode 
      ? 'bg-neutral-900 border-transparent' 
      : 'bg-white border-transparent'"
  >
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">

      <!-- Date Range From -->
      <div class="flex flex-col">
        <label 
          class="text-sm font-medium mb-1"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          From Date
        </label>
        <input 
          type="date" 
          v-model="filters.dateFrom" 
          class="rounded px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:border-transparent"
          :class="isDarkMode 
            ? 'bg-neutral-800 border border-transparent text-gray-100 focus:ring-amber-500' 
            : 'bg-gray-50 border border-transparent text-gray-900 focus:ring-amber-600'"
        />
      </div>

      <!-- Date Range To -->
      <div class="flex flex-col">
        <label 
          class="text-sm font-medium mb-1"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          To Date
        </label>
        <input 
          type="date" 
          v-model="filters.dateTo" 
          class="rounded px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:border-transparent"
          :class="isDarkMode 
            ? 'bg-neutral-800 border border-transparent text-gray-100 focus:ring-amber-500' 
            : 'bg-gray-50 border border-transparent text-gray-900 focus:ring-amber-600'"
        />
      </div>

      <!-- Direction -->
      <div class="flex flex-col">
        <label 
          class="text-sm font-medium mb-1"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          Direction
        </label>
        <select 
          v-model="filters.direction" 
          class="rounded px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:border-transparent"
          :class="isDarkMode 
            ? 'bg-neutral-800 border border-transparent text-gray-100 focus:ring-amber-500' 
            : 'bg-gray-50 border border-transparent text-gray-900 focus:ring-amber-600'"
        >
          <option value="">All</option>
          <option value="1">Inbound</option>
          <option value="2">Outbound</option>
        </select>
      </div>

      <!-- Phone Number -->
      <div class="flex flex-col">
        <label 
          class="text-sm font-medium mb-1"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          Phone
        </label>
        <input 
          type="text" 
          v-model="filters.phone" 
          placeholder="Enter phone number"
          class="rounded px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:border-transparent"
          :class="isDarkMode 
            ? 'bg-neutral-800 border border-transparent text-gray-100 placeholder-gray-500 focus:ring-amber-500' 
            : 'bg-gray-50 border border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'"
        />
      </div>

      <!-- Extension -->
      <div class="flex flex-col">
        <label 
          class="text-sm font-medium mb-1"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          Extension
        </label>
        <input 
          type="text" 
          v-model="filters.extension" 
          placeholder="Enter extension"
          class="rounded px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:border-transparent"
          :class="isDarkMode 
            ? 'bg-neutral-800 border border-transparent text-gray-100 placeholder-gray-500 focus:ring-amber-500' 
            : 'bg-gray-50 border border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'"
        />
      </div>

      <!-- Hangup Status -->
      <div class="flex flex-col">
        <label 
          class="text-sm font-medium mb-1"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          Hangup Status
        </label>
        <select 
          v-model="filters.hangupStatus" 
          class="rounded px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:border-transparent"
          :class="isDarkMode 
            ? 'bg-neutral-800 border border-transparent text-gray-100 focus:ring-amber-500' 
            : 'bg-gray-50 border border-transparent text-gray-900 focus:ring-amber-600'"
        >
          <option value="">All</option>
          <option value="answered">Answered</option>
          <option value="abandoned">Abandoned</option>
          <option value="dump">AgentDump</option>
          <option value="missed">Missed</option>
          <option value="ivr">IVR</option>
          <option value="noanswer">Flash</option>
          <option value="busy">Busy</option>
          <option value="networkerror">Network Error</option>
          <option value="voicemail">Voicemail</option>
          <option value="xfer_consult">Consult</option>
          <option value="xfer_noanswer">Transfer No Answer</option>
          <option value="xfer_offline">Transfer Unavailable</option>
          <option value="xfer_ok">Transferred</option>
          <option value="SCHED">Sched</option>
          <option value="Reattempt">Reattempt</option>
        </select>
      </div>

      <!-- Hangup By -->
      <div class="flex flex-col">
        <label 
          class="text-sm font-medium mb-1"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          Hangup By
        </label>
        <select 
          v-model="filters.hangupBy" 
          class="rounded px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:border-transparent"
          :class="isDarkMode 
            ? 'bg-neutral-800 border border-transparent text-gray-100 focus:ring-amber-500' 
            : 'bg-gray-50 border border-transparent text-gray-900 focus:ring-amber-600'"
        >
          <option value="">All</option>
          <option value="phone">Customer</option>
          <option value="usr">Extension</option>
          <option value="ivr">IVR</option>
          <option value="net">Network</option>
        </select>
      </div>

      <!-- QA Score -->
      <div class="flex flex-col">
        <label 
          class="text-sm font-medium mb-1"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          Min QA Score
        </label>
        <input 
          type="number" 
          v-model="filters.qaScore" 
          placeholder="0-100"
          min="0"
          max="100"
          class="rounded px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:border-transparent"
          :class="isDarkMode 
            ? 'bg-neutral-800 border border-transparent text-gray-100 placeholder-gray-500 focus:ring-amber-500' 
            : 'bg-gray-50 border border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'"
        />
      </div>

    </div>

    <!-- Action Buttons -->
    <div class="flex gap-2 mt-4">
      <button
        @click="applyFilters"
        class="text-white px-6 py-2 rounded-lg transition-all duration-200 font-medium shadow-lg flex items-center gap-2 active:scale-95"
        :class="isDarkMode 
          ? 'bg-amber-600 hover:bg-amber-700' 
          : 'bg-amber-700 hover:bg-amber-800'"
      >
        <i-mdi-filter class="w-4 h-4" />
        Apply Filters
      </button>
      
      <button
        @click="resetFilters"
        class="px-6 py-2 rounded-lg transition-all duration-200 font-medium border flex items-center gap-2"
        :class="isDarkMode 
          ? 'bg-gray-700 text-gray-300 border-transparent hover:bg-gray-600' 
          : 'bg-gray-100 text-gray-700 border-transparent hover:bg-gray-200'"
      >
        <i-mdi-refresh class="w-4 h-4" />
        Reset
      </button>
    </div>
  </div>
</template>

<script setup>
import { reactive, defineEmits, inject } from 'vue'

// Inject theme
const isDarkMode = inject('isDarkMode')

const emit = defineEmits(['update:filters'])

const filters = reactive({
  dateFrom: '',
  dateTo: '',
  direction: '',
  phone: '',
  extension: '',
  hangupStatus: '',
  hangupBy: '',
  qaScore: ''
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

  // Date range - using chan_ts field
  if (filters.dateFrom || filters.dateTo) {
    const fromTs = filters.dateFrom ? getUnixTimestamp(filters.dateFrom) : 0
    const toTs = filters.dateTo ? getEndOfDayTimestamp(filters.dateTo) : Math.floor(Date.now() / 1000)
    params.chan_ts = `${fromTs};${toTs}`
  }

  // Direction - using vector field
  if (filters.direction) {
    params.vector = filters.direction
  }

  // Phone - using phone field
  if (filters.phone) {
    params.phone = filters.phone.trim()
  }

  // Extension - using usr field
  if (filters.extension) {
    params.usr = filters.extension.trim()
  }

  // Hangup Status - using hangup_status field (backend keys)
  if (filters.hangupStatus) {
    params.hangup_status = filters.hangupStatus
  }

  // Hangup By - using hangup_reason field (backend keys)
  if (filters.hangupBy) {
    params.hangup_reason = filters.hangupBy
  }

  // QA Score - using qa_score field (minimum score)
  if (filters.qaScore) {
    params.qa_score = filters.qaScore
  }

  emit('update:filters', params)
}

function resetFilters() {
  filters.dateFrom = ''
  filters.dateTo = ''
  filters.direction = ''
  filters.phone = ''
  filters.extension = ''
  filters.hangupStatus = ''
  filters.hangupBy = ''
  filters.qaScore = ''
  
  emit('update:filters', {})
}
</script>
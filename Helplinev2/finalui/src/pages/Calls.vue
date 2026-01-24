<template>
  <div class="flex flex-col h-full bg-gray-50 dark:bg-black p-4 gap-4">
    <!-- Header -->
    <div class="flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-2">Call Management</h1>
        <p class="text-gray-500 text-sm">Monitor and manage voice interactions.</p>
      </div>

      <!-- Action Buttons -->
      <div class="flex gap-2">
        <!-- Add any global actions here -->
      </div>
    </div>

    <!-- Filters -->
     <CallsFilter 
      :current-filters="currentFilters"
      :active-view="activeView"
      @filter="applyFilters" 
    />

    <!-- Main Content -->
    <div class="flex-1 flex flex-col gap-4 min-h-0">
      <!-- View Toggles and Refresh -->
      <div class="flex flex-wrap items-center justify-between gap-4">
        <!-- View Toggle Buttons -->
        <div class="flex gap-3">
          <button @click="activeView = 'timeline'" :class="getViewButtonClass(activeView === 'timeline')">
            <i-mdi-timeline-text-outline class="w-5 h-5" />
            Timeline
          </button>

          <button @click="activeView = 'table'" :class="getViewButtonClass(activeView === 'table')">
            <i-mdi-table class="w-5 h-5" />
            Table
          </button>

          <button @click="activeView = 'sip'" :class="getViewButtonClass(activeView === 'sip')">
            <i-mdi-phone-settings class="w-5 h-5" />
            SIP Agent
          </button>

          <button
            @click="refreshCalls"
            :disabled="callsStore.loading"
            :class="[
              'px-5 py-2.5 rounded-xl font-medium transition-all duration-200 flex items-center gap-2 text-sm border disabled:opacity-50 disabled:cursor-not-allowed',
              isDarkMode
                ? 'bg-black text-gray-300 border-transparent hover:border-green-500 hover:text-green-400'
                : 'bg-white text-gray-700 border-transparent hover:border-green-600 hover:text-green-600'
            ]"
          >
            <i-mdi-refresh class="w-5 h-5" />
            Refresh
          </button>

          <button v-if="authStore.canExport" @click="handleDownload"
            :disabled="callsStore.loading || callsStore.calls.length === 0" :class="[
              'px-5 py-2.5 rounded-xl font-medium transition-all duration-200 flex items-center gap-2 text-sm border disabled:opacity-50 disabled:cursor-not-allowed',
              isDarkMode
                ? 'bg-black text-gray-300 border-transparent hover:border-amber-500 hover:text-amber-400'
                : 'bg-white text-gray-700 border-transparent hover:border-amber-600 hover:text-amber-700'
            ]">
            <i-mdi-file-excel-outline class="w-5 h-5 text-green-500" />
            Download
          </button>
        </div>
      </div>

      <!-- Timeline view -->
      <div v-if="activeView === 'timeline'" class="flex-1 min-h-0 overflow-hidden flex flex-col">
        <div class="flex-1 overflow-y-auto pr-2 custom-scrollbar">
           <CallsTimeline :grouped-calls="groupedCalls" :selected-call-id="selectedCallId"
            @select-call="selectCall" @create-qa="handleCreateQA" />
        </div>
      </div>

      <!-- Table view -->
      <div v-if="activeView === 'table'">
        <CallsTable :calls="callsStore.calls" :calls-store="callsStore" :selected-call-id="selectedCallId"
          @select-call="selectCall" @create-qa="handleCreateQA" />
      </div>

      <!-- SIP Agent view -->
      <div v-if="activeView === 'sip'">
        <SipAgentView />
      </div>

      <!-- Pagination Controls (not shown for SIP view) -->
      <Pagination v-if="activeView !== 'sip'" :paginationInfo="callsStore.paginationInfo"
        :hasNextPage="callsStore.hasNextPage" :hasPrevPage="callsStore.hasPrevPage" :loading="callsStore.loading"
        :pageSize="selectedPageSize" @prev="goToPrevPage" @next="goToNextPage" @goToPage="goToPage"
        @changePageSize="changePageSize" />
    </div>

    <!-- QA Drawer -->
    <QaFormDrawer :is-open="qaForm.isOpen.value" :current-call="qaForm.currentCall.value" :is-dark-mode="isDarkMode"
      :scores="qaForm.scores" :comments="qaForm.comments" v-model:generalFeedback="qaForm.generalFeedback.value"
      :category-scores="qaForm.categoryScores.value" :total-score="qaForm.totalScore.value"
      :total-percentage="qaForm.totalPercentage.value" :is-loading="qaForm.isLoading.value" @close="qaForm.closeForm"
      @submit="qaForm.submitQa" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject, watch } from "vue"
import { useRouter } from "vue-router"
import { toast } from 'vue-sonner'
import CallsTimeline from "@/components/calls/CallsTimeline.vue"
import CallsTable from "@/components/calls/CallsTable.vue"
import CallsFilter from "@/components/calls/CallsFilter.vue"
import SipAgentView from "@/components/calls/SipAgentView.vue"
import Pagination from "@/components/base/Pagination.vue"
import { useCallStore } from "@/stores/calls"
import { useSearchStore } from "@/stores/search"
import { useAuthStore } from "@/stores/auth"
import { useCallDownload } from "@/composables/useCallDownload"
import { useQaForm } from "@/modules/qa/useQaForm"
import QaFormDrawer from "@/modules/qa/QaFormDrawer.vue"

// Inject theme
const isDarkMode = inject('isDarkMode')

const router = useRouter()
const callsStore = useCallStore()
const searchStore = useSearchStore()
const authStore = useAuthStore()
const activeView = ref("timeline")
const selectedCallId = ref(null)
const currentFilters = ref({})
const selectedPageSize = ref(20)
const { triggerDownload } = useCallDownload()

// Debounce handle for global search
let searchDebounce = null

// Watch for global search query changes
watch(() => searchStore.query, (newQuery) => {
  clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => {
    // Merge search query with existing filters
    const searchParams = { ...currentFilters.value }
    if (newQuery) {
      searchParams.q = newQuery
    } else {
      delete searchParams.q
    }
    applyFilters(searchParams)
  }, 500)
})

// Dynamic button class based on active state
const getViewButtonClass = (isActive) => {
  const baseClasses = 'px-5 py-2.5 rounded-xl font-medium transition-all duration-200 flex items-center gap-2 text-sm'

  if (isActive) {
    return isDarkMode.value
      ? `${baseClasses} bg-amber-600 text-white shadow-lg shadow-blue-900/50`
      : `${baseClasses} bg-amber-700 text-white shadow-lg shadow-amber-900/30`
  } else {
    return isDarkMode.value
      ? `${baseClasses} bg-black text-gray-300 border border-transparent hover:border-amber-600 hover:text-amber-500`
      : `${baseClasses} bg-white text-gray-700 border border-transparent hover:border-amber-600 hover:text-amber-700`
  }
}

// Fetch calls on mount
onMounted(async () => {
  try {
    console.log("Fetching calls...")
    // If there is an existing search query, apply it
    const params = { _o: 0, _c: selectedPageSize.value }
    if (searchStore.query) {
      params.q = searchStore.query
    }
    await callsStore.listCalls(params)
    console.log("Calls fetched:", callsStore.calls)
  } catch (err) {
    console.error("Error fetching calls:", err)
    toast.error('Failed to load calls. Please try again.')
  }
})

// Apply filters and fetch calls (resets to first page)
async function applyFilters(filters) {
  currentFilters.value = filters
  try {
    console.log("Applying filters:", filters)
    // Reset pagination when filters change
    callsStore.resetPagination()
    await callsStore.listCalls({ ...filters, _o: 0, _c: selectedPageSize.value })

    // Auto-select if a single record is found via direct search
    if (filters.q && callsStore.calls.length === 1) {
      const call = callsStore.calls[0]
      const idIndex = callsStore.calls_k?.uniqueid?.[0]
      if (idIndex !== undefined) {
        selectCall(call[idIndex])
        toast.success(`Found and selected call: ${call[idIndex]}`)
      }
    }
  } catch (err) {
    console.error("Error fetching filtered calls:", err)
    toast.error('Failed to apply filters. Please try again.')
  }
}

// Refresh calls with current filters (maintains current page)
async function refreshCalls() {
  try {
    console.log("Refreshing calls...")
    const params = {
      ...currentFilters.value,
      _o: callsStore.pagination.offset,
      _c: callsStore.pagination.limit
    }
    if (searchStore.query) {
      params.q = searchStore.query
    }
    await callsStore.listCalls(params)
    toast.success('Calls refreshed successfully!')
  } catch (err) {
    console.error("Error refreshing calls:", err)
    toast.error('Failed to refresh calls. Please try again.')
  }
}

// Handle XLSX download
function handleDownload() {
  const params = { ...currentFilters.value }
  if (searchStore.query) {
    params.q = searchStore.query
  }

  // Trigger the legacy download
  triggerDownload(params)
}

// Handle create QA (Legacy router method replaced by Drawer)
function handleCreateQA(uniqueid) {
  if (!authStore.isSupervisor && !authStore.isAdministrator) {
    toast.error("You do not have permission to perform QA.")
    return
  }

  // Find call object
  const call = callsStore.getCallById(uniqueid)
  if (!call) {
    toast.error("Call details not found.")
    return
  }

  // Map array to object with safer fallback access
  const keys = callsStore.calls_k || {}
  const getVal = (keyName) => {
    const idx = keys[keyName]?.[0]
    return idx !== undefined && call[idx] !== undefined ? call[idx] : null
  }

  const formatDur = (val) => {
    if (!val || val === '0') return '0.00'
    const num = parseFloat(val)
    return (num / 100).toFixed(2)
  }

  const callObj = {
    uniqueid: getVal('uniqueid') || getVal('chan_uniqueid') || uniqueid,
    extension: getVal('agent_ext') || getVal('extension') || 'Unknown',
    phone: getVal('callerid') || getVal('phone') || 'Unknown',
    duration: formatDur(getVal('talk_time') || getVal('duration')),
    created: getVal('dth') || getVal('created') || 0,
    recording_url: getVal('recordingfile') || getVal('recording_url') || null
  }

  console.log('Opening QA Form for:', callObj) // Debug log
  qaForm.openForm(callObj)
}

const qaForm = useQaForm()

// Parent-level select handler (child components emit callId)
function selectCall(callId) {
  selectedCallId.value = callId
}

// Group calls by date (uses your store's calls and calls_k indexes)
const groupedCalls = computed(() => {
  const groups = {}
  if (!callsStore.calls || !Array.isArray(callsStore.calls)) return groups

  const tsIndex = callsStore.calls_k?.dth?.[0]
  if (tsIndex === undefined) return groups

  callsStore.calls.forEach((call) => {
    const ts = call[tsIndex]
    const dateLabel = ts ? new Date(ts * 1000).toLocaleDateString() : "Unknown"

    if (!groups[dateLabel]) groups[dateLabel] = []
    groups[dateLabel].push(call)
  })

  // Sort groups by newest date first
  const sorted = Object.keys(groups)
    .sort((a, b) => new Date(b) - new Date(a))
    .reduce((acc, k) => {
      acc[k] = groups[k]
      return acc
    }, {})

  return sorted
})

// Pagination handlers
async function goToNextPage() {
  try {
    const params = { ...currentFilters.value }
    if (searchStore.query) params.q = searchStore.query
    await callsStore.nextPage(params)
  } catch (err) {
    console.error("Error going to next page:", err)
    toast.error('Failed to load next page.')
  }
}

async function goToPrevPage() {
  try {
    const params = { ...currentFilters.value }
    if (searchStore.query) params.q = searchStore.query
    await callsStore.prevPage(params)
  } catch (err) {
    console.error("Error going to previous page:", err)
    toast.error('Failed to load previous page.')
  }
}

async function goToPage(page) {
  if (page === '...') return
  try {
    const params = { ...currentFilters.value }
    if (searchStore.query) params.q = searchStore.query
    await callsStore.goToPage(page, params)
  } catch (err) {
    console.error("Error going to page:", err)
    toast.error('Failed to load page.')
  }
}

async function changePageSize(size) {
  selectedPageSize.value = size
  try {
    const params = { ...currentFilters.value }
    if (searchStore.query) params.q = searchStore.query
    await callsStore.setPageSize(size, params)
  } catch (err) {
    console.error("Error changing page size:", err)
    toast.error('Failed to change page size.')
  }
}
</script>
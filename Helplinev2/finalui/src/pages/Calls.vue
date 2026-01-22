<template>
  <div 
    class="space-y-6"
  >

    <!-- Filters -->
    <CallsFilter @update:filters="applyFilters" />
    <!-- Loading State -->
    <div 
      v-if="callsStore.loading" 
      class="flex justify-center items-center py-12 rounded-xl shadow-xl border"
      :class="isDarkMode 
        ? 'bg-black border-transparent' 
        : 'bg-white border-transparent'"
    >
      <div 
        :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
      >
        Loading calls...
      </div>
    </div>

    <!-- Content when loaded -->
    <div v-else>
      <!-- View Toggle Buttons and Stats Row -->
      <div class="flex justify-between items-center mb-6">
        <!-- Total Count with Pagination Info -->
        <div
          class="flex items-center gap-2"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          <i-mdi-phone-outline
            class="w-5 h-5"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
          />
          <span class="text-sm">
            Showing {{ callsStore.paginationInfo.rangeStart }} - {{ callsStore.paginationInfo.rangeEnd }} of
          </span>
          <span
            class="text-lg font-bold"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
          >
            {{ callsStore.paginationInfo.total }}
          </span>
          <span class="text-sm">calls</span>
        </div>

        <!-- View Toggle Buttons -->
        <div class="flex gap-3">
          <button
            @click="activeView = 'timeline'"
            :class="getViewButtonClass(activeView === 'timeline')"
          >
            <i-mdi-timeline-text-outline class="w-5 h-5" />
            Timeline
          </button>

          <button
            @click="activeView = 'table'"
            :class="getViewButtonClass(activeView === 'table')"
          >
            <i-mdi-table class="w-5 h-5" />
            Table
          </button>

          <button
            @click="activeView = 'sip'"
            :class="getViewButtonClass(activeView === 'sip')"
          >
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
        </div>
      </div>

      <!-- Timeline view -->
      <div v-if="activeView === 'timeline'">
        <Timeline
          :grouped-calls="groupedCalls"
          :calls-store="callsStore"
          @select-call="selectCall"
          @create-qa="handleCreateQA"
        />
      </div>

      <!-- Table view -->
      <div v-if="activeView === 'table'">
        <Table
          :calls="callsStore.calls"
          :calls-store="callsStore"
          :selected-call-id="selectedCallId"
          @select-call="selectCall"
          @create-qa="handleCreateQA"
        />
      </div>

      <!-- SIP Agent view -->
      <div v-if="activeView === 'sip'">
        <SipAgentView />
      </div>

      <!-- Pagination Controls (not shown for SIP view) -->
      <Pagination
        v-if="activeView !== 'sip'"
        :paginationInfo="callsStore.paginationInfo"
        :hasNextPage="callsStore.hasNextPage"
        :hasPrevPage="callsStore.hasPrevPage"
        :loading="callsStore.loading"
        :pageSize="selectedPageSize"
        @prev="goToPrevPage"
        @next="goToNextPage"
        @goToPage="goToPage"
        @changePageSize="changePageSize"
      />
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject, watch } from "vue"
import { useRouter } from "vue-router"
import { toast } from 'vue-sonner'
import Timeline from "@/components/calls/Timeline.vue"
import Table from "@/components/calls/Table.vue"
import CallsFilter from "@/components/calls/CallsFilter.vue"
import SipAgentView from "@/components/calls/SipAgentView.vue"
import Pagination from "@/components/base/Pagination.vue"
import { useCallStore } from "@/stores/calls"
import { useSearchStore } from "@/stores/search"

// Inject theme
const isDarkMode = inject('isDarkMode')

const router = useRouter()
const callsStore = useCallStore()
const searchStore = useSearchStore()
const activeView = ref("timeline")
const selectedCallId = ref(null)
const currentFilters = ref({})
const selectedPageSize = ref(20)

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

// Handle create QA
function handleCreateQA(uniqueid) {
  router.push({
    name: 'QaCreation',
    query: { callId: uniqueid }
  })
}

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
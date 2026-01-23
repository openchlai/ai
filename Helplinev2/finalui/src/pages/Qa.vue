<template>
  <div 
    class="space-y-6"
  >

    <!-- Filters -->
    <QAFilter @update:filters="applyFilters" />

    <!-- Loading State -->
    <div 
      v-if="qaStore.loading" 
      class="flex justify-center items-center py-12 rounded-lg shadow-xl border"
      :class="isDarkMode 
        ? 'bg-black border-transparent' 
        : 'bg-white border-transparent'"
    >
      <div 
        :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
      >
        Loading QA records...
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
          <i-mdi-clipboard-check
            class="w-5 h-5"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
          />
          <span class="text-sm">
            Showing {{ qaStore.paginationInfo.rangeStart }} - {{ qaStore.paginationInfo.rangeEnd }} of
          </span>
          <span
            class="text-lg font-bold"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
          >
            {{ qaStore.paginationInfo.total }}
          </span>
          <span class="text-sm">QA records</span>
        </div>

        <!-- View Toggle Buttons -->
        <div class="flex gap-3">
          <button
            @click="currentView = 'timeline'"
            :class="getViewButtonClass(currentView === 'timeline')"
          >
            <i-mdi-timeline-text-outline class="w-5 h-5" />
            Timeline
          </button>

          <button
            @click="currentView = 'table'"
            :class="getViewButtonClass(currentView === 'table')"
          >
            <i-mdi-table class="w-5 h-5" />
            Table
          </button>

          <button
            @click="refreshQA"
            :disabled="qaStore.loading"
            class="px-5 py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 text-sm border disabled:opacity-50 disabled:cursor-not-allowed"
            :class="isDarkMode 
              ? 'bg-black text-gray-300 border-transparent hover:border-green-500 hover:text-green-400' 
              : 'bg-white text-gray-700 border-transparent hover:border-green-600 hover:text-green-700'"
          >
            <i-mdi-refresh class="w-5 h-5" />
            Refresh
          </button>
        </div>
      </div>

      <!-- Timeline view -->
      <div v-if="currentView === 'timeline'">
        <QATimeline
          :qas="qaStore.qas"
          :qas_k="qaStore.qas_k"
        />
      </div>

      <!-- Table view -->
      <div v-if="currentView === 'table'">
        <Table
          :qas="qaStore.qas"
          :qas_k="qaStore.qas_k"
        />
      </div>

      <!-- Pagination Controls -->
      <Pagination
        :paginationInfo="qaStore.paginationInfo"
        :hasNextPage="qaStore.hasNextPage"
        :hasPrevPage="qaStore.hasPrevPage"
        :loading="qaStore.loading"
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
import { ref, onMounted, inject } from 'vue'
import { toast } from 'vue-sonner'
import { useQAStore } from '@/stores/qas'
import Table from '@/components/qas/Table.vue'
import QATimeline from '@/components/qas/QATimeline.vue'
import QAFilter from '@/components/qas/QAFilter.vue'
import Pagination from '@/components/base/Pagination.vue'

const qaStore = useQAStore()
const currentView = ref('timeline')
const currentFilters = ref({})
const selectedPageSize = ref(20)

// Inject theme
const isDarkMode = inject('isDarkMode')

// Dynamic button class for view toggle
const getViewButtonClass = (isActive) => {
  const baseClasses = 'px-5 py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 text-sm'
  
  if (isActive) {
    return isDarkMode.value
      ? `${baseClasses} bg-amber-600 text-white shadow-lg shadow-amber-900/50`
      : `${baseClasses} bg-amber-700 text-white shadow-lg shadow-amber-900/30`
  } else {
    return isDarkMode.value
      ? `${baseClasses} bg-black text-gray-300 border border-transparent hover:border-amber-600 hover:text-amber-500`
      : `${baseClasses} bg-white text-gray-700 border border-transparent hover:border-amber-600 hover:text-amber-700`
  }
}

onMounted(async () => {
  try {
    console.log('Fetching QA records...')
    await qaStore.listQA({ _o: 0, _c: selectedPageSize.value })
    console.log('QA records fetched:', qaStore.qas)
    console.log('Pagination info:', qaStore.paginationInfo)
  } catch (err) {
    console.error('Failed to fetch QA records:', err)
    toast.error('Failed to load QA records. Please try again.')
  }
})

// Apply filters and fetch QA records (resets to first page)
async function applyFilters(filters) {
  currentFilters.value = filters
  try {
    console.log('Applying filters:', filters)
    qaStore.resetPagination()
    await qaStore.listQA({ ...filters, _o: 0, _c: selectedPageSize.value })
    console.log('Filtered QA records fetched:', qaStore.qas)
  } catch (err) {
    console.error('Error fetching filtered QA records:', err)
    toast.error('Failed to apply filters. Please try again.')
  }
}

// Refresh QA with current filters (maintains current page)
async function refreshQA() {
  try {
    console.log('Refreshing QA records...')
    await qaStore.listQA({
      ...currentFilters.value,
      _o: qaStore.pagination.offset,
      _c: qaStore.pagination.limit
    })
    console.log('QA records refreshed')
    toast.success('QA records refreshed successfully!')
  } catch (err) {
    console.error('Error refreshing QA records:', err)
    toast.error('Failed to refresh QA records. Please try again.')
  }
}

// Pagination handlers
async function goToNextPage() {
  try {
    await qaStore.nextPage(currentFilters.value)
  } catch (err) {
    console.error('Error going to next page:', err)
    toast.error('Failed to load next page.')
  }
}

async function goToPrevPage() {
  try {
    await qaStore.prevPage(currentFilters.value)
  } catch (err) {
    console.error('Error going to previous page:', err)
    toast.error('Failed to load previous page.')
  }
}

async function goToPage(page) {
  if (page === '...') return
  try {
    await qaStore.goToPage(page, currentFilters.value)
  } catch (err) {
    console.error('Error going to page:', err)
    toast.error('Failed to load page.')
  }
}

async function changePageSize(size) {
  selectedPageSize.value = size
  try {
    await qaStore.setPageSize(size, currentFilters.value)
  } catch (err) {
    console.error('Error changing page size:', err)
    toast.error('Failed to change page size.')
  }
}
</script>
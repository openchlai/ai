<template>
  <div 
    class="space-y-6"
  >

    <!-- Filters -->
    <ActivitiesFilter @update:filters="applyFilters" />

    <!-- Loading State -->
    <div 
      v-if="activitiesStore.loading" 
      class="flex justify-center items-center py-12 rounded-lg shadow-xl border"
      :class="isDarkMode 
        ? 'bg-black border-transparent' 
        : 'bg-white border-transparent'"
    >
      <div 
        :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
      >
        Loading activities...
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
          <i-mdi-bell
            class="w-5 h-5"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
          />
          <span class="text-sm">
            Showing {{ activitiesStore.paginationInfo.rangeStart }} - {{ activitiesStore.paginationInfo.rangeEnd }} of
          </span>
          <span
            class="text-lg font-bold"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
          >
            {{ activitiesStore.paginationInfo.total }}
          </span>
          <span class="text-sm">activities</span>
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
            @click="refreshActivities"
            :disabled="activitiesStore.loading"
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
        <ActivitiesTimeline
          :activities="activitiesStore.activitiesAsObjects"
        />
      </div>

      <!-- Table view -->
      <div v-if="currentView === 'table'">
        <ActivitiesTable
          :activities="activitiesStore.activitiesAsObjects"
        />
      </div>

      <!-- Pagination Controls -->
      <Pagination
        :paginationInfo="activitiesStore.paginationInfo"
        :hasNextPage="activitiesStore.hasNextPage"
        :hasPrevPage="activitiesStore.hasPrevPage"
        :loading="activitiesStore.loading"
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
import { useActivitiesStore } from '@/stores/activities'
import ActivitiesFilter from '@/components/activities/ActivitiesFilter.vue'
import ActivitiesTable from '@/components/activities/ActivitiesTable.vue'
import ActivitiesTimeline from '@/components/activities/ActivitiesTimeline.vue'
import Pagination from '@/components/base/Pagination.vue'

const activitiesStore = useActivitiesStore()
const currentView = ref('timeline')
const currentFilters = ref({ action: 'notify' })
const selectedPageSize = ref(20)

// Inject theme
const isDarkMode = inject('isDarkMode')

// Dynamic button class for view toggle
const getViewButtonClass = (isActive) => {
  const baseClasses = 'px-5 py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 text-sm'
  
  if (isActive) {
    return isDarkMode.value
      ? `${baseClasses} bg-amber-600 text-white shadow-lg shadow-blue-900/50`
      : `${baseClasses} bg-amber-700 text-white shadow-lg shadow-amber-900/30`
  } else {
    return isDarkMode.value
      ? `${baseClasses} bg-black text-gray-300 border border-transparent hover:border-amber-500 hover:text-amber-500`
      : `${baseClasses} bg-white text-gray-700 border border-transparent hover:border-amber-600 hover:text-amber-700`
  }
}

onMounted(async () => {
  try {
    console.log('Fetching activities...')
    await activitiesStore.listActivities({ ...currentFilters.value, _o: 0, _c: selectedPageSize.value })
    console.log('Activities fetched:', activitiesStore.activitiesAsObjects)
    console.log('Pagination info:', activitiesStore.paginationInfo)
  } catch (err) {
    console.error('Failed to fetch activities:', err)
    toast.error('Failed to load activities. Please try again.')
  }
})

// Apply filters and fetch activities (resets to first page)
async function applyFilters(filters) {
  currentFilters.value = filters
  try {
    console.log('Applying filters:', filters)
    activitiesStore.resetPagination()
    await activitiesStore.listActivities({ ...filters, _o: 0, _c: selectedPageSize.value })
    console.log('Filtered activities fetched:', activitiesStore.activitiesAsObjects)
  } catch (err) {
    console.error('Error fetching filtered activities:', err)
    toast.error('Failed to apply filters. Please try again.')
  }
}

// Refresh activities with current filters (maintains current page)
async function refreshActivities() {
  try {
    console.log('Refreshing activities...')
    await activitiesStore.listActivities({
      ...currentFilters.value,
      _o: activitiesStore.pagination.offset,
      _c: activitiesStore.pagination.limit
    })
    console.log('Activities refreshed')
    toast.success('Activities refreshed successfully!')
  } catch (err) {
    console.error('Error refreshing activities:', err)
    toast.error('Failed to refresh activities. Please try again.')
  }
}

// Pagination handlers
async function goToNextPage() {
  try {
    await activitiesStore.nextPage(currentFilters.value)
  } catch (err) {
    console.error('Error going to next page:', err)
    toast.error('Failed to load next page.')
  }
}

async function goToPrevPage() {
  try {
    await activitiesStore.prevPage(currentFilters.value)
  } catch (err) {
    console.error('Error going to previous page:', err)
    toast.error('Failed to load previous page.')
  }
}

async function goToPage(page) {
  if (page === '...') return
  try {
    await activitiesStore.goToPage(page, currentFilters.value)
  } catch (err) {
    console.error('Error going to page:', err)
    toast.error('Failed to load page.')
  }
}

async function changePageSize(size) {
  selectedPageSize.value = size
  try {
    await activitiesStore.setPageSize(size, currentFilters.value)
  } catch (err) {
    console.error('Error changing page size:', err)
    toast.error('Failed to change page size.')
  }
}
</script>
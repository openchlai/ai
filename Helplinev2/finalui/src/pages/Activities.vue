<template>
  <div 
    class="p-6 space-y-6 min-h-screen"
    :class="isDarkMode ? 'bg-black' : 'bg-gray-50'"
  >
    <!-- Page Header -->
    <div class="mb-6">
      <h1 
        class="text-3xl font-bold flex items-center gap-3"
        :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
      >
        <i-mdi-clipboard-list-outline 
          class="w-8 h-8"
          :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
        />
        Notification Activities
      </h1>
      <p 
        class="mt-2"
        :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
      >
        Track and manage all notification activities and case updates
      </p>
    </div>

    <!-- Filters -->
    <ActivitiesFilter @update:filters="applyFilters" />

    <!-- Loading State -->
    <div 
      v-if="activitiesStore.loading" 
      class="flex justify-center items-center py-12 rounded-lg shadow-xl border"
      :class="isDarkMode 
        ? 'bg-gray-800 border-transparent' 
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
        <!-- Total Count -->
        <div 
          class="flex items-center gap-2"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          <i-mdi-bell 
            class="w-5 h-5"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
          />
          <span class="text-sm">Total Activities:</span>
          <span 
            class="text-lg font-bold"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
          >
            {{ activitiesStore.activityCount }}
          </span>
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
              ? 'bg-gray-800 text-gray-300 border-transparent hover:border-green-500 hover:text-green-400' 
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

const activitiesStore = useActivitiesStore()
const currentView = ref('timeline')
const currentFilters = ref({ action: 'notify' })

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
      ? `${baseClasses} bg-gray-800 text-gray-300 border border-transparent hover:border-amber-500 hover:text-amber-500`
      : `${baseClasses} bg-white text-gray-700 border border-transparent hover:border-amber-600 hover:text-amber-700`
  }
}

onMounted(async () => {
  try {
    console.log('Fetching activities...')
    await activitiesStore.listActivities(currentFilters.value)
    console.log('Activities fetched:', activitiesStore.activitiesAsObjects)
  } catch (err) {
    console.error('Failed to fetch activities:', err)
    toast.error('Failed to load activities. Please try again.')
  }
})

// Apply filters and fetch activities
async function applyFilters(filters) {
  currentFilters.value = filters
  try {
    console.log('Applying filters:', filters)
    await activitiesStore.listActivities(filters)
    console.log('Filtered activities fetched:', activitiesStore.activitiesAsObjects)
  } catch (err) {
    console.error('Error fetching filtered activities:', err)
    toast.error('Failed to apply filters. Please try again.')
  }
}

// Refresh activities with current filters
async function refreshActivities() {
  try {
    console.log('Refreshing activities...')
    await activitiesStore.listActivities(currentFilters.value)
    console.log('Activities refreshed')
    toast.success('Activities refreshed successfully!')
  } catch (err) {
    console.error('Error refreshing activities:', err)
    toast.error('Failed to refresh activities. Please try again.')
  }
}
</script>
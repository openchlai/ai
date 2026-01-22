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
        <i-mdi-check-decagram 
          class="w-8 h-8"
          :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
        />
        QA Results
      </h1>
      <p 
        class="mt-2"
        :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
      >
        Review and analyze quality assurance evaluations and call performance
      </p>
    </div>

    <!-- Filters -->
    <QAFilter @update:filters="applyFilters" />

    <!-- Loading State -->
    <div 
      v-if="qaStore.loading" 
      class="flex justify-center items-center py-12 rounded-lg shadow-xl border"
      :class="isDarkMode 
        ? 'bg-gray-800 border-transparent' 
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
        <!-- Total Count -->
        <div 
          class="flex items-center gap-2"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          <i-mdi-clipboard-check 
            class="w-5 h-5"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
          />
          <span class="text-sm">Total QA Records:</span>
          <span 
            class="text-lg font-bold"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
          >
            {{ qaStore.qaCount }}
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
            @click="refreshQA"
            :disabled="qaStore.loading"
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

const qaStore = useQAStore()
const currentView = ref('timeline')
const currentFilters = ref({})

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
      ? `${baseClasses} bg-gray-800 text-gray-300 border border-transparent hover:border-amber-600 hover:text-amber-500`
      : `${baseClasses} bg-white text-gray-700 border border-transparent hover:border-amber-600 hover:text-amber-700`
  }
}

onMounted(async () => {
  try {
    console.log('Fetching QA records...')
    await qaStore.listQA()
    console.log('QA records fetched:', qaStore.qas)
  } catch (err) {
    console.error('Failed to fetch QA records:', err)
    toast.error('Failed to load QA records. Please try again.')
  }
})

// Apply filters and fetch QA records
async function applyFilters(filters) {
  currentFilters.value = filters
  try {
    console.log('Applying filters:', filters)
    await qaStore.listQA(filters)
    console.log('Filtered QA records fetched:', qaStore.qas)
  } catch (err) {
    console.error('Error fetching filtered QA records:', err)
    toast.error('Failed to apply filters. Please try again.')
  }
}

// Refresh QA with current filters
async function refreshQA() {
  try {
    console.log('Refreshing QA records...')
    await qaStore.listQA(currentFilters.value)
    console.log('QA records refreshed')
    toast.success('QA records refreshed successfully!')
  } catch (err) {
    console.error('Error refreshing QA records:', err)
    toast.error('Failed to refresh QA records. Please try again.')
  }
}
</script>
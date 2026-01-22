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
        <i-mdi-view-dashboard-outline 
          class="w-8 h-8"
          :class="isDarkMode ? 'text-amber-500' : 'text-amber-600'"
        />
        Dashboard
      </h1>
      <p 
        class="mt-2"
        :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
      >
        Overview of case analytics and key performance metrics
      </p>
    </div>

    <!-- 🔥 Shared Filters Bar -->
    <CasesFilters @update:filters="applyFilters" />

    <!-- Grid for the analytics blocks -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Case Categories -->
      <div 
        class="shadow-xl rounded-lg p-4 border"
        :class="isDarkMode 
          ? 'bg-neutral-900 border-transparent' 
          : 'bg-white border-transparent'"
      >
        <CaseCategories :filters="filters" />
      </div>

      <!-- Case Locations -->
      <div 
        class="shadow-xl rounded-lg p-4 border"
        :class="isDarkMode 
          ? 'bg-neutral-900 border-transparent' 
          : 'bg-white border-transparent'"
      >
        <CaseLocations :filters="filters" />
      </div>

      <!-- Daily Cases by Source -->
      <div 
        class="shadow-xl rounded-lg p-4 md:col-span-2 border"
        :class="isDarkMode 
          ? 'bg-neutral-900 border-transparent' 
          : 'bg-white border-transparent'"
      >
        <CasesBySourceDaily :filters="filters" />
      </div>

      <!-- Case Status + Priority -->
      <div 
        class="shadow-xl rounded-lg p-4 md:col-span-2 border"
        :class="isDarkMode 
          ? 'bg-neutral-900 border-transparent' 
          : 'bg-white border-transparent'"
      >
        <CaseStatusPriority :filters="filters" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import CasesFilters from "@/components/dashboard/CasesFilters.vue"
import CaseCategories from "@/components/dashboard/CaseCategories.vue"
import CaseLocations from "@/components/dashboard/CaseLocations.vue"
import CasesBySourceDaily from "@/components/dashboard/CasesBySourceDaily.vue"
import CaseStatusPriority from "@/components/dashboard/CaseStatusPriority.vue"

// Inject theme
const isDarkMode = inject('isDarkMode')

// Filters now use actual backend field names
const filters = ref({
  gbv_related: '1,2' // Default to both
})

function applyFilters(updatedFilters) {
  filters.value = updatedFilters
}
</script>
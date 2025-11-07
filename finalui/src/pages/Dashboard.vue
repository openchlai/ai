<template>
  <div class="p-6 space-y-6">

    <h1 class="text-2xl font-bold text-gray-800 mb-4">Dashboard</h1>

    <!-- 🔥 Shared Filters Bar -->
    <CasesFilters @update:filters="applyFilters" />

    <!-- Grid for the analytics blocks -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">

      <!-- Case Categories -->
      <div class="bg-white shadow rounded-lg p-4">
        <CaseCategories :filters="filters" />
      </div>

      <!-- Case Locations -->
      <div class="bg-white shadow rounded-lg p-4">
        <CaseLocations :filters="filters" />
      </div>

      <!-- Daily Cases by Source -->
      <div class="bg-white shadow rounded-lg p-4 md:col-span-2">
        <CasesBySourceDaily :filters="filters" />
      </div>

      <!-- Case Status + Priority -->
      <div class="bg-white shadow rounded-lg p-4 md:col-span-2">
        <CaseStatusPriority :filters="filters" />
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import CasesFilters from "@/components/dashboard/CasesFilters.vue";
import CaseCategories from "@/components/dashboard/CaseCategories.vue";
import CaseLocations from "@/components/dashboard/CaseLocations.vue";
import CasesBySourceDaily from "@/components/dashboard/CasesBySourceDaily.vue";
import CaseStatusPriority from "@/components/dashboard/CaseStatusPriority.vue";

const filters = ref({
  dash_period: 'all',
  dash_gbv: 'both',
  dash_src: 'all'
})

function applyFilters(updatedFilters) {
  filters.value = updatedFilters
}
</script>
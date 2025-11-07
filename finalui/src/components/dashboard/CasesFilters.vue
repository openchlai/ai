<template>
  <div class="w-full bg-white rounded-lg p-4 shadow-sm border mb-4 flex flex-wrap gap-4">

    <!-- Duration Filter -->
    <div class="flex flex-col">
      <label class="text-sm font-medium mb-1">Duration</label>
      <select v-model="filters.dash_period" class="border rounded px-3 py-2 text-sm">
        <option value="all">All</option>
        <option value="today">Today</option>
        <option value="this_week">This Week</option>
        <option value="this_month">This Month</option>
        <option value="last_3_month">Last 3 Months</option>
        <option value="last_6_month">Last 6 Months</option>
        <option value="last_9_month">Last 9 Months</option>
        <option value="this_year">This Year</option>
      </select>
    </div>

    <!-- GBV Filter -->
    <div class="flex flex-col">
      <label class="text-sm font-medium mb-1">GBV</label>
      <select v-model="filters.dash_gbv" class="border rounded px-3 py-2 text-sm">
        <option value="both">Both</option>
        <option value="vac">VAC</option>
        <option value="gbv">GBV</option>
      </select>
    </div>

    <!-- Source Filter -->
    <div class="flex flex-col">
      <label class="text-sm font-medium mb-1">Source</label>
      <select v-model="filters.dash_src" class="border rounded px-3 py-2 text-sm">
        <option value="all">All</option>
        <option value="call">Call</option>
        <option value="sms">SMS</option>
        <option value="email">Email</option>
        <option value="walkin">Walk-in</option>
        <option value="social">Social</option>
      </select>
    </div>

    <!-- Apply Button -->
    <div class="flex items-end">
      <button
        @click="emitFilters"
        class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition text-sm"
      >
        Apply
      </button>
    </div>

  </div>
</template>

<script setup>
import { reactive, onMounted } from 'vue'

const emit = defineEmits(['update:filters'])

const filters = reactive({
  dash_period: 'all',
  dash_gbv: 'both',
  dash_src: 'all'
})

function emitFilters() {
  emit('update:filters', { ...filters })
}

// Emit default filters on mount so widgets load immediately
onMounted(() => {
  emitFilters()
})
</script>
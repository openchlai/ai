<template>
  <div class="relative border-l-2 border-gray-200 pl-6 space-y-6">
    <div
      v-for="caseItem in cases"
      :key="cases_k.id ? caseItem[cases_k.id[0]] : caseItem.id"
      class="relative bg-white shadow rounded-lg p-4"
    >
      <!-- Timeline Dot -->
      <div class="absolute -left-3 top-4 w-6 h-6 bg-blue-500 rounded-full border-4 border-white"></div>

      <!-- Case Info -->
      <h3 class="text-lg font-semibold text-gray-800">
        Case #{{ getValue(caseItem, 'id') }}
      </h3>
      <p class="text-sm text-gray-500">
        Created on: {{ formatDate(getValue(caseItem, 'dt')) }}
      </p>
      <p class="text-sm text-gray-600">
        Created by: {{ getValue(caseItem, 'created_by') || 'N/A' }}
      </p>

      <!-- Labels -->
      <div class="flex flex-wrap gap-2 mt-3">
        <!-- Priority -->
        <span
          :class="[
            'px-3 py-1 rounded-full text-xs font-medium',
            getPriorityClass(getValue(caseItem, 'priority'))
          ]"
        >
          Priority:
          {{ getPriorityText(getValue(caseItem, 'priority')) }}
        </span>

        <!-- Status -->
        <span
          :class="[
            'px-3 py-1 rounded-full text-xs font-medium',
            getStatusClass(getValue(caseItem, 'status'))
          ]"
        >
          Status:
          {{ getStatusText(getValue(caseItem, 'status')) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  cases: Array,
  cases_k: Object,
});

// Map the array-style structure
const getValue = (caseItem, key) => {
  if (!props.cases_k?.[key]) return null;
  return caseItem[props.cases_k[key][0]];
};

// Format timestamps nicely
const formatDate = (timestamp) => {
  if (!timestamp) return 'N/A';
  const value =
    timestamp < 10000000000 ? timestamp * 1000 : timestamp * 3600 * 1000;
  return new Date(value).toLocaleString();
};

// --- Priority ---
const getPriorityClass = (priority) => {
  switch (String(priority)) {
    case '3':
      return 'bg-red-100 text-red-700'; // High
    case '2':
      return 'bg-yellow-100 text-yellow-700'; // Medium
    case '1':
    default:
      return 'bg-green-100 text-green-700'; // Low
  }
};

const getPriorityText = (priority) => {
  switch (String(priority)) {
    case '3':
      return 'High';
    case '2':
      return 'Medium';
    case '1':
      return 'Low';
    default:
      return 'Unknown';
  }
};

// --- Status ---
const getStatusClass = (status) => {
  switch (String(status)) {
    case '2':
      return 'bg-green-100 text-green-700'; // Closed
    case '1':
    default:
      return 'bg-yellow-100 text-yellow-700'; // Open
  }
};

const getStatusText = (status) => {
  switch (String(status)) {
    case '2':
      return 'Closed';
    case '1':
      return 'Open';
    default:
      return 'Unknown';
  }
};
</script>

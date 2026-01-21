<template>
  <div class="bg-white shadow rounded-lg overflow-hidden">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-100">
        <tr>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">Case ID</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">Created By</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">Created On</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">Source</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">Priority</th>
          <th class="px-4 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
        </tr>
      </thead>

      <tbody class="divide-y divide-gray-100">
        <tr
          v-for="caseItem in cases"
          :key="cases_k.id ? caseItem[cases_k.id[0]] : caseItem.id"
          class="hover:bg-gray-50 transition"
        >
          <td class="px-4 py-2">
            {{ getValue(caseItem, 'id') }}
          </td>
          <td class="px-4 py-2">
            {{ getValue(caseItem, 'created_by') || 'N/A' }}
          </td>
          <td class="px-4 py-2">
            {{ formatDate(getValue(caseItem, 'dt')) }}
          </td>
          <td class="px-4 py-2">
            {{ getValue(caseItem, 'src') || 'N/A' }}
          </td>

          <!-- Priority -->
          <td class="px-4 py-2">
            <span
              :class="[
                'px-2 py-1 rounded-full text-xs font-semibold',
                getPriorityClass(getValue(caseItem, 'priority'))
              ]"
            >
              {{ formatPriority(getValue(caseItem, 'priority')) }}
            </span>
          </td>

          <!-- Status -->
          <td class="px-4 py-2">
            <span
              :class="[
                'px-2 py-1 rounded-full text-xs font-semibold',
                getStatusClass(getValue(caseItem, 'status'))
              ]"
            >
              {{ formatStatus(getValue(caseItem, 'status')) }}
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
const props = defineProps({
  cases: Array,
  cases_k: Object,
});

// Access values using the cases_k structure
const getValue = (caseItem, key) => {
  if (!props.cases_k?.[key]) return null;
  return caseItem[props.cases_k[key][0]];
};

// Convert timestamp to readable date
const formatDate = (timestamp) => {
  if (!timestamp) return 'N/A';
  const value =
    timestamp < 10000000000 ? timestamp * 1000 : timestamp * 3600 * 1000;
  return new Date(value).toLocaleString();
};

// Priority label formatter
const formatPriority = (priority) => {
  if (!priority) return 'N/A';
  switch (Number(priority)) {
    case 3:
      return 'High';
    case 2:
      return 'Medium';
    case 1:
      return 'Low';
    default:
      return 'Unknown';
  }
};

// Status label formatter
const formatStatus = (status) => {
  if (!status) return 'N/A';
  switch (Number(status)) {
    case 1:
      return 'Open';
    case 2:
      return 'Closed';
    default:
      return 'Unknown';
  }
};

// Tailwind color classes based on priority
const getPriorityClass = (priority) => {
  switch (Number(priority)) {
    case 3: // High
      return 'bg-red-100 text-red-700';
    case 2: // Medium
      return 'bg-yellow-100 text-yellow-700';
    case 1: // Low
      return 'bg-green-100 text-green-700';
    default:
      return 'bg-gray-100 text-gray-600';
  }
};

// Tailwind color classes based on status
const getStatusClass = (status) => {
  switch (Number(status)) {
    case 1: // Open
      return 'bg-yellow-100 text-yellow-700';
    case 2: // Closed
      return 'bg-green-100 text-green-700';
    default:
      return 'bg-gray-100 text-gray-600';
  }
};
</script>

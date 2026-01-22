<template>
  <div 
    class="shadow-xl rounded-lg overflow-hidden border"
    :class="isDarkMode 
      ? 'bg-neutral-900 border-transparent' 
      : 'bg-white border-transparent'"
  >
    <!-- Activities Table -->
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr 
            class="border-b"
            :class="isDarkMode 
              ? 'bg-black/60 border-transparent' 
              : 'bg-gray-50 border-transparent'"
          >
            <th 
              class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              ID
            </th>
            <th 
              class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Created On
            </th>
            <th 
              class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Created By
            </th>
            <th 
              class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Case ID
            </th>
            <th 
              class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Assigned To
            </th>
            <th 
              class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Channel
            </th>
            <th 
              class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Action Detail
            </th>
            <th 
              class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Disposition
            </th>
          </tr>
        </thead>
        <tbody 
          class="divide-y"
          :class="isDarkMode ? 'divide-gray-700' : 'divide-gray-200'"
        >
          <tr 
            v-for="activity in activities" 
            :key="activity.id" 
            class="transition-all duration-200"
            :class="isDarkMode 
              ? 'hover:bg-neutral-800' 
              : 'hover:bg-gray-50'"
          >
            <td 
              class="px-6 py-4 whitespace-nowrap text-sm"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              {{ activity.id }}
            </td>
            <td 
              class="px-6 py-4 whitespace-nowrap text-sm"
              :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
            >
              {{ formatTimestamp(activity.created_on) }}
            </td>
            <td 
              class="px-6 py-4 whitespace-nowrap text-sm"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              {{ activity.created_by }}
            </td>
            <td 
              class="px-6 py-4 whitespace-nowrap text-sm font-medium"
              :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
            >
              #{{ activity.case_id }}
            </td>
            <td 
              class="px-6 py-4 whitespace-nowrap text-sm"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              {{ activity.assigned_to }}
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <span 
                class="px-3 py-1 rounded-full text-xs font-medium uppercase border"
                :class="isDarkMode 
                  ? 'bg-amber-600/20 text-amber-500 border-amber-600/30' 
                  : 'bg-amber-100 text-amber-700 border-amber-300'"
              >
                {{ activity.src }}
              </span>
            </td>
            <td 
              class="px-6 py-4 text-sm max-w-xs truncate"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              {{ activity.action_detail }}
            </td>
            <td 
              class="px-6 py-4 text-sm"
              :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
            >
              {{ activity.dispositions }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div 
      v-if="!activities || activities.length === 0" 
      class="text-center py-12"
    >
      <i-mdi-bell-off-outline 
        class="w-16 h-16 mx-auto mb-4"
        :class="isDarkMode ? 'text-gray-600' : 'text-gray-400'"
      />
      <p 
        :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
      >
        No activities found
      </p>
    </div>
  </div>
</template>

<script setup>
import { inject } from 'vue'

defineProps({
  activities: {
    type: Array,
    default: () => []
  }
})

// Inject theme
const isDarkMode = inject('isDarkMode')

// Format unix timestamp to readable date
function formatTimestamp(timestamp) {
  if (!timestamp || timestamp === '0') return '-'
  const date = new Date(parseInt(timestamp) * 1000)
  return date.toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
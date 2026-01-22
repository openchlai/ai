<template>
  <div class="space-y-6">
    <div 
      v-for="(group, date) in groupedActivities" 
      :key="date" 
      class="shadow-xl rounded-lg overflow-hidden border"
      :class="isDarkMode 
        ? 'bg-neutral-900 border-transparent' 
        : 'bg-white border-transparent'"
    >
      <!-- Date Header -->
      <div 
        class="px-6 py-3 border-b"
        :class="isDarkMode 
          ? 'bg-black/60 border-transparent' 
          : 'bg-gray-50 border-transparent'"
      >
        <h3 
          class="text-sm font-semibold flex items-center gap-2"
          :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
        >
          <i-mdi-calendar class="w-4 h-4" />
          {{ date }}
        </h3>
      </div>

      <!-- Activities List -->
      <div 
        class="divide-y"
        :class="isDarkMode ? 'divide-gray-700' : 'divide-gray-200'"
      >
        <div 
          v-for="activity in group" 
          :key="activity.id"
          class="p-6 transition-all duration-200"
          :class="isDarkMode 
            ? 'hover:bg-gray-700/30' 
            : 'hover:bg-gray-50'"
        >
          <div class="flex items-start gap-4">
            <!-- Icon -->
            <div 
              class="flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center border"
              :class="isDarkMode 
                ? 'bg-amber-600/20 border-amber-600/30' 
                : 'bg-amber-100 border-amber-300'"
            >
              <i-mdi-bell 
                class="w-5 h-5"
                :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
              />
            </div>

            <!-- Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-start justify-between gap-4 mb-2">
                <div>
                  <h4 
                    class="text-sm font-semibold"
                    :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
                  >
                    Activity {{ activity.id }}
                  </h4>
                  <p 
                    class="text-xs mt-1"
                    :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
                  >
                    {{ formatTimestamp(activity.created_on) }}
                  </p>
                </div>
                <span 
                  class="px-3 py-1 rounded-full text-xs font-medium uppercase border whitespace-nowrap"
                  :class="isDarkMode 
                    ? 'bg-amber-600/20 text-amber-500 border-amber-600/30' 
                    : 'bg-amber-100 text-amber-700 border-amber-300'"
                >
                  {{ activity.src }}
                </span>
              </div>

              <div class="grid grid-cols-2 gap-4 mt-3">
                <div>
                  <p 
                    class="text-xs mb-1"
                    :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
                  >
                    Created By
                  </p>
                  <p 
                    class="text-sm"
                    :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                  >
                    {{ activity.created_by }}
                  </p>
                </div>
                <div>
                  <p 
                    class="text-xs mb-1"
                    :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
                  >
                    Assigned To
                  </p>
                  <p 
                    class="text-sm"
                    :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                  >
                    {{ activity.assigned_to }}
                  </p>
                </div>
                <div>
                  <p 
                    class="text-xs mb-1"
                    :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
                  >
                    Case ID
                  </p>
                  <p 
                    class="text-sm font-medium"
                    :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
                  >
                    {{ activity.case_id }}
                  </p>
                </div>
                <div>
                  <p 
                    class="text-xs mb-1"
                    :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
                  >
                    Disposition
                  </p>
                  <p 
                    class="text-sm"
                    :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
                  >
                    {{ activity.dispositions || '-' }}
                  </p>
                </div>
              </div>

              <div 
                v-if="activity.action_detail" 
                class="mt-3 pt-3 border-t"
                :class="isDarkMode ? 'border-transparent' : 'border-transparent'"
              >
                <p 
                  class="text-xs mb-1"
                  :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
                >
                  Action Detail
                </p>
                <p 
                  class="text-sm"
                  :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                >
                  {{ activity.action_detail }}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div 
      v-if="Object.keys(groupedActivities).length === 0" 
      class="shadow-xl rounded-lg border p-12 text-center"
      :class="isDarkMode 
        ? 'bg-neutral-900 border-transparent' 
        : 'bg-white border-transparent'"
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
import { computed, inject } from 'vue'

const props = defineProps({
  activities: {
    type: Array,
    default: () => []
  }
})

// Inject theme
const isDarkMode = inject('isDarkMode')

// Group activities by date
const groupedActivities = computed(() => {
  const groups = {}
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)

  props.activities.forEach(activity => {
    const timestamp = activity.created_on
    if (!timestamp || timestamp === '0') return

    const date = new Date(parseInt(timestamp) * 1000)
    let label

    if (date.toDateString() === today.toDateString()) {
      label = 'Today'
    } else if (date.toDateString() === yesterday.toDateString()) {
      label = 'Yesterday'
    } else {
      label = date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    if (!groups[label]) groups[label] = []
    groups[label].push(activity)
  })

  return groups
})

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
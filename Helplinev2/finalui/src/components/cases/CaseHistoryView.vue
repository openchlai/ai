<template>
  <div class="space-y-6">
    <div
      class="p-4 rounded-lg border-l-4"
      :class="isDarkMode
        ? 'bg-purple-900/20 border-purple-500 text-purple-300'
        : 'bg-purple-50 border-purple-500 text-purple-800'"
    >
      <p class="text-sm">View all changes and updates to this case</p>
    </div>

    <!-- History Timeline -->
    <div class="space-y-4">
      <!-- History Items -->
      <div
        v-for="(item, index) in mockHistory"
        :key="index"
        class="relative pl-8 pb-6 border-l-2"
        :class="isDarkMode ? 'border-transparent' : 'border-transparent'"
      >
        <!-- Timeline Dot -->
        <div
          class="absolute -left-2 top-0 w-4 h-4 rounded-full border-2"
          :class="[
            isDarkMode ? 'border-transparent' : 'border-white',
            getTimelineDotColor(item.type)
          ]"
        ></div>

        <!-- History Card -->
        <div
          class="rounded-lg border p-4"
          :class="isDarkMode
            ? 'bg-gray-800 border-transparent'
            : 'bg-white border-transparent'"
        >
          <div class="flex items-start justify-between mb-2">
            <div class="flex items-center gap-2">
              <component
                :is="getHistoryIcon(item.type)"
                class="w-5 h-5"
                :class="getHistoryIconColor(item.type)"
              />
              <h5
                class="font-semibold"
                :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'"
              >
                {{ item.title }}
              </h5>
            </div>
            <span
              class="text-xs whitespace-nowrap ml-4"
              :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
            >
              {{ item.timeAgo }}
            </span>
          </div>

          <p
            class="text-sm mb-2"
            :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
          >
            {{ item.description }}
          </p>

          <!-- Changes -->
          <div
            v-if="item.changes && item.changes.length"
            class="mt-3 space-y-1"
          >
            <div
              v-for="(change, idx) in item.changes"
              :key="idx"
              class="text-xs flex items-center gap-2 p-2 rounded"
              :class="isDarkMode
                ? 'bg-gray-900/50'
                : 'bg-gray-50'"
            >
              <span :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'">
                {{ change.field }}:
              </span>
              <span
                class="line-through"
                :class="isDarkMode ? 'text-red-400' : 'text-red-600'"
              >
                {{ change.oldValue }}
              </span>
              <i-mdi-arrow-right class="w-3 h-3" :class="isDarkMode ? 'text-gray-600' : 'text-gray-400'" />
              <span
                class="font-medium"
                :class="isDarkMode ? 'text-green-400' : 'text-green-600'"
              >
                {{ change.newValue }}
              </span>
            </div>
          </div>

          <!-- User Info -->
          <div class="flex items-center gap-2 mt-3 pt-3 border-t" :class="isDarkMode ? 'border-transparent' : 'border-transparent'">
            <i-mdi-account-circle 
              class="w-4 h-4"
              :class="isDarkMode ? 'text-gray-500' : 'text-gray-400'"
            />
            <p
              class="text-xs"
              :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
            >
              Updated by: <span class="font-medium">{{ item.user }}</span>
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Mock Notice -->
    <div
      class="p-4 rounded-lg border"
      :class="isDarkMode
        ? 'bg-gray-800 border-transparent'
        : 'bg-gray-100 border-transparent'"
    >
      <div class="flex items-start gap-3">
        <i-mdi-information-outline 
          class="w-5 h-5 mt-0.5"
          :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
        />
        <div>
          <p 
            class="text-sm font-semibold mb-1"
            :class="isDarkMode ? 'text-gray-200' : 'text-gray-800'"
          >
            Mock Data
          </p>
          <p 
            class="text-xs"
            :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
          >
            This is sample history data. Actual case history will be integrated with the backend API in the next update.
          </p>
        </div>
      </div>
    </div>

    <!-- Back Button -->
    <button
      @click="$emit('back')"
      class="w-full px-6 py-3 rounded-lg font-medium transition-all duration-200 border flex items-center justify-center gap-2"
      :class="isDarkMode
        ? 'bg-gray-800 text-gray-300 border-transparent hover:bg-gray-700'
        : 'bg-white text-gray-700 border-transparent hover:bg-gray-50'"
    >
      <i-mdi-arrow-left class="w-5 h-5" />
      Back to Details
    </button>
  </div>
</template>

<script setup>
import { inject } from 'vue'

defineProps({
  caseItem: {
    type: Object,
    required: true
  }
})

defineEmits(['back'])

// Inject theme
const isDarkMode = inject('isDarkMode')

// Mock history data
const mockHistory = [
  {
    type: 'update',
    title: 'Case Status Updated',
    description: 'Case priority was escalated and status changed',
    timeAgo: '2 hours ago',
    user: 'John Doe',
    changes: [
      { field: 'Priority', oldValue: 'Medium', newValue: 'High' },
      { field: 'Status', oldValue: 'Open', newValue: 'In Progress' }
    ]
  },
  {
    type: 'comment',
    title: 'Comment Added',
    description: 'Client has been contacted and scheduled for follow-up counseling session next Tuesday at 2:00 PM.',
    timeAgo: '1 day ago',
    user: 'Jane Smith',
    changes: []
  },
  {
    type: 'escalation',
    title: 'Case Escalated',
    description: 'Case escalated to supervisor due to complexity',
    timeAgo: '2 days ago',
    user: 'Michael Johnson',
    changes: [
      { field: 'Escalated To', oldValue: 'None', newValue: 'Sarah Williams - Supervisor' }
    ]
  },
  {
    type: 'update',
    title: 'Assessment Updated',
    description: 'General case assessment status changed',
    timeAgo: '3 days ago',
    user: 'John Doe',
    changes: [
      { field: 'Assessment', oldValue: 'Not Started', newValue: 'Progressing' }
    ]
  },
  {
    type: 'client',
    title: 'Client Added',
    description: 'New client "Maria Garcia" added to the case',
    timeAgo: '5 days ago',
    user: 'Jane Smith',
    changes: []
  },
  {
    type: 'created',
    title: 'Case Created',
    description: 'Case was initially created and assigned',
    timeAgo: '1 week ago',
    user: 'John Doe',
    changes: []
  }
]

// Helper functions for styling
const getTimelineDotColor = (type) => {
  const colors = {
    update: isDarkMode.value ? 'bg-amber-500' : 'bg-amber-600',
    comment: isDarkMode.value ? 'bg-green-500' : 'bg-green-600',
    escalation: isDarkMode.value ? 'bg-orange-500' : 'bg-orange-600',
    client: isDarkMode.value ? 'bg-purple-500' : 'bg-purple-600',
    created: isDarkMode.value ? 'bg-gray-500' : 'bg-gray-600'
  }
  return colors[type] || colors.update
}

const getHistoryIcon = (type) => {
  const icons = {
    update: 'i-mdi-update',
    comment: 'i-mdi-comment-text',
    escalation: 'i-mdi-arrow-up-bold',
    client: 'i-mdi-account-plus',
    created: 'i-mdi-plus-circle'
  }
  return icons[type] || 'i-mdi-information'
}

const getHistoryIconColor = (type) => {
  const colors = {
    update: isDarkMode.value ? 'text-amber-500' : 'text-amber-700',
    comment: isDarkMode.value ? 'text-green-400' : 'text-green-600',
    escalation: isDarkMode.value ? 'text-orange-400' : 'text-orange-600',
    client: isDarkMode.value ? 'text-purple-400' : 'text-purple-600',
    created: isDarkMode.value ? 'text-gray-400' : 'text-gray-600'
  }
  return colors[type] || colors.update
}
</script>
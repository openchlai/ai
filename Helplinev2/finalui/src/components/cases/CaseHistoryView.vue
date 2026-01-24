<template>
  <div class="space-y-6">
    <div class="p-4 rounded-lg border-l-4" :class="isDarkMode
      ? 'bg-purple-900/20 border-purple-500 text-purple-300'
      : 'bg-purple-50 border-purple-500 text-purple-800'">
      <div class="flex items-center gap-2">
        <i-mdi-history class="w-5 h-5" />
        <p class="text-sm font-semibold">Case History Timeline</p>
      </div>
      <p class="text-xs mt-1 opacity-80">Track all modifications and life-cycle events for this case.</p>
    </div>

    <!-- Empty State -->
    <div v-if="!activities || activities.length === 0" class="text-center py-12 border border-dashed rounded-lg"
      :class="isDarkMode ? 'border-gray-800 text-gray-500' : 'border-gray-200 text-gray-400'">
      <i-mdi-history class="w-12 h-12 mx-auto mb-3 opacity-20" />
      <p>No activity history found for this case.</p>
    </div>

    <!-- History Timeline -->
    <div v-else class="space-y-4">
      <div v-for="(item, index) in activities" :key="index" class="relative pl-8 pb-6 border-l-2"
        :class="isDarkMode ? 'border-gray-800' : 'border-gray-100'">
        <!-- Timeline Dot -->
        <div class="absolute -left-2 top-0 w-4 h-4 rounded-full border-2" :class="[
          isDarkMode ? 'border-black' : 'border-white',
          getTimelineDotColor(getActVal(item, 'activity'))
        ]"></div>

        <!-- History Card -->
        <div class="rounded-lg border p-4 transition-all hover:shadow-md" :class="isDarkMode
          ? 'bg-black border-gray-800 hover:border-gray-700'
          : 'bg-white border-gray-100 hover:border-gray-200'">
          <div class="flex items-start justify-between mb-2">
            <div class="flex items-center gap-2">
              <component :is="getHistoryIcon(getActVal(item, 'activity'))" class="w-5 h-5"
                :class="getHistoryIconColor(getActVal(item, 'activity'))" />
              <div>
                <h5 class="font-semibold text-sm" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">
                  {{ formatActivityTitle(getActVal(item, 'activity')) }}
                </h5>
                <p class="text-xs" :class="isDarkMode ? 'text-gray-500' : 'text-gray-400'">
                  Action ID: #{{ getActVal(item, 'id') }}
                </p>
              </div>
            </div>
            <span class="text-xs font-medium px-2 py-1 rounded"
              :class="isDarkMode ? 'bg-gray-800 text-gray-400' : 'bg-gray-100 text-gray-600'">
              {{ formatDate(getActVal(item, 'created_on')) }}
            </span>
          </div>

          <div class="space-y-3">
            <!-- Details / Description -->
            <div class="grid grid-cols-2 gap-x-4 gap-y-2 mt-2">
              <div v-if="getActVal(item, 'status')">
                <span class="text-[10px] uppercase font-bold text-gray-500 block">Status</span>
                <span class="text-xs font-medium" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                  {{ formatStatus(getActVal(item, 'status')) }}
                </span>
              </div>
              <div v-if="getActVal(item, 'disposition')">
                <span class="text-[10px] uppercase font-bold text-gray-500 block">Disposition</span>
                <span class="text-xs font-medium" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                  {{ getActVal(item, 'disposition') }}
                </span>
              </div>
              <div v-if="getActVal(item, 'src')">
                <span class="text-[10px] uppercase font-bold text-gray-500 block">Channel</span>
                <span class="text-xs font-medium text-amber-500">
                  {{ getActVal(item, 'src') }}
                </span>
              </div>
              <div v-if="getActVal(item, 'change_count') !== '0'">
                <span class="text-[10px] uppercase font-bold text-gray-500 block">Changes</span>
                <span class="text-xs font-medium" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                  {{ getActVal(item, 'change_count') }} fields updated
                </span>
              </div>
            </div>

            <p v-if="getActVal(item, 'detail')" class="text-sm p-3 rounded italic"
              :class="isDarkMode ? 'bg-gray-900 text-gray-400' : 'bg-gray-50 text-gray-600'">
              "{{ getActVal(item, 'detail') }}"
            </p>

            <!-- User Info -->
            <div class="flex items-center gap-2 pt-3 border-t"
              :class="isDarkMode ? 'border-gray-800' : 'border-gray-100'">
              <div
                class="w-6 h-6 rounded-full bg-purple-500 flex items-center justify-center text-[10px] text-white font-bold">
                {{ String(getActVal(item, 'created_by')).charAt(0) }}
              </div>
              <p class="text-xs" :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'">
                Modified by: <span class="font-semibold" :class="isDarkMode ? 'text-gray-200' : 'text-gray-800'">{{
                  getActVal(item, 'created_by') }}</span>
                <span class="ml-1 opacity-60">({{ getActVal(item, 'created_by_role') }})</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Back Button -->
    <button @click="$emit('back')"
      class="w-full px-6 py-4 rounded-xl font-bold transition-all duration-200 border-2 flex items-center justify-center gap-3 active:scale-[0.98]"
      :class="isDarkMode
        ? 'bg-black text-gray-300 border-gray-800 hover:border-purple-500 hover:text-purple-400'
        : 'bg-white text-gray-700 border-gray-200 hover:border-purple-600 hover:text-purple-700'">
      <i-mdi-arrow-left class="w-5 h-5" />
      Return to Case Overview
    </button>
  </div>
</template>

<script setup>
  import { inject } from 'vue'

  const props = defineProps({
    caseItem: {
      type: Array,
      required: true
    },
    cases_k: {
      type: Object,
      required: true
    },
    activities: {
      type: Array,
      default: () => []
    },
    activities_k: {
      type: Object,
      default: () => ({})
    }
  })

  defineEmits(['back'])

  // Inject theme
  const isDarkMode = inject('isDarkMode')

  // Helper to get value from activity array using mapping
  const getActVal = (actArr, key) => {
    if (!actArr || !props.activities_k?.[key]) return null
    const index = props.activities_k[key][0]
    return actArr[index]
  }

  // Format date
  const formatDate = (timestamp) => {
    if (!timestamp) return 'N/A'
    const value = timestamp < 10000000000 ? timestamp * 1000 : timestamp
    return new Date(value).toLocaleString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const formatActivityTitle = (type) => {
    switch (String(type)) {
      case '1': return 'Case Initially Created'
      case '2': return 'General Update'
      case '3': return 'Manual Log / Activity'
      case '4': return 'Status Escalation'
      case '5': return 'Assignment Change'
      default: return 'Case Activity'
    }
  }

  const formatStatus = (status) => {
    switch (String(status)) {
      case '1': return 'Open'
      case '2': return 'Closed'
      case '3': return 'Pending'
      default: return 'Active'
    }
  }

  // Styling helpers
  const getTimelineDotColor = (type) => {
    switch (String(type)) {
      case '1': return isDarkMode.value ? 'bg-green-500' : 'bg-green-600'
      case '2': return isDarkMode.value ? 'bg-amber-500' : 'bg-amber-600'
      case '3': return isDarkMode.value ? 'bg-purple-500' : 'bg-purple-600'
      case '4': return isDarkMode.value ? 'bg-red-500' : 'bg-red-600'
      default: return isDarkMode.value ? 'bg-blue-500' : 'bg-blue-600'
    }
  }

  const getHistoryIcon = (type) => {
    switch (String(type)) {
      case '1': return 'i-mdi-plus-circle'
      case '2': return 'i-mdi-update'
      case '3': return 'i-mdi-card-text-outline'
      case '4': return 'i-mdi-arrow-up-bold-circle'
      case '5': return 'i-mdi-account-arrow-right'
      default: return 'i-mdi-information-outline'
    }
  }

  const getHistoryIconColor = (type) => {
    switch (String(type)) {
      case '1': return 'text-green-500'
      case '2': return 'text-amber-500'
      case '3': return 'text-purple-500'
      case '4': return 'text-red-500'
      default: return 'text-blue-500'
    }
  }
</script>
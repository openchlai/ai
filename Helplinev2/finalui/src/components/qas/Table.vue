<template>
  <div 
    class="rounded-lg shadow-xl border overflow-hidden"
    :class="isDarkMode 
      ? 'bg-neutral-900 border-transparent' 
      : 'bg-white border-transparent'"
  >
    <div class="overflow-x-auto">
      <table class="w-full min-w-[1400px]">
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
              Call Date
            </th>
            <th 
              class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              User
            </th>
            <th 
              class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Talk Time
            </th>
            <th 
              class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Opening
            </th>
            <th 
              class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Listening
            </th>
            <th 
              class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Proactive
            </th>
            <th 
              class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Resolution
            </th>
            <th 
              class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Holding
            </th>
            <th 
              class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Closing
            </th>
            <th 
              class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Total Score
            </th>
            <th 
              class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Supervisor
            </th>
            <th 
              class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Created On
            </th>
          </tr>
        </thead>

        <tbody 
          class="divide-y"
          :class="isDarkMode ? 'divide-gray-700' : 'divide-gray-200'"
        >
          <tr
            v-for="(qa, i) in qas"
            :key="i"
            class="transition-all duration-200"
            :class="isDarkMode 
              ? 'hover:bg-neutral-800' 
              : 'hover:bg-gray-50'"
          >
            <!-- Call Date -->
            <td 
              class="px-6 py-4 text-sm whitespace-nowrap"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              {{ formatTimestamp(qa[qas_k.chan_chan_ts[0]]) }}
            </td>

            <!-- User -->
            <td 
              class="px-6 py-4 text-sm whitespace-nowrap"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              {{ qa[qas_k.chan_user_name[0]] }}
            </td>

            <!-- Talk Time -->
            <td 
              class="px-6 py-4 text-sm whitespace-nowrap"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              {{ formatTalkTime(qa[qas_k.chan_talk_time[0]]) }}
            </td>

            <!-- Scores -->
            <td class="px-6 py-4 text-sm whitespace-nowrap">
              <span 
                class="px-2 py-1 rounded font-medium"
                :class="isDarkMode 
                  ? 'bg-amber-600/20 text-amber-500' 
                  : 'bg-amber-100 text-amber-700'"
              >
                {{ qa[qas_k.opening_phrase[0]] }}%
              </span>
            </td>
            <td class="px-6 py-4 text-sm whitespace-nowrap">
              <span 
                class="px-2 py-1 rounded font-medium"
                :class="isDarkMode 
                  ? 'bg-amber-600/20 text-amber-500' 
                  : 'bg-amber-100 text-amber-700'"
              >
                {{ qa[qas_k.listening_score_p[0]] }}%
              </span>
            </td>
            <td class="px-6 py-4 text-sm whitespace-nowrap">
              <span 
                class="px-2 py-1 rounded font-medium"
                :class="isDarkMode 
                  ? 'bg-amber-600/20 text-amber-500' 
                  : 'bg-amber-100 text-amber-700'"
              >
                {{ qa[qas_k.proactive_score_p[0]] }}%
              </span>
            </td>
            <td class="px-6 py-4 text-sm whitespace-nowrap">
              <span 
                class="px-2 py-1 rounded font-medium"
                :class="isDarkMode 
                  ? 'bg-amber-600/20 text-amber-500' 
                  : 'bg-amber-100 text-amber-700'"
              >
                {{ qa[qas_k.resolution_score_p[0]] }}%
              </span>
            </td>
            <td class="px-6 py-4 text-sm whitespace-nowrap">
              <span 
                class="px-2 py-1 rounded font-medium"
                :class="isDarkMode 
                  ? 'bg-amber-600/20 text-amber-500' 
                  : 'bg-amber-100 text-amber-700'"
              >
                {{ qa[qas_k.holding_score_p[0]] }}%
              </span>
            </td>
            <td class="px-6 py-4 text-sm whitespace-nowrap">
              <span 
                class="px-2 py-1 rounded font-medium"
                :class="isDarkMode 
                  ? 'bg-amber-600/20 text-amber-500' 
                  : 'bg-amber-100 text-amber-700'"
              >
                {{ qa[qas_k.closing_score_p[0]] }}%
              </span>
            </td>
            <td class="px-6 py-4 text-sm whitespace-nowrap">
              <span 
                class="px-3 py-1 rounded-full font-semibold border"
                :class="isDarkMode 
                  ? 'bg-green-600/20 text-green-400 border-green-600/30' 
                  : 'bg-green-100 text-green-700 border-green-300'"
              >
                {{ qa[qas_k.total_score_p[0]] }}%
              </span>
            </td>

            <!-- Supervisor -->
            <td 
              class="px-6 py-4 text-sm whitespace-nowrap"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              {{ qa[qas_k.created_by[0]] }}
            </td>

            <!-- Created On -->
            <td 
              class="px-6 py-4 text-sm whitespace-nowrap"
              :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
            >
              {{ formatTimestamp(qa[qas_k.created_on[0]]) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div 
      v-if="!qas || qas.length === 0" 
      class="text-center py-12"
    >
      <i-mdi-clipboard-check-outline 
        class="w-16 h-16 mx-auto mb-4"
        :class="isDarkMode ? 'text-gray-600' : 'text-gray-400'"
      />
      <p 
        :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
      >
        No QA records found
      </p>
    </div>
  </div>
</template>

<script setup>
import { inject } from 'vue'

defineProps({
  qas: {
    type: Array,
    required: true,
  },
  qas_k: {
    type: Object,
    required: true,
  },
})

// Inject theme
const isDarkMode = inject('isDarkMode')

/**
 * Convert numeric timestamp (seconds or milliseconds)
 * into readable date format e.g. 17 Oct 2025 9:40 AM
 */
const formatTimestamp = (val) => {
  if (!val) return ''
  let timestamp = Number(val)
  if (timestamp < 10000000000) timestamp *= 1000 // convert seconds → ms if needed
  const date = new Date(timestamp)
  return date.toLocaleString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

/**
 * Convert talk time (in seconds) → "m:ss"
 */
const formatTalkTime = (seconds) => {
  if (!seconds || isNaN(seconds)) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
</script>
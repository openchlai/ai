<template>
  <div class="p-4 bg-white rounded-2xl shadow">
    <table class="min-w-full border-collapse text-sm">
      <thead class="bg-gray-100 text-gray-700">
        <tr>
          <th class="text-left py-2 px-3">Call Date</th>
          <th class="text-left py-2 px-3">User</th>
          <th class="text-left py-2 px-3">Talk Time</th>
          <th class="text-left py-2 px-3">Opening</th>
          <th class="text-left py-2 px-3">Listening</th>
          <th class="text-left py-2 px-3">Proactive</th>
          <th class="text-left py-2 px-3">Resolution</th>
          <th class="text-left py-2 px-3">Holding</th>
          <th class="text-left py-2 px-3">Closing</th>
          <th class="text-left py-2 px-3">Total Score</th>
          <th class="text-left py-2 px-3">Supervisor</th>
          <th class="text-left py-2 px-3">Created On</th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="(qa, i) in qas"
          :key="i"
          class="border-t hover:bg-gray-50 transition"
        >
          <!-- Call Date -->
          <td class="py-2 px-3">
            {{ formatTimestamp(qa[qas_k.chan_chan_ts[0]]) }}
          </td>

          <!-- User -->
          <td class="py-2 px-3">{{ qa[qas_k.chan_user_name[0]] }}</td>

          <!-- Talk Time -->
          <td class="py-2 px-3">{{ formatTalkTime(qa[qas_k.chan_talk_time[0]]) }}</td>

          <!-- Scores -->
          <td class="py-2 px-3">{{ qa[qas_k.opening_phrase[0]] }} %</td>
          <td class="py-2 px-3">{{ qa[qas_k.listening_score_p[0]] }} %</td>
          <td class="py-2 px-3">{{ qa[qas_k.proactive_score_p[0]] }} %</td>
          <td class="py-2 px-3">{{ qa[qas_k.resolution_score_p[0]] }} %</td>
          <td class="py-2 px-3">{{ qa[qas_k.holding_score_p[0]] }} %</td>
          <td class="py-2 px-3">{{ qa[qas_k.closing_score_p[0]] }} %</td>
          <td class="py-2 px-3">{{ qa[qas_k.total_score_p[0]] }} %</td>

          <!-- Supervisor -->
          <td class="py-2 px-3">{{ qa[qas_k.created_by[0]] }}</td>

          <!-- Created On -->
          <td class="py-2 px-3">
            {{ formatTimestamp(qa[qas_k.created_on[0]]) }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
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

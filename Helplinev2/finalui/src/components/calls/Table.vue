<template>
  <div 
    class="rounded-xl shadow-xl overflow-auto border"
    :class="isDarkMode 
      ? 'bg-gray-800 border-transparent' 
      : 'bg-white border-transparent'"
  >
    <table class="min-w-full text-sm text-left">
      <thead 
        class="border-b"
        :class="isDarkMode 
          ? 'bg-gray-900/60 border-transparent' 
          : 'bg-gray-50 border-transparent'"
      >
        <tr>
          <th 
            class="px-4 py-4 text-xs font-semibold uppercase tracking-wider"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            Date
          </th>
          <th 
            class="px-4 py-4 text-xs font-semibold uppercase tracking-wider"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            Direction
          </th>
          <th 
            class="px-4 py-4 text-xs font-semibold uppercase tracking-wider"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            Phone
          </th>
          <th 
            class="px-4 py-4 text-xs font-semibold uppercase tracking-wider"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            Extension
          </th>
          <th 
            class="px-4 py-4 text-xs font-semibold uppercase tracking-wider"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            Wait Time
          </th>
          <th 
            class="px-4 py-4 text-xs font-semibold uppercase tracking-wider"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            Talk Time
          </th>
          <th 
            class="px-4 py-4 text-xs font-semibold uppercase tracking-wider"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            Hangup Status
          </th>
          <th 
            class="px-4 py-4 text-xs font-semibold uppercase tracking-wider"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            Hangup By
          </th>
          <th 
            class="px-4 py-4 text-xs font-semibold uppercase tracking-wider"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            QA Score
          </th>
          <th 
            class="px-4 py-4 text-xs font-semibold uppercase tracking-wider"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            Disposition
          </th>
          <th 
            class="px-4 py-4 text-xs font-semibold uppercase tracking-wider text-center"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            QA
          </th>
        </tr>
      </thead>

      <tbody 
        class="divide-y"
        :class="isDarkMode ? 'divide-gray-700' : 'divide-gray-200'"
      >
        <tr
          v-for="(call, idx) in calls"
          :key="call[callsStore.calls_k?.uniqueid?.[0]] || idx"
          :class="[
            'cursor-pointer transition-all duration-200',
            call[callsStore.calls_k?.uniqueid?.[0]] === selectedCallId 
              ? (isDarkMode 
                  ? 'bg-amber-600/10 border-l-4 border-l-amber-500' 
                  : 'bg-amber-100 border-l-4 border-l-amber-600')
              : (isDarkMode
                  ? 'hover:bg-gray-700/30'
                  : 'hover:bg-gray-50')
          ]"
          @click="emitSelect(call)"
        >
          <!-- Date -->
          <td 
            class="px-4 py-3"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            {{
              call[callsStore.calls_k?.chan_ts?.[0]]
                ? formatDateTime(call[callsStore.calls_k.chan_ts[0]])
                : 'N/A'
            }}
          </td>

          <!-- Direction -->
          <td class="px-4 py-3">
            <span :class="['px-3 py-1 rounded-full text-xs font-semibold border', directionClass(call[callsStore.calls_k?.vector?.[0]])]">
              {{ call[callsStore.calls_k?.vector?.[0]] === '1' ? 'Inbound' : call[callsStore.calls_k?.vector?.[0]] === '2' ? 'Outbound' : 'N/A' }}
            </span>
          </td>

          <!-- Phone -->
          <td 
            class="px-4 py-3 font-medium"
            :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'"
          >
            {{ call[callsStore.calls_k?.phone?.[0]] || 'N/A' }}
          </td>

          <!-- Extension -->
          <td 
            class="px-4 py-3"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            {{ call[callsStore.calls_k?.usr?.[0]] || 'N/A' }}
            <span 
              v-if="call[callsStore.calls_k?.usr_name?.[0]]" 
              class="text-xs block"
              :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
            >
              {{ call[callsStore.calls_k.usr_name[0]] }}
            </span>
          </td>

          <!-- Wait Time -->
          <td 
            class="px-4 py-3"
            :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
          >
            {{ formatDuration(call[callsStore.calls_k?.wait_time_tot?.[0]]) }}
          </td>

          <!-- Talk Time -->
          <td 
            class="px-4 py-3"
            :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
          >
            {{ formatDuration(call[callsStore.calls_k?.talk_time?.[0]]) }}
          </td>

          <!-- Hangup Status -->
          <td class="px-4 py-3">
            <span :class="['px-3 py-1 rounded-full text-xs font-semibold border', statusClass(call[callsStore.calls_k?.hangup_status?.[0]])]">
              {{ getStatusLabel(call[callsStore.calls_k?.hangup_status?.[0]]) }}
            </span>
          </td>

          <!-- Hangup By -->
          <td 
            class="px-4 py-3"
            :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
          >
            {{ getHangupReasonLabel(call[callsStore.calls_k?.hangup_reason?.[0]]) }}
          </td>

          <!-- QA Score -->
          <td 
            class="px-4 py-3 font-medium"
            :class="isDarkMode ? 'text-blue-400' : 'text-amber-700'"
          >
            {{ call[callsStore.calls_k?.qa_score?.[0]] || '-' }}
          </td>

          <!-- Disposition -->
          <td 
            class="px-4 py-3 text-xs"
            :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
          >
            {{ call[callsStore.calls_k?.dispositions?.[0]] || '-' }}
          </td>

          <!-- QA Creation Button -->
          <td class="px-4 py-3 text-center">
            <button 
              @click.stop="emitCreateQA(call)" 
              :disabled="!isAnswered(call)"
              :class="[
                'p-2 rounded transition-all duration-200',
                isAnswered(call) 
                  ? (isDarkMode 
                      ? 'bg-amber-600 text-white hover:bg-amber-700 active:scale-95' 
                      : 'bg-amber-700 text-white hover:bg-amber-800 active:scale-95')
                  : (isDarkMode
                      ? 'bg-gray-700 text-gray-500 cursor-not-allowed opacity-50'
                      : 'bg-gray-200 text-gray-400 cursor-not-allowed opacity-50')
              ]"
              :title="isAnswered(call) ? 'Create QA Evaluation' : 'Only available for answered calls'"
            >
              <i-mdi-clipboard-check class="w-5 h-5" />
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <div 
      v-if="!calls || calls.length === 0" 
      class="p-4 text-center"
      :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
    >
      No calls available.
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, inject } from 'vue'

// Inject theme
const isDarkMode = inject('isDarkMode')

const props = defineProps({
  calls: { type: Array, required: true },
  callsStore: { type: Object, required: true },
  selectedCallId: { type: [String, Number, null], default: null }
})

const emit = defineEmits(['select-call', 'create-qa'])

// Backend hangup_reason mapping
const hangupReasonMap = {
  "": "",
  "phone": "Customer",
  "usr": "Extension",
  "ivr": "IVR",
  "net": "Network"
}

// Backend hangup_status mapping
const hangupStatusMap = {
  "": "",
  "answered": "Answered",
  "abandoned": "Abandoned",
  "dump": "AgentDump",
  "ivr": "IVR",
  "missed": "Missed",
  "no-answer": "Flash",
  "noanswer": "Flash",
  "busy": "Busy",
  "networkerror": "Network Error",
  "voicemail": "Voicemail",
  "xfer_consult": "Consult",
  "xfer_noanswer": "Transfer No Answer",
  "xfer_offline": "Transfer Unavailable",
  "xfer_ok": "Transferred",
  "SCHED": "Sched",
  "Reattempt": "Reattempt"
}

function getHangupReasonLabel(reason) {
  if (!reason) return 'N/A'
  return hangupReasonMap[reason] || reason
}

function getStatusLabel(status) {
  if (!status) return 'Unknown'
  return hangupStatusMap[status] || status
}

function emitSelect(call) {
  const idIndex = props.callsStore.calls_k?.uniqueid?.[0]
  const id = idIndex !== undefined ? call[idIndex] : null
  if (id !== null) emit('select-call', id)
}

function emitCreateQA(call) {
  const idIndex = props.callsStore.calls_k?.uniqueid?.[0]
  const uniqueid = idIndex !== undefined ? call[idIndex] : null
  if (uniqueid !== null) emit('create-qa', uniqueid)
}

// Check if call status is answered
function isAnswered(call) {
  const statusIndex = props.callsStore.calls_k?.hangup_status?.[0]
  if (statusIndex === undefined) return false
  const status = call[statusIndex]
  return status === 'answered'
}

// Format timestamp to readable date and time
function formatDateTime(timestamp) {
  if (!timestamp || timestamp === '0') return 'N/A'
  const date = new Date(parseInt(timestamp) * 1000)
  return date.toLocaleString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  })
}

// Format duration (stored as integer representing centiseconds, display as decimal minutes)
function formatDuration(value) {
  if (!value || value === '0') return '0.00'
  const num = parseFloat(value)
  const minutes = num / 100
  return minutes.toFixed(2)
}

// Direction styling - theme aware
function directionClass(direction) {
  if (!direction) {
    return isDarkMode.value 
      ? 'bg-gray-700/50 text-gray-400 border-transparent'
      : 'bg-gray-100 text-gray-600 border-transparent'
  }
  const d = String(direction)
  if (d === '1') {
    return isDarkMode.value
      ? 'bg-blue-600/20 text-blue-400 border-blue-600/30'
      : 'bg-blue-100 text-blue-700 border-blue-300'
  }
  if (d === '2') {
    return isDarkMode.value
      ? 'bg-green-600/20 text-green-400 border-green-600/30'
      : 'bg-green-100 text-green-700 border-green-300'
  }
  return isDarkMode.value
    ? 'bg-gray-700/50 text-gray-400 border-transparent'
    : 'bg-gray-100 text-gray-600 border-transparent'
}

// Status styling - theme aware
function statusClass(status) {
  if (!status) {
    return isDarkMode.value
      ? 'bg-gray-700/50 text-gray-400 border-transparent'
      : 'bg-gray-100 text-gray-600 border-transparent'
  }
  const s = String(status).toLowerCase()
  
  if (s === 'answered' || s === 'xfer_ok' || s === 'sched') {
    return isDarkMode.value
      ? 'bg-green-600/20 text-green-400 border-green-600/30'
      : 'bg-green-100 text-green-700 border-green-300'
  }
  if (s === 'abandoned' || s === 'missed' || s === 'no-answer' || s === 'noanswer' || s === 'busy' || s === 'xfer_noanswer' || s === 'xfer_offline') {
    return isDarkMode.value
      ? 'bg-amber-600/20 text-amber-400 border-amber-600/30'
      : 'bg-amber-100 text-amber-700 border-amber-300'
  }
  if (s === 'dump') {
    return isDarkMode.value
      ? 'bg-red-600/20 text-red-400 border-red-600/30'
      : 'bg-red-100 text-red-700 border-red-300'
  }
  if (s === 'ivr' || s === 'xfer_consult') {
    return isDarkMode.value
      ? 'bg-blue-600/20 text-blue-400 border-blue-600/30'
      : 'bg-blue-100 text-blue-700 border-blue-300'
  }
  if (s === 'voicemail') {
    return isDarkMode.value
      ? 'bg-green-600/20 text-green-400 border-green-600/30'
      : 'bg-green-100 text-green-700 border-green-300'
  }
  if (s === 'networkerror') {
    return isDarkMode.value
      ? 'bg-purple-600/20 text-purple-400 border-purple-600/30'
      : 'bg-purple-100 text-purple-700 border-purple-300'
  }
  if (s === 'reattempt') {
    return isDarkMode.value
      ? 'bg-cyan-600/20 text-cyan-400 border-cyan-600/30'
      : 'bg-cyan-100 text-cyan-700 border-cyan-300'
  }
  
  return isDarkMode.value
    ? 'bg-gray-700/50 text-gray-400 border-transparent'
    : 'bg-gray-100 text-gray-600 border-transparent'
}
</script>
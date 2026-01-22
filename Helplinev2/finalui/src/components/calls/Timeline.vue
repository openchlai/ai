<template>
  <div class="space-y-6">
    <div
      v-for="(group, label) in groupedCalls"
      :key="label"
      class="shadow-lg rounded-xl border overflow-hidden p-0"
      :class="isDarkMode 
        ? 'bg-neutral-900 border-transparent' 
        : 'bg-white border-transparent'"
    >
      <h2 
        class="text-base font-semibold p-4 border-b uppercase tracking-wide"
        :class="isDarkMode 
          ? 'text-amber-500 border-transparent bg-neutral-900' 
          : 'text-amber-700 border-transparent bg-gray-50/50'"
      >
        {{ label }}
      </h2>

      <div>
        <div
          v-for="(call, index) in group"
          :key="index"
          @click="handleSelect(call)"
          class="flex items-center gap-4 p-4 cursor-pointer transition-all duration-200 border-b last:border-b-0"
          :class="isDarkMode 
            ? 'hover:bg-gray-700/50 border-transparent' 
            : 'hover:bg-gray-50 border-transparent'"
        >
          <!-- Icon -->
          <div 
            class="w-10 h-10 flex items-center justify-center rounded-xl flex-shrink-0"
            :class="isDarkMode 
              ? 'text-amber-500 bg-gray-900' 
              : 'text-amber-700 bg-white border border-transparent'"
          >
            <i-mdi-phone class="w-6 h-6" />
          </div>

          <!-- Details -->
          <div class="flex-1">
            <div 
              class="font-medium text-sm"
              :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'"
            >
              Call ID: {{ call[callsStore.calls_k?.uniqueid?.[0]] || 'N/A' }}
            </div>

            <div 
              class="text-xs mt-1"
              :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
            >
              {{ formatDateTime(call[callsStore.calls_k?.dth?.[0]]) }}
            </div>

            <div 
              class="text-xs mt-1"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Agent:
              <span 
                class="font-medium"
                :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
              >
                {{ call[callsStore.calls_k?.user_name?.[0]] || 'Unknown' }}
              </span>
            </div>
          </div>

          <!-- QA Button -->
          <button 
            @click.stop="emitCreateQA(call)" 
            :disabled="!isAnswered(call)"
            :class="[
              'p-2 rounded-xl transition-all duration-200 flex-shrink-0',
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
        </div>
      </div>
    </div>

    <div 
      v-if="Object.keys(groupedCalls).length === 0" 
      class="text-center py-12 rounded-lg border"
      :class="isDarkMode 
        ? 'text-gray-500 bg-neutral-900 border-transparent' 
        : 'text-gray-500 bg-white border-transparent'"
    >
      No calls to show.
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits, inject } from 'vue'

// Inject theme
const isDarkMode = inject('isDarkMode')

const props = defineProps({
  groupedCalls: { type: Object, required: true },
  callsStore: { type: Object, required: true }
})

const emit = defineEmits(['select-call', 'create-qa'])

// Format timestamp to readable date and time (same as CallsTable)
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

// When user clicks a call, emit the call's unique id
function handleSelect(call) {
  const idIndex = props.callsStore.calls_k?.uniqueid?.[0]
  const id = idIndex !== undefined ? call[idIndex] : null
  if (id !== null) emit('select-call', id)
}

// Emit create-qa event with uniqueid
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
</script>
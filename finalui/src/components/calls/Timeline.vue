<template>
  <div class="space-y-6">
    <div
      v-for="(group, label) in groupedCalls"
      :key="label"
      class="bg-white shadow-sm rounded-lg p-4"
    >
      <h2 class="text-lg font-semibold text-amber-700 mb-3 border-b pb-2">
        {{ label }}
      </h2>

      <div class="space-y-3">
        <div
          v-for="(call, index) in group"
          :key="index"
          @click="handleSelect(call)"
          class="flex items-center gap-4 p-3 bg-amber-50 hover:bg-amber-100 rounded-lg shadow-sm cursor-pointer transition"
        >
          <!-- Icon -->
          <div class="text-amber-600 w-8 h-8 flex items-center justify-center">
            <svg viewBox="0 0 24 24" fill="none" class="w-6 h-6" xmlns="http://www.w3.org/2000/svg">
              <path d="M22 16.92V19C22 20.1046 21.1046 21 20 21C10.6112 21 3 13.3888 3 4C3 2.89543 3.89543 2 5 2H7.08C7.55607 2 7.95823 2.33718 8.02513 2.80754L8.7 7.5C8.76694 7.97036 8.53677 8.42989 8.12 8.67L6.5 9.5C7.84 12.16 11.84 16.16 14.5 17.5L15.33 15.88C15.5701 15.4632 16.0296 15.2331 16.5 15.3L21.1925 16.0249C21.6628 16.0918 22 16.4939 22 16.97V16.92Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>

          <!-- Details -->
          <div class="flex-1">
            <div class="font-medium text-gray-800">
              Call ID: {{ call[callsStore.calls_k?.uniqueid?.[0]] || 'N/A' }}
            </div>

            <div class="text-sm text-gray-500">
              {{
                call[callsStore.calls_k?.dth?.[0]]
                  ? new Date(call[callsStore.calls_k.dth[0]] * 1000).toLocaleString()
                  : 'N/A'
              }}
            </div>

            <div class="text-sm text-gray-600">
              Agent:
              <span class="font-medium text-amber-700">
                {{ call[callsStore.calls_k?.user_name?.[0]] || 'Unknown' }}
              </span>
            </div>
          </div>

          <!-- optional duration / meta -->
          <div class="text-sm text-gray-500">
            <!-- if you have duration seconds at index 'duration', replace accordingly -->
            <!-- Example: formatTime(call[callsStore.calls_k?.duration?.[0]]) -->
          </div>
        </div>
      </div>
    </div>

    <div v-if="Object.keys(groupedCalls).length === 0" class="text-center text-gray-500">
      No calls to show.
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  groupedCalls: { type: Object, required: true },
  callsStore: { type: Object, required: true },
});

const emit = defineEmits(['select-call']);

// When user clicks a call, emit the call's unique id (keep parent selectCall behavior)
function handleSelect(call) {
  const idIndex = props.callsStore.calls_k?.uniqueid?.[0];
  const id = idIndex !== undefined ? call[idIndex] : null;
  if (id !== null) emit('select-call', id);
}
</script>

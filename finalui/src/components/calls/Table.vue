<template>
  <div class="bg-white rounded-xl shadow overflow-auto">
    <table class="min-w-full text-sm text-left text-gray-600">
      <thead class="bg-amber-600 text-white">
        <tr>
          <th class="px-4 py-2">Call ID</th>
          <th class="px-4 py-2">Case ID</th>
          <th class="px-4 py-2">Date</th>
          <th class="px-4 py-2">Time</th>
          <th class="px-4 py-2">Status</th>
          <th class="px-4 py-2">Agent</th>
          <th class="px-4 py-2 text-center">Actions</th>
        </tr>
      </thead>

      <tbody>
        <tr
          v-for="(call, idx) in calls"
          :key="call[callsStore.calls_k?.uniqueid?.[0]] || idx"
          :class="[
            'hover:bg-amber-50 cursor-pointer transition',
            call[callsStore.calls_k?.uniqueid?.[0]] === selectedCallId ? 'bg-amber-100' : ''
          ]"
          @click="emitSelect(call)"
        >
          <td class="px-4 py-2 font-medium">
            #{{ call[callsStore.calls_k?.uniqueid?.[0]] || 'N/A' }}
          </td>

          <td class="px-4 py-2 text-amber-700">
            #{{ call[callsStore.calls_k?.has_case_id?.[0]] || 'N/A' }}
          </td>

          <td class="px-4 py-2">
            {{
              call[callsStore.calls_k?.dth?.[0]]
                ? new Date(call[callsStore.calls_k.dth[0]] * 1000).toLocaleDateString()
                : 'N/A'
            }}
          </td>

          <td class="px-4 py-2">
            {{
              call[callsStore.calls_k?.dth?.[0]]
                ? new Date(call[callsStore.calls_k.dth[0]] * 1000).toLocaleTimeString()
                : 'N/A'
            }}
          </td>

          <td class="px-4 py-2">
            <span :class="['px-2 py-1 rounded-full text-xs font-semibold', statusClass(call[callsStore.calls_k?.status?.[0]])]">
              {{ call[callsStore.calls_k?.status?.[0]] || 'Unknown' }}
            </span>
          </td>

          <td class="px-4 py-2" :class="{ 'text-gray-400 italic': !(call[callsStore.calls_k?.user_name?.[0]]) }">
            {{ call[callsStore.calls_k?.user_name?.[0]] || 'Unassigned' }}
          </td>

          <td class="px-4 py-2 text-center">
            <div class="flex items-center justify-center gap-2">
              <button @click.stop="emitViewDetails(call)" class="p-1.5 bg-gray-100 hover:bg-amber-100 rounded">
                <!-- eye icon -->
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M1 12S5 4 12 4s11 8 11 8-4 8-11 8S1 12 1 12z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/></svg>
              </button>

              <button @click.stop="emitLinkToCase(call)" class="p-1.5 bg-gray-100 hover:bg-amber-100 rounded">
                <!-- link icon -->
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M10 13C10.4295 13.5741 10.9774 14.0491 11.6066 14.3929C12.2357 14.7367 12.9315 14.9411 13.6467 14.9923C14.3618 15.0435 15.0796 14.9403 15.7513 14.6897C16.4231 14.4392 17.0331 14.047 17.54 13.54L20.54 10.54" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
              </button>

              <button @click.stop="emitViewCase(call)" class="p-1.5 bg-amber-600 text-white hover:bg-amber-700 rounded">
                <!-- doc icon -->
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2"/></svg>
              </button>
            </div>
          </td>
        </tr>
      </tbody>
    </table>

    <div v-if="!calls || calls.length === 0" class="p-4 text-center text-gray-500">
      No calls available.
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue';

const props = defineProps({
  calls: { type: Array, required: true },
  callsStore: { type: Object, required: true },
  selectedCallId: { type: [String, Number, null], default: null },
});

const emit = defineEmits(['select-call', 'view-call-details', 'link-to-case', 'view-case']);

function emitSelect(call) {
  const idIndex = props.callsStore.calls_k?.uniqueid?.[0];
  const id = idIndex !== undefined ? call[idIndex] : null;
  if (id !== null) emit('select-call', id);
}

function emitViewDetails(call) {
  const idIndex = props.callsStore.calls_k?.uniqueid?.[0];
  const id = idIndex !== undefined ? call[idIndex] : null;
  if (id !== null) emit('view-call-details', id);
}

function emitLinkToCase(call) {
  const idIndex = props.callsStore.calls_k?.uniqueid?.[0];
  const id = idIndex !== undefined ? call[idIndex] : null;
  if (id !== null) emit('link-to-case', id);
}

function emitViewCase(call) {
  const caseIndex = props.callsStore.calls_k?.case_id?.[0];
  const cid = caseIndex !== undefined ? call[caseIndex] : null;
  if (cid !== null) emit('view-case', cid);
}

// Small helper to map status -> Tailwind classes (adjust to your real statuses)
function statusClass(status) {
  if (!status) return 'bg-gray-100 text-gray-700';
  const s = String(status).toLowerCase();
  if (s.includes('completed') || s.includes('answered') || s.includes('resolved')) return 'bg-green-100 text-green-800';
  if (s.includes('missed') || s.includes('failed') || s.includes('abandoned')) return 'bg-red-100 text-red-800';
  if (s.includes('pending') || s.includes('ivr') || s.includes('queued')) return 'bg-amber-100 text-amber-800';
  return 'bg-gray-100 text-gray-700';
}
</script>

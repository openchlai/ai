<template>
  <div class="p-6 space-y-6">
    <!-- View Toggle Buttons -->
    <div class="flex justify-end space-x-3">
      <button
        @click="activeView = 'timeline'"
        :class="[
          'px-4 py-2 rounded-lg font-semibold text-white transition-colors duration-200',
          activeView === 'timeline' ? 'bg-amber-700' : 'bg-amber-400 hover:bg-amber-500'
        ]"
      >
        Timeline View
      </button>

      <button
        @click="activeView = 'table'"
        :class="[
          'px-4 py-2 rounded-lg font-semibold text-white transition-colors duration-200',
          activeView === 'table' ? 'bg-amber-700' : 'bg-amber-400 hover:bg-amber-500'
        ]"
      >
        Table View
      </button>
    </div>

    <!-- Timeline view -->
    <div v-if="activeView === 'timeline'">
      <Timeline
        :grouped-calls="groupedCalls"
        :calls-store="callsStore"
        @select-call="selectCall"
      />
    </div>

    <!-- Table view -->
    <div v-if="activeView === 'table'">
      <Table
        :calls="callsStore.calls"
        :calls-store="callsStore"
        :selected-call-id="selectedCallId"
        @select-call="selectCall"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import Timeline from "@/components/calls/Timeline.vue";
import Table from "@/components/calls/Table.vue";
import { useCallStore } from "@/stores/calls"; // <-- correct store import

const callsStore = useCallStore();
const activeView = ref("timeline");
const selectedCallId = ref(null);

// Fetch calls on mount
onMounted(async () => {
  try {
    console.log("Fetching calls...");
    await callsStore.listCalls(); // keep your existing store method
    console.log("Calls fetched:", callsStore.calls);
  } catch (err) {
    console.error("Error fetching calls:", err);
  }
});

// parent-level select handler (child components emit callId)
function selectCall(callId) {
  selectedCallId.value = callId;
}

// Group calls by date (uses your store's calls and calls_k indexes)
const groupedCalls = computed(() => {
  const groups = {};
  if (!callsStore.calls || !Array.isArray(callsStore.calls)) return groups;

  const tsIndex = callsStore.calls_k?.dth?.[0];
  if (tsIndex === undefined) return groups;

  callsStore.calls.forEach((call) => {
    const ts = call[tsIndex];
    const dateLabel = ts ? new Date(ts * 1000).toLocaleDateString() : "Unknown";

    if (!groups[dateLabel]) groups[dateLabel] = [];
    groups[dateLabel].push(call);
  });

  // optional: sort groups by newest date first
  const sorted = Object.keys(groups)
    .sort((a, b) => new Date(b) - new Date(a))
    .reduce((acc, k) => {
      acc[k] = groups[k];
      return acc;
    }, {});

  return sorted;
});
</script>

<!-- src/views/CallsView.vue -->
<script setup>
import { ref, onMounted } from 'vue';
import { useCallStore } from '@/stores/calls';

const callStore = useCallStore();
const pivotData = ref([]);
const pivotColumns = ref([]);

// Filters
const filters = ref({
  _a: '',
  _c: 20,
  field: '',
  value: ''
});

// Fetch initial calls on mount
onMounted(() => {
  callStore.listCalls({ _c: filters.value._c });
});

// Apply filters to main table
const applyFilters = async () => {
  const params = {
    _a: filters.value._a,
    _c: filters.value._c
  };

  if (filters.value.field && filters.value.value) {
    params[filters.value.field] = filters.value.value;
  }

  await callStore.listCalls(params);
};

// View call details
const handleViewCall = async (uniqueid) => {
  try {
    const details = await callStore.viewCall(uniqueid);
    alert(JSON.stringify(details, null, 2));
  } catch (err) {
    console.error('Failed to view call:', err.message);
  }
};

// Download single call recording
const handleDownloadRecording = async (uniqueid) => {
  try {
    const blob = await callStore.downloadCallRecording(uniqueid, 'wav');
    const url = window.URL.createObjectURL(new Blob([blob], { type: 'audio/wav' }));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${uniqueid}.wav`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    console.error('Download failed:', err.message);
  }
};

// Download CSV with filters
const handleDownloadCSV = async () => {
  try {
    const params = { _a: filters.value._a, _c: filters.value._c };
    if (filters.value.field && filters.value.value) {
      params[filters.value.field] = filters.value.value;
    }

    const blob = await callStore.downloadCSV(params);
    const url = window.URL.createObjectURL(new Blob([blob], { type: 'text/csv' }));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'calls.csv');
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    console.error('CSV Download failed:', err.message);
  }
};

// Get pivot report with filters
const handlePivotReport = async () => {
  try {
    const params = { _a: filters.value._a, _c: filters.value._c };
    if (filters.value.field && filters.value.value) {
      params[filters.value.field] = filters.value.value;
    }

    const data = await callStore.getPivotReport({
      ...params,
      xaxis: 'usr',
      yaxis: 'hangup_status'
    });

    if (Array.isArray(data) && data.length > 0) {
      pivotColumns.value = Object.keys(data[0]);
      pivotData.value = data;
    } else {
      pivotColumns.value = [];
      pivotData.value = [];
    }
  } catch (err) {
    console.error('Pivot report fetch failed:', err.message);
  }
};
</script>

<template>
  <section class="calls-view">
    <h2>Calls List</h2>

    <!-- Filters -->
    <div class="filters">
      <input v-model="filters._a" placeholder="Start position (_a)" />
      <input v-model.number="filters._c" type="number" placeholder="Max records (_c)" />
      <input v-model="filters.field" placeholder="Filter field (e.g. hangup_status)" />
      <input v-model="filters.value" placeholder="Filter value (e.g. answered)" />
      <button @click="applyFilters">Apply Filters</button>
      <button @click="handleDownloadCSV">Download CSV</button>
      <button @click="handlePivotReport">Get Pivot Report</button>
    </div>

    <p v-if="callStore.loading">Loading…</p>
    <p v-else-if="callStore.error" class="error">{{ callStore.error }}</p>

    <div v-else>
      <h3>Total Calls: {{ callStore.callCount }}</h3>

      <!-- Calls Table -->
      <table v-if="callStore.callCount">
        <thead>
          <tr>
            <th v-for="(meta, key) in callStore.calls_k" :key="key">
              {{ meta[3] || key }}
            </th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="call in callStore.calls" :key="call[0]">
            <td v-for="(meta, key) in callStore.calls_k" :key="key">
              {{ call[parseInt(meta[0])] }}
            </td>
            <td>
              <button @click="handleViewCall(call[0])">View</button>
              <button @click="handleDownloadRecording(call[0])">
                Download Recording
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else>
        <p>No calls available.</p>
      </div>

      <!-- Pivot Table -->
      <div v-if="pivotData.length" class="pivot-section">
        <h3>Pivot Report</h3>
        <table>
          <thead>
            <tr>
              <th v-for="col in pivotColumns" :key="col">{{ col }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in pivotData" :key="idx">
              <td v-for="col in pivotColumns" :key="col">{{ row[col] }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<style scoped>
.calls-view {
  padding: 1rem;
  overflow-x: auto;
}

.filters {
  margin-bottom: 1rem;
}

.filters input {
  margin-right: 0.5rem;
  padding: 4px 8px;
}

.filters button {
  margin-right: 0.5rem;
  padding: 4px 8px;
  cursor: pointer;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
}

.filters button:hover {
  background: #45a049;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
  font-size: 14px;
}

th, td {
  border: 1px solid #ccc;
  padding: 6px 8px;
  text-align: left;
}

button {
  margin-right: 5px;
  padding: 4px 8px;
  cursor: pointer;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
}

button:hover {
  background: #45a049;
}

.error {
  color: #e74c3c;
}
</style>


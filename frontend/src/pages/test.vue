<!-- src/views/CasesView.vue -->
<script setup>
import { ref, onMounted } from 'vue';
import { useCaseStore } from '@/stores/cases';

const caseStore = useCaseStore();

// Filters for listing, CSV and pivot
const filters = ref({
  _a: '',
  _c: 20,
  category_main: '',
  status: ''
});

// Pivot data
const pivotData = ref([]);
const pivotColumns = ref([]);

onMounted(() => {
  caseStore.listCases({ _c: filters.value._c });
});

// Download CSV handler
const handleDownloadCSV = async () => {
  try {
    const blob = await caseStore.downloadCSV({ 
      _a: filters.value._a,
      _c: filters.value._c,
      category_main: filters.value.category_main,
      status: filters.value.status
    });
    const url = window.URL.createObjectURL(new Blob([blob], { type: 'text/csv' }));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'cases.csv');
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    console.error('CSV Download failed:', err.message);
  }
};

// Pivot report handler
const handlePivotReport = async () => {
  try {
    const data = await caseStore.getPivotReport({
      _a: filters.value._a,
      _c: filters.value._c,
      category_main: filters.value.category_main,
      status: filters.value.status,
      xaxis: 'status',
      yaxis: 'priority'
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
  <section class="cases-view">
    <h2>Cases List</h2>

    <!-- Filters -->
    <div class="filters">
      <input v-model="filters._a" placeholder="Start (_a)" />
      <input v-model.number="filters._c" type="number" placeholder="Count (_c)" />
      <input v-model="filters.category_main" placeholder="Category Main" />
      <input v-model="filters.status" placeholder="Status" />
      <button @click="caseStore.listCases(filters)">Refresh List</button>
      <button @click="handleDownloadCSV">Download CSV</button>
      <button @click="handlePivotReport">Get Pivot Report</button>
    </div>

    <p v-if="caseStore.loading">Loading…</p>
    <p v-else-if="caseStore.error" class="error">{{ caseStore.error }}</p>

    <div v-else>
      <h3>Total Cases: {{ caseStore.caseCount }}</h3>

      <!-- Case Table -->
      <table v-if="caseStore.caseCount">
        <thead>
          <tr>
            <th v-for="(meta, key) in caseStore.cases_k" :key="key">
              {{ meta[3] || key }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in caseStore.cases" :key="item[0]">
            <td v-for="(meta, key) in caseStore.cases_k" :key="key">
              {{ item[parseInt(meta[0])] }}
            </td>
          </tr>
        </tbody>
      </table>

      <div v-else>
        <p>No cases available.</p>
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
.cases-view {
  padding: 1rem;
  overflow-x: auto;
}

.filters {
  margin-bottom: 1rem;
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

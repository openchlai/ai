<template>
  <div>
    <SidePanel
      :userRole="userRole"
      :isInQueue="isInQueue"
      :isProcessingQueue="isProcessingQueue"
      :currentCall="currentCall"
      @toggle-queue="handleQueueToggle"
      @logout="handleLogout"
      @sidebar-toggle="handleSidebarToggle"
    />

    <div class="main-content">
    <div class="header">
      <h1>Reports</h1>
      <div class="actions">
        <button class="action-btn" @click="refreshCalls" :disabled="loading">Refresh</button>
        <button class="action-btn" @click="downloadCallsCSV" :disabled="loading || callCount === 0">Download CSV</button>
        <button class="action-btn" @click="fetchPivot" :disabled="loading">Fetch Pivot</button>
      </div>
    </div>

    <div class="filters glass-card fine-border">
      <div class="filter-row">
        <div class="filter-item">
          <label for="from">From</label>
          <input id="from" type="date" v-model="from" />
        </div>
        <div class="filter-item">
          <label for="to">To</label>
          <input id="to" type="date" v-model="to" />
        </div>
        <div class="filter-item">
          <label for="search">Search</label>
          <input id="search" type="text" placeholder="Filter text (optional)" v-model="q" />
        </div>
        <div class="filter-item">
          <label>&nbsp;</label>
          <button class="apply-btn" @click="applyFilters" :disabled="loading">Apply</button>
        </div>
      </div>
    </div>

    <div class="kpis">
      <div class="kpi glass-card fine-border">
        <div class="kpi-label">Total Calls</div>
        <div class="kpi-value">{{ callCount }}</div>
      </div>
      <div class="kpi glass-card fine-border">
        <div class="kpi-label">Errors</div>
        <div class="kpi-value">{{ error ? 1 : 0 }}</div>
      </div>
    </div>

    <div class="content">
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading call data…</p>
      </div>
      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
      </div>
      <div v-else>
        <table class="table">
          <thead>
            <tr>
              <th>#</th>
              <th>Date/Time</th>
              <th>Unique ID</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, idx) in previewRows" :key="idx">
              <td>{{ idx + 1 }}</td>
              <td>{{ row.readableDate }}</td>
              <td>{{ extractUniqueId(row) }}</td>
            </tr>
          </tbody>
        </table>
        <div class="hint" v-if="previewRows.length === 0">No rows to display. Adjust filters or refresh.</div>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useCallStore } from '@/stores/calls'
import SidePanel from '@/components/SidePanel.vue'

const callStore = useCallStore()
const { loading, error, formattedCalls, calls_k } = storeToRefs(callStore)

const from = ref('')
const to = ref('')
const q = ref('')

const callCount = computed(() => callStore.callCount)
const previewRows = computed(() => formattedCalls.value.slice(0, 25))

function extractUniqueId(row) {
  const index = parseInt(calls_k.value?.uniqueid?.[0] ?? -1)
  return index >= 0 ? row[index] : ''
}

async function refreshCalls() {
  const params = {}
  if (from.value) params.from = from.value
  if (to.value) params.to = to.value
  if (q.value) params.q = q.value
  await callStore.listCalls(params)
}

async function applyFilters() {
  await refreshCalls()
}

async function downloadCallsCSV() {
  try {
    const blob = await callStore.downloadCSV({ from: from.value || undefined, to: to.value || undefined, q: q.value || undefined })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'calls.csv'
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  } catch (err) {
    console.error('CSV download failed:', err)
  }
}

async function fetchPivot() {
  try {
    const data = await callStore.getPivotReport({ from: from.value || undefined, to: to.value || undefined })
    console.log('Pivot report:', data)
    alert('Pivot report fetched. Check console for details.')
  } catch (err) {
    console.error('Pivot fetch failed:', err)
  }
}

onMounted(() => {
  refreshCalls()
})

// SidePanel integration - minimal local state and handlers
const userRole = ref('user')
const isInQueue = ref(false)
const isProcessingQueue = ref(false)
const currentCall = ref(null)

function handleQueueToggle() {
  if (isProcessingQueue.value) return
  isInQueue.value = !isInQueue.value
}
function handleLogout() {
  console.log('Logging out...')
}
function handleSidebarToggle(_) {}
</script>

<style scoped>
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.actions {
  display: flex;
  gap: 10px;
}
.action-btn, .apply-btn {
  padding: 8px 14px;
  border-radius: 8px;
  border: none;
  background: var(--accent-color);
  color: #fff;
  cursor: pointer;
}
.filters {
  background: var(--content-bg);
  padding: 12px;
  border-radius: 12px;
  margin-bottom: 16px;
}
.filter-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}
.filter-item label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
}
.filter-item input, .filter-item select {
  width: 100%;
  padding: 8px 10px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  background: var(--input-bg);
  color: var(--text-color);
}
.kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}
.kpi {
  background: var(--content-bg);
  border-radius: 12px;
  padding: 16px;
}
.kpi-label { color: var(--text-secondary); font-size: 12px; }
.kpi-value { font-size: 22px; font-weight: 700; }
.content {
  background: var(--content-bg);
  color: var(--text-color);
  border-radius: 12px;
  padding: 0;
  overflow: hidden;
}
.table { width: 100%; border-collapse: collapse; }
.table th, .table td { padding: 12px 16px; border-bottom: 1px solid var(--border-color); text-align: left; }
.table thead th { background: var(--sidebar-bg); }
.hint { padding: 16px; color: var(--text-secondary); }
.loading-state { padding: 40px; display: flex; gap: 12px; align-items: center; }
.spinner {
  border: 4px solid var(--border-color);
  border-top: 4px solid var(--accent-color);
  border-radius: 50%;
  width: 28px;
  height: 28px;
  animation: spin 1s linear infinite;
}
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
</style>


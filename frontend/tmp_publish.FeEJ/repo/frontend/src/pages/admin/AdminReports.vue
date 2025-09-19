<template>
  <div class="main-scroll-content">
    <!-- Reports Grid -->
    <div class="reports-grid">
      <div class="report-card glass-card fine-border">
        <div class="card-header">
          <div class="section-title">Case Statistics</div>
          <select class="time-filter" v-model="selectedTimeRange">
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
          </select>
        </div>
        <div class="report-content">
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ totalCases }}</div>
              <div class="stat-label">Total Cases</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ resolvedCases }}</div>
              <div class="stat-label">Resolved</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ avgResolutionTime }}</div>
              <div class="stat-label">Avg. Resolution (days)</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ resolutionRate }}%</div>
              <div class="stat-label">Resolution Rate</div>
            </div>
          </div>
        </div>
      </div>

      <div class="report-card glass-card fine-border">
        <div class="card-header">
          <div class="section-title">Team Performance</div>
          <button class="generate-btn" @click="generateReport('performance')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14,2 14,8 20,8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10,9 9,9 8,9"></polyline>
            </svg>
            Generate Report
          </button>
        </div>
        <div class="report-content">
          <div class="performance-list">
            <div
              v-for="member in teamMembers"
              :key="member.id"
              class="performance-item"
            >
              <div class="member-info">
                <div class="member-avatar">
                  {{ getInitials(member.name) }}
                </div>
                <div class="member-details">
                  <div class="member-name">{{ member.name }}</div>
                  <div class="member-role">{{ member.role }}</div>
                </div>
              </div>
              <div class="performance-stats">
                <div class="stat">
                  <div class="stat-value">{{ member.casesAssigned }}</div>
                  <div class="stat-label">Cases</div>
                </div>
                <div class="stat">
                  <div class="stat-value">{{ member.resolutionRate || 85 }}%</div>
                  <div class="stat-label">Success Rate</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Section -->
    <div class="charts-section">
      <div class="chart-card glass-card fine-border">
        <div class="card-header">
          <div class="section-title">Case Trends</div>
          <select class="time-filter" v-model="selectedChartPeriod">
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
            <option value="90">Last 90 days</option>
          </select>
        </div>
        <div class="trend-chart">
          <div class="trend-line"></div>
          <div class="chart-points">
            <div
              v-for="(point, index) in chartPoints"
              :key="index"
              class="chart-point"
              :style="{ left: point.x + '%', top: point.y + '%' }"
            ></div>
          </div>
        </div>
      </div>

      <div class="chart-card glass-card fine-border">
        <div class="card-header">
          <div class="section-title">Case Categories Distribution</div>
        </div>
        <div class="chart-container">
          <div class="chart-placeholder">
            <div class="chart-bars">
              <div
                v-for="(bar, index) in categoryData"
                :key="index"
                class="chart-bar"
                :style="{ height: bar.percentage + '%', backgroundColor: bar.color }"
                :title="`${bar.name}: ${bar.percentage}%`"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useCaseStore } from '../../stores/cases'
import { useUserStore } from '../../stores/users'

const caseStore = useCaseStore()
const userStore = useUserStore()

// Reactive data
const selectedTimeRange = ref(30)
const selectedChartPeriod = ref(30)

// Chart data
const chartPoints = ref([
  { x: 10, y: 60 },
  { x: 25, y: 45 },
  { x: 40, y: 70 },
  { x: 55, y: 55 },
  { x: 70, y: 80 },
  { x: 85, y: 65 }
])

const categoryData = ref([
  { name: 'Child Protection', percentage: 35, color: '#FF6B6B' },
  { name: 'Family Support', percentage: 25, color: '#4ECDC4' },
  { name: 'Education', percentage: 20, color: '#45B7D1' },
  { name: 'Health', percentage: 15, color: '#96CEB4' },
  { name: 'Legal', percentage: 5, color: '#FFEAA7' }
])

// Computed properties
const totalCases = computed(() => caseStore.cases.length)
const resolvedCases = computed(() => caseStore.cases.filter(c => c.status === 'Resolved').length)
const avgResolutionTime = computed(() => {
  const resolvedCases = caseStore.cases.filter(c => c.status === 'Resolved')
  if (resolvedCases.length === 0) return 0
  // Mock calculation - in real app, you'd calculate actual resolution times
  return Math.round(resolvedCases.length * 2.5)
})
const resolutionRate = computed(() => {
  return totalCases.value > 0 ? Math.round((resolvedCases.value / totalCases.value) * 100) : 0
})

const teamMembers = computed(() => userStore.users)

// Methods
const generateReport = (type) => {
  console.log('Generate report:', type)
  alert(`Generating ${type} report...`)
}

const getInitials = (name) => {
  if (!name || typeof name !== 'string') return ''
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
}

onMounted(async () => {
  await caseStore.listCases()
  await userStore.listUsers()
})
</script>

<style scoped>
/* Reports & Analytics specific styles are inherited from global components.css */
</style>

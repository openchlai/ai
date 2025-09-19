<template>
  <div class="main-scroll-content">
    <!-- Dashboard Grid -->
    <div class="dashboard-grid">
      <div class="dashboard-card glass-card fine-border">
        <div class="card-header">
          <div class="card-title">Total Cases</div>
          <div class="card-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14,2 14,8 20,8"></polyline>
              <line x1="16" y1="13" x2="8" y2="13"></line>
              <line x1="16" y1="17" x2="8" y2="17"></line>
              <polyline points="10,9 9,9 8,9"></polyline>
            </svg>
          </div>
        </div>
        <div class="card-value">{{ totalCases }}</div>
        <div class="card-subtitle">Total cases in system</div>
        <div class="card-trend positive">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="22,12 18,12 15,21 9,3 6,12 2,12"></polyline>
          </svg>
          +12% this month
        </div>
      </div>

      <div class="dashboard-card glass-card fine-border">
        <div class="card-header">
          <div class="card-title">Active Cases</div>
          <div class="card-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12,6 12,12 16,14"></polyline>
            </svg>
          </div>
        </div>
        <div class="card-value">{{ activeCases }}</div>
        <div class="card-subtitle">Currently being processed</div>
        <div class="card-trend neutral">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          No change
        </div>
      </div>

      <div class="dashboard-card glass-card fine-border">
        <div class="card-header">
          <div class="card-title">Team Members</div>
          <div class="card-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="9" cy="7" r="4"></circle>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
            </svg>
          </div>
        </div>
        <div class="card-value">{{ activeTeamMembers }}</div>
        <div class="card-subtitle">Active team members</div>
        <div class="card-trend positive">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="22,12 18,12 15,21 9,3 6,12 2,12"></polyline>
          </svg>
          +2 new members
        </div>
      </div>

      <div class="dashboard-card glass-card fine-border">
        <div class="card-header">
          <div class="card-title">Resolution Rate</div>
          <div class="card-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
              <polyline points="22,4 12,14.01 9,11.01"></polyline>
            </svg>
          </div>
        </div>
        <div class="card-value">{{ resolutionRate }}%</div>
        <div class="card-subtitle">Cases resolved this month</div>
        <div class="card-trend positive">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="22,12 18,12 15,21 9,3 6,12 2,12"></polyline>
          </svg>
          +5% improvement
        </div>
      </div>
    </div>

    <!-- Dashboard Content Grid -->
    <div class="dashboard-content-grid">
      <!-- Quick Actions Card -->
      <div class="quick-actions-card glass-card fine-border">
        <div class="section-title">Quick Actions</div>
        <div class="quick-actions-list">
          <button class="quick-action-btn" @click="navigateTo('/admin/cases')">
            <div class="action-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
            </div>
            Create New Case
          </button>
          <button class="quick-action-btn" @click="navigateTo('/admin/users')">
            <div class="action-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                <circle cx="8.5" cy="7" r="4"></circle>
                <line x1="20" y1="8" x2="20" y2="14"></line>
                <line x1="23" y1="11" x2="17" y2="11"></line>
              </svg>
            </div>
            Invite Team Member
          </button>
          <button class="quick-action-btn" @click="generateReport('monthly')">
            <div class="action-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14,2 14,8 20,8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <polyline points="10,9 9,9 8,9"></polyline>
              </svg>
            </div>
            Generate Report
          </button>
          <button class="quick-action-btn" @click="navigateTo('/admin/ai-assistant')">
            <div class="action-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
              </svg>
            </div>
            AI Assistant
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useCaseStore } from '../../stores/cases'
import { useUserStore } from '../../stores/users'

const router = useRouter()
const caseStore = useCaseStore()
const userStore = useUserStore()

// Reactive data
const selectedTimeRange = ref(30)
const miniBarsData = ref([65, 78, 45, 89, 92, 76, 84])

// Computed properties
const totalCases = computed(() => caseStore.cases.length)
const activeCases = computed(() => caseStore.cases.filter(c => c.status === 'Open' || c.status === 'In Progress').length)
const teamMembers = computed(() => userStore.users)
const activeTeamMembers = computed(() => userStore.users.filter(u => u.status === 'Active').length)
const resolutionRate = computed(() => {
  const resolvedCases = caseStore.cases.filter(c => c.status === 'Resolved').length
  return totalCases.value > 0 ? Math.round((resolvedCases / totalCases.value) * 100) : 0
})
const recentCases = computed(() => caseStore.cases.slice(0, 5))

// Methods
const navigateTo = (path) => {
  router.push(path)
}

const viewCase = (caseId) => {
  router.push(`/admin/cases/${caseId}`)
}

const generateReport = (type) => {
  console.log('Generate report:', type)
  alert(`Generating ${type} report...`)
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}

// Status helpers (match main Dashboard)
const statusMap = {
  0: { label: 'None', color: '#ffffff' },
  1: { label: 'Ongoing', color: '#8B4513' },
  2: { label: 'Closed', color: '#4eb151' },
  3: { label: 'Escalated', color: '#ff0000' }
}

function getStatusLabel(statusCode) {
  const status = statusMap[Number(statusCode)]
  return status ? status.label : 'Unknown'
}

function getStatusColor(statusCode) {
  const status = statusMap[Number(statusCode)]
  return status ? status.color : '#ccc'
}

onMounted(async () => {
  await caseStore.listCases()
  await userStore.listUsers()
})
</script>

<style scoped>
/* Dashboard specific styles are inherited from global components.css */
</style>

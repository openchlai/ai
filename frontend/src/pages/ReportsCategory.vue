<template>
  <div>
    <!-- SidePanel Component -->
    <SidePanel
      :userRole="userRole"
      :isInQueue="isInQueue"
      :isProcessingQueue="isProcessingQueue"
      :currentCall="currentCall"
      @toggle-queue="handleQueueToggle"
      @logout="handleLogout"
      @sidebar-toggle="handleSidebarToggle"
    />

    <!-- Main Content -->
    <div class="main-content">
      <div class="page-container">
        <!-- Header -->
        <div class="header">
          <div class="header-content">
            <div class="title-section">
              <h1>{{ pageTitle }}</h1>
              <p>{{ pageDescription }}</p>
            </div>
            <div class="header-actions">
              <button class="back-btn" @click="goBack">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="M19 12H5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Back to Reports
              </button>
              <div class="download-dropdown">
                <button class="action-btn primary dropdown-toggle" @click="toggleDownloadMenu">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M21 15V19C21 19.5304 20.7893 20.0391 20.4142 20.4142C20.0391 20.7893 19.5304 21 19 21H5C4.46957 21 3.96086 20.7893 3.58579 20.4142C3.21071 20.0391 3 19.5304 3 19V15" stroke="currentColor" stroke-width="2"/>
                    <path d="M7 10L12 15L17 10" stroke="currentColor" stroke-width="2"/>
                    <path d="M12 15V3" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  Download
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" class="dropdown-arrow">
                    <path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="2"/>
                  </svg>
                </button>
                <div class="dropdown-menu" v-if="showDownloadMenu">
                  <button class="dropdown-item" @click="downloadReport('csv')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2"/>
                      <path d="M14 2V8H20" stroke="currentColor" stroke-width="2"/>
                      <path d="M16 13H8" stroke="currentColor" stroke-width="2"/>
                      <path d="M16 17H8" stroke="currentColor" stroke-width="2"/>
                      <path d="M10 9H8" stroke="currentColor" stroke-width="2"/>
                    </svg>
                    Download as CSV
                  </button>
                  <button class="dropdown-item" @click="downloadReport('excel')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2"/>
                      <path d="M14 2V8H20" stroke="currentColor" stroke-width="2"/>
                      <path d="M16 13H8" stroke="currentColor" stroke-width="2"/>
                      <path d="M16 17H8" stroke="currentColor" stroke-width="2"/>
                      <path d="M10 9H8" stroke="currentColor" stroke-width="2"/>
                    </svg>
                    Download as Excel
                  </button>
                  <button class="dropdown-item" @click="downloadReport('pdf')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2"/>
                      <path d="M14 2V8H20" stroke="currentColor" stroke-width="2"/>
                      <path d="M16 13H8" stroke="currentColor" stroke-width="2"/>
                      <path d="M16 17H8" stroke="currentColor" stroke-width="2"/>
                      <path d="M10 9H8" stroke="currentColor" stroke-width="2"/>
                    </svg>
                    Download as PDF
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- KPIs Cards -->
        <div class="kpis-section">
          <div class="kpi-card">
            <div class="kpi-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2"/>
                <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2"/>
                <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div class="kpi-content">
              <div class="kpi-value">{{ totalCount }}</div>
              <div class="kpi-label">Total {{ categoryName }}</div>
            </div>
          </div>
          <div class="kpi-card">
            <div class="kpi-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M12 2V22" stroke="currentColor" stroke-width="2"/>
                <path d="M17 5H9.5C8.57174 5 7.6815 5.36875 7.02513 6.02513C6.36875 6.6815 6 7.57174 6 8.5C6 9.42826 6.36875 10.3185 7.02513 10.9749C7.6815 11.6313 8.57174 12 9.5 12H14.5C15.4283 12 16.3185 12.3687 16.9749 13.0251C17.6313 13.6815 18 14.5717 18 15.5C18 16.4283 17.6313 17.3185 16.9749 17.9749C16.3185 18.6313 15.4283 19 14.5 19H6" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div class="kpi-content">
              <div class="kpi-value">{{ averageMetric }}</div>
              <div class="kpi-label">Average</div>
            </div>
          </div>
          <div class="kpi-card">
            <div class="kpi-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
            <div class="kpi-content">
              <div class="kpi-value">{{ successRate }}%</div>
              <div class="kpi-label">Success Rate</div>
            </div>
          </div>
        </div>

        <!-- Search and Filters -->
        <div class="controls-section">
          <div class="controls-row">
            <div class="search-container">
              <input 
                type="text" 
                placeholder="Search {{ categoryName.toLowerCase() }}..." 
                v-model="searchQuery"
                class="search-input"
              />
            </div>
            <div class="filter-buttons">
              <button 
                class="filter-btn" 
                :class="{ active: activeFilter === 'all' }"
                @click="setActiveFilter('all')"
              >
                All
              </button>
              <button 
                class="filter-btn" 
                :class="{ active: activeFilter === 'today' }"
                @click="setActiveFilter('today')"
              >
                Today
              </button>
              <button 
                class="filter-btn" 
                :class="{ active: activeFilter === 'week' }"
                @click="setActiveFilter('week')"
              >
                This Week
              </button>
              <button 
                class="filter-btn" 
                :class="{ active: activeFilter === 'month' }"
                @click="setActiveFilter('month')"
              >
                This Month
              </button>
              <button 
                class="filter-btn" 
                :class="{ active: activeFilter === 'date-range' }"
                @click="setActiveFilter('date-range')"
              >
                Date Range
              </button>
            </div>
          </div>
        </div>

        <!-- Date Range Filters (Conditional) -->
        <div v-if="activeFilter === 'date-range'" class="date-range-section">
          <div class="date-range-card">
            <div class="date-inputs">
              <div class="date-input-group">
                <label for="from">From Date</label>
                <input id="from" type="date" v-model="fromDate" />
              </div>
              <div class="date-input-group">
                <label for="to">To Date</label>
                <input id="to" type="date" v-model="toDate" />
              </div>
              <div class="date-input-group">
                <label>&nbsp;</label>
                <button class="apply-btn" @click="applyFilters" :disabled="loading">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M21 21L16.514 16.506L21 21ZM19 10.5C19 15.194 15.194 19 10.5 19C5.806 19 2 15.194 2 10.5C2 5.806 5.806 2 10.5 2C15.194 2 19 5.806 19 10.5Z" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  Apply Filters
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Content -->
        <div class="content-section">
          <div class="content-header">
            <h2>{{ categoryName }} Data</h2>
            <div class="content-actions">
              <div class="view-toggle">
                <button class="filter-btn" :class="{ active: viewMode === 'table' }" @click="viewMode = 'table'">Table</button>
                <button class="filter-btn" :class="{ active: viewMode === 'graph' }" @click="viewMode = 'graph'">Graph</button>
              </div>
              <button class="action-btn" @click="refreshData" :disabled="loading">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M1 4V10H7" stroke="currentColor" stroke-width="2"/>
                  <path d="M23 20V14H17" stroke="currentColor" stroke-width="2"/>
                  <path d="M20.49 9C19.2214 7.33122 17.4547 6.08128 15.3778 5.43313C13.3008 4.78497 11.0167 4.7729 8.93142 5.39824C6.84616 6.02358 5.06075 7.25792 3.76476 8.91151C2.46877 10.5651 1.71538 12.5609 1.587 14.6583C1.45862 16.7557 1.96021 18.8529 3.02871 20.6467C4.09721 22.4405 5.68649 23.8458 7.57151 24.6693C9.45653 25.4928 11.5537 25.6975 13.5829 25.2578C15.6121 24.8181 17.4856 23.7508 18.976 22.176L23 18" stroke="currentColor" stroke-width="2"/>
                </svg>
                Refresh
              </button>
            </div>
          </div>

          <!-- Graph View -->
          <div v-if="viewMode === 'graph'" class="graph-view">
            <div class="graph-row">
              <div class="graph-card">
                <h3>Distribution</h3>
                <svg viewBox="0 0 42 42" class="donut">
                  <circle class="donut-ring" cx="21" cy="21" r="15.915" fill="transparent" stroke="#eee" stroke-width="3"></circle>
                  <circle class="donut-segment a" cx="21" cy="21" r="15.915" fill="transparent" :stroke-dasharray="successRate + ' ' + (100-successRate)" stroke="#2E7D32" stroke-width="3" stroke-dashoffset="25"></circle>
                  <text x="21" y="21" text-anchor="middle" dominant-baseline="middle" class="chart-center">{{ successRate }}%</text>
                </svg>
              </div>
              <div class="graph-card">
                <h3>Trend</h3>
                <svg viewBox="0 0 300 120" class="line">
                  <polyline :points="trendPoints" fill="none" stroke="#1E88E5" stroke-width="3" />
                </svg>
              </div>
            </div>
          </div>

          <!-- Table View -->
          <div v-else class="data-table">
            <div v-if="loading" class="loading-state">
              <div class="spinner"></div>
              <p>Loading {{ categoryName }} data...</p>
            </div>
            <div v-else-if="error" class="error-state">
              <p>{{ error }}</p>
            </div>
            <div v-else>
              <table class="table">
                <thead>
                  <tr>
                    <th v-for="header in tableHeaders" :key="header">{{ header }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in tableData" :key="index">
                    <td v-for="header in tableHeaders" :key="header">{{ row[header] || '-' }}</td>
                  </tr>
                </tbody>
              </table>
              <div v-if="tableData.length === 0" class="empty-state">
                <p>No {{ categoryName }} data found. Try adjusting your filters.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SidePanel from '@/components/SidePanel.vue'

const route = useRoute()
const router = useRouter()

// SidePanel props and state
const userRole = ref("admin")
const isInQueue = ref(false)
const isProcessingQueue = ref(false)
const currentCall = ref(null)

// SidePanel event handlers
const handleQueueToggle = () => {
  isInQueue.value = !isInQueue.value
}

const handleLogout = () => {
  console.log("Logout clicked")
}

const handleSidebarToggle = () => {
  console.log("Sidebar toggle clicked")
}

// Page state
const loading = ref(false)
const error = ref(null)
const fromDate = ref('')
const toDate = ref('')
const searchQuery = ref('')
const showDownloadMenu = ref(false)
const activeFilter = ref('all')
const viewMode = ref('table')

// Computed properties
const category = computed(() => route.params.category)

const hasActiveFilters = computed(() => {
  return fromDate.value || toDate.value || searchQuery.value || activeFilter.value !== 'all'
})

const categoryName = computed(() => {
  const names = {
    calls: 'Calls',
    cases: 'Cases', 
    counsellors: 'Counsellors',
    channels: 'Channels',
    all: 'All'
  }
  return names[category.value] || 'Reports'
})

const pageTitle = computed(() => `${categoryName.value} Reports`)

const pageDescription = computed(() => {
  const descriptions = {
    calls: 'Detailed analytics and metrics for all call activities',
    cases: 'Comprehensive case tracking and resolution statistics',
    counsellors: 'Performance metrics and workload analysis for counsellors',
    channels: 'Chat, WhatsApp and other channels: volume, directions, dispositions',
    all: 'Complete system overview with all metrics and analytics'
  }
  return descriptions[category.value] || 'View detailed reports and analytics'
})

// Mock data for demonstration
const totalCount = ref(0)
const averageMetric = ref(0)
const successRate = ref(0)
const tableHeaders = ref([])
const tableData = ref([])
const trendPoints = computed(() => {
  // Generate simple mock trend points from table data length
  const n = 8
  const pts = Array.from({ length: n }, (_, i) => {
    const x = (i / (n - 1)) * 300
    const y = 100 - ((Math.sin(i) + 1) * 40 + 10) // 10..90
    return `${x},${y}`
  })
  return pts.join(' ')
})

// Methods
const goBack = () => {
  router.push({ name: 'Reports' })
}

const applyFilters = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Mock data based on category
    const mockData = {
      calls: {
        total: 1247,
        average: '8.5 min',
        success: 94,
        headers: ['ID', 'Date', 'Duration', 'Status', 'Counsellor'],
        data: [
          { ID: 'C001', Date: '2024-01-15', Duration: '12:30', Status: 'Completed', Counsellor: 'John Doe' },
          { ID: 'C002', Date: '2024-01-15', Duration: '8:45', Status: 'Completed', Counsellor: 'Jane Smith' },
          { ID: 'C003', Date: '2024-01-15', Duration: '15:20', Status: 'In Progress', Counsellor: 'Mike Johnson' }
        ]
      },
      cases: {
        total: 89,
        average: '3.2 days',
        success: 87,
        headers: ['Case ID', 'Status', 'Created', 'Assigned To', 'Priority'],
        data: [
          { 'Case ID': 'CS001', Status: 'Resolved', Created: '2024-01-10', 'Assigned To': 'John Doe', Priority: 'High' },
          { 'Case ID': 'CS002', Status: 'In Progress', Created: '2024-01-12', 'Assigned To': 'Jane Smith', Priority: 'Medium' },
          { 'Case ID': 'CS003', Status: 'Open', Created: '2024-01-14', 'Assigned To': 'Mike Johnson', Priority: 'Low' }
        ]
      },
      counsellors: {
        total: 12,
        average: '85%',
        success: 92,
        headers: ['Name', 'Active Cases', 'Completed Cases', 'Success Rate', 'Avg Response Time'],
        data: [
          { Name: 'John Doe', 'Active Cases': 5, 'Completed Cases': 45, 'Success Rate': '94%', 'Avg Response Time': '2.3h' },
          { Name: 'Jane Smith', 'Active Cases': 3, 'Completed Cases': 38, 'Success Rate': '89%', 'Avg Response Time': '1.8h' },
          { Name: 'Mike Johnson', 'Active Cases': 7, 'Completed Cases': 52, 'Success Rate': '91%', 'Avg Response Time': '2.1h' }
        ]
      },
      channels: {
        total: 10,
        average: 'hourly',
        success: 0,
        headers: ['Channel', 'Case Created', 'Counselor Request', 'New Reporter', 'Noisy Background', 'Complaint', 'Silent', 'Total'],
        data: [
          { Channel: 'chat', 'Case Created': 1, 'Counselor Request': 1, 'New Reporter': 2, 'Noisy Background': 1, Complaint: 0, Silent: 0, Total: 5 },
          { Channel: 'safepal', 'Case Created': 0, 'Counselor Request': 0, 'New Reporter': 0, 'Noisy Background': 0, Complaint: 1, Silent: 0, Total: 1 },
          { Channel: 'whatsApp', 'Case Created': 0, 'Counselor Request': 0, 'New Reporter': 2, 'Noisy Background': 0, Complaint: 0, Silent: 0, Total: 2 }
        ]
      },
      all: {
        total: 1336,
        average: '85%',
        success: 90,
        headers: ['Metric', 'Current', 'Previous', 'Change', 'Status'],
        data: [
          { Metric: 'Total Calls', Current: '1247', Previous: '1189', Change: '+4.9%', Status: 'Positive' },
          { Metric: 'Active Cases', Current: '89', Previous: '76', Change: '+17.1%', Status: 'Positive' },
          { Metric: 'Counsellor Performance', Current: '85%', Previous: '82%', Change: '+3.7%', Status: 'Positive' }
        ]
      }
    }
    
    const data = mockData[category.value] || mockData.all
    
    totalCount.value = data.total
    averageMetric.value = data.average
    successRate.value = data.success
    tableHeaders.value = data.headers
    tableData.value = data.data
    
  } catch (err) {
    error.value = 'Failed to load data. Please try again.'
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  applyFilters()
}

const downloadReport = (format = 'csv') => {
  // Mock download functionality
  console.log(`Downloading ${categoryName.value} report as ${format.toUpperCase()}...`)
  
  const formats = {
    csv: 'CSV',
    excel: 'Excel',
    pdf: 'PDF'
  }
  
  alert(`${categoryName.value} report download started as ${formats[format]}!`)
}

const toggleDownloadMenu = () => {
  showDownloadMenu.value = !showDownloadMenu.value
}

const clearFilters = () => {
  fromDate.value = ''
  toDate.value = ''
  searchQuery.value = ''
  activeFilter.value = 'all'
  showDownloadMenu.value = false
  applyFilters()
}

const setActiveFilter = (filter) => {
  activeFilter.value = filter
  if (filter !== 'date-range') {
    applyFilters()
  }
}

// Lifecycle
onMounted(() => {
  applyFilters()
  
  // Close download menu when clicking outside
  document.addEventListener('click', (event) => {
    const dropdown = document.querySelector('.download-dropdown')
    if (dropdown && !dropdown.contains(event.target)) {
      showDownloadMenu.value = false
    }
  })
})
</script>

<style scoped>
/* ReportsCategory styles moved to global components.css */
.view-toggle { display:flex; gap:8px; margin-right:8px; }
.graph-view { background: var(--color-surface); border:1px solid var(--color-border); border-radius: var(--radius-lg); padding:12px; }
.graph-row { display:grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap:12px; }
.graph-card { background: var(--color-surface); border:1px solid var(--color-border); border-radius: var(--radius-lg); padding:12px; }
.donut { width: 160px; height:160px; display:block; margin:auto; }
.chart-center { font-size: 10px; fill: var(--color-fg); font-weight: 800; }
.line { width: 100%; height: 160px; }
</style>

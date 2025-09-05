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
      <div class="page-container scrollable-container">
        <!-- Modern Header -->
        <div class="page-header">
          <div class="header-top">
            <div class="header-left">
              <button class="btn btn--secondary btn--sm" @click="goBack">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M19 12H5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                  <path d="M12 19L5 12L12 5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
                Back to Reports
              </button>
            </div>
            <div class="header-right">
              <div class="download-dropdown">
                <button class="btn btn--primary btn--sm dropdown-toggle" @click="toggleDownloadMenu">
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
                    </svg>
                    Download as CSV
                  </button>
                  <button class="dropdown-item" @click="downloadReport('excel')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2"/>
                      <path d="M14 2V8H20" stroke="currentColor" stroke-width="2"/>
                    </svg>
                    Download as Excel
                  </button>
                  <button class="dropdown-item" @click="downloadReport('pdf')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                      <path d="M14 2H6C5.46957 2 4.96086 2.21071 4.58579 2.58579C4.21071 2.96086 4 3.46957 4 4V20C4 20.5304 4.21071 21.0391 4.58579 21.4142C4.96086 21.7893 5.46957 22 6 22H18C18.5304 22 19.0391 21.7893 19.4142 21.4142C19.7893 21.0391 20 20.5304 20 20V8L14 2Z" stroke="currentColor" stroke-width="2"/>
                      <path d="M14 2V8H20" stroke="currentColor" stroke-width="2"/>
                    </svg>
                    Download as PDF
                  </button>
                </div>
              </div>
            </div>
          </div>
          <div class="header-content">
            <h1 class="page-h1">{{ pageTitle }}</h1>
            <p class="page-sub">{{ pageDescription }}</p>
          </div>
        </div>

        <!-- Modern KPI Cards -->
        <div class="kpi-grid">
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

        <!-- Search and Controls Section -->
        <div class="search-and-controls-section">
            <div class="search-container">
              <input 
                type="text" 
                placeholder="Search {{ categoryName.toLowerCase() }}..." 
                v-model="searchQuery"
                class="search-input"
              />
            </div>
          <div class="controls-group">
            <div class="filter-tabs">
              <button 
                class="filter-tab" 
                :class="{ active: activeFilter === 'all' }"
                @click="setActiveFilter('all')"
              >
                All
              </button>
              <button 
                class="filter-tab" 
                :class="{ active: activeFilter === 'today' }"
                @click="setActiveFilter('today')"
              >
                Today
              </button>
              <button 
                class="filter-tab" 
                :class="{ active: activeFilter === 'week' }"
                @click="setActiveFilter('week')"
              >
                This Week
              </button>
              <button 
                class="filter-tab" 
                :class="{ active: activeFilter === 'month' }"
                @click="setActiveFilter('month')"
              >
                This Month
              </button>
              <button 
                class="filter-tab" 
                :class="{ active: activeFilter === 'date-range' }"
                @click="setActiveFilter('date-range')"
              >
                Date Range
              </button>
            </div>
            <div class="view-controls">
              <div class="view-toggle">
                <button class="btn btn--sm" :class="{ 'btn--primary': viewMode === 'table', 'btn--secondary': viewMode !== 'table' }" @click="viewMode = 'table'">Table</button>
                <button class="btn btn--sm" :class="{ 'btn--primary': viewMode === 'graph', 'btn--secondary': viewMode !== 'graph' }" @click="viewMode = 'graph'">Graph</button>
              </div>
              <button class="btn btn--secondary btn--sm" @click="refreshData" :disabled="loading">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M1 4V10H7" stroke="currentColor" stroke-width="2"/>
                  <path d="M23 20V14H17" stroke="currentColor" stroke-width="2"/>
                  <path d="M20.49 9C19.2214 7.33122 17.4547 6.08128 15.3778 5.43313C13.3008 4.78497 11.0167 4.7729 8.93142 5.39824C6.84616 6.02358 5.06075 7.25792 3.76476 8.91151C2.46877 10.5651 1.71538 12.5609 1.587 14.6583C1.45862 16.7557 1.96021 18.8529 3.02871 20.6467C4.09721 22.4405 5.68649 23.8458 7.57151 24.6693C9.45653 25.4928 11.5537 25.6975 13.5829 25.2578C15.6121 24.8181 17.4856 23.7508 18.976 22.176L23 18" stroke="currentColor" stroke-width="2"/>
                </svg>
                Refresh
              </button>
            </div>
          </div>
        </div>

        <!-- Date Range Section -->
        <div v-if="activeFilter === 'date-range'" class="date-range-section">
          <div class="date-range-card">
            <div class="date-inputs">
              <div class="date-input-group">
                <label for="from">From Date</label>
                <input id="from" type="date" v-model="fromDate" class="date-input" />
              </div>
              <div class="date-input-group">
                <label for="to">To Date</label>
                <input id="to" type="date" v-model="toDate" class="date-input" />
              </div>
              <div class="date-input-group">
                <label>&nbsp;</label>
                <button class="btn btn--primary btn--sm" @click="applyFilters" :disabled="loading">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                    <path d="M21 21L16.514 16.506L21 21ZM19 10.5C19 15.194 15.194 19 10.5 19C5.806 19 2 15.194 2 10.5C2 5.806 5.806 2 10.5 2C15.194 2 19 5.806 19 10.5Z" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  Apply Filters
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Content Section -->
        <div class="content-section">
          <!-- Graph View -->
          <div v-if="viewMode === 'graph'" class="graph-view">
            <div class="graph-grid">
              <!-- Success Rate Donut Chart -->
              <div class="graph-card">
                <div class="graph-header">
                  <h3>Success Rate Distribution</h3>
                  <div class="graph-subtitle">Overall performance metrics</div>
                </div>
                <div class="graph-content">
                  <div class="donut-container">
                    <svg viewBox="0 0 120 120" class="donut-chart">
                      <!-- Background circle -->
                      <circle cx="60" cy="60" r="45" fill="none" stroke="#f0f0f0" stroke-width="8"></circle>
                      <!-- Success segment -->
                      <circle cx="60" cy="60" r="45" fill="none" 
                              :stroke-dasharray="successRate + ' ' + (100-successRate)" 
                              stroke="#10B981" stroke-width="8" 
                              stroke-dashoffset="25" 
                              stroke-linecap="round"
                              class="success-segment"></circle>
                      <!-- Center text -->
                      <text x="60" y="55" text-anchor="middle" class="donut-percentage">{{ successRate }}%</text>
                      <text x="60" y="70" text-anchor="middle" class="donut-label">Success</text>
                    </svg>
                    <div class="donut-legend">
                      <div class="legend-item">
                        <div class="legend-color success"></div>
                        <span>Success: {{ successRate }}%</span>
                      </div>
                      <div class="legend-item">
                        <div class="legend-color failure"></div>
                        <span>Failed: {{ 100 - successRate }}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Trend Line Chart -->
              <div class="graph-card">
                <div class="graph-header">
                  <h3>Performance Trend</h3>
                  <div class="graph-subtitle">Last 7 days activity</div>
                </div>
                <div class="graph-content">
                  <div class="line-chart-container">
                    <svg viewBox="0 0 400 200" class="line-chart">
                      <!-- Grid lines -->
                      <defs>
                        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                          <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#f0f0f0" stroke-width="1"/>
                        </pattern>
                      </defs>
                      <rect width="400" height="200" fill="url(#grid)"></rect>
                      
                      <!-- Y-axis labels -->
                      <text x="10" y="20" class="axis-label">100</text>
                      <text x="10" y="60" class="axis-label">75</text>
                      <text x="10" y="100" class="axis-label">50</text>
                      <text x="10" y="140" class="axis-label">25</text>
                      <text x="10" y="180" class="axis-label">0</text>
                      
                      <!-- Trend line -->
                      <polyline :points="trendPoints" fill="none" stroke="#3B82F6" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="trend-line"></polyline>
                      
                      <!-- Data points -->
                      <circle v-for="(point, index) in trendDataPoints" :key="index" 
                              :cx="point.x" :cy="point.y" r="4" fill="#3B82F6" stroke="white" stroke-width="2" class="data-point"></circle>
                      
                      <!-- X-axis labels -->
                      <text x="50" y="195" class="axis-label">Mon</text>
                      <text x="100" y="195" class="axis-label">Tue</text>
                      <text x="150" y="195" class="axis-label">Wed</text>
                      <text x="200" y="195" class="axis-label">Thu</text>
                      <text x="250" y="195" class="axis-label">Fri</text>
                      <text x="300" y="195" class="axis-label">Sat</text>
                      <text x="350" y="195" class="axis-label">Sun</text>
                    </svg>
                  </div>
                </div>
              </div>

              <!-- Volume Bar Chart -->
              <div class="graph-card">
                <div class="graph-header">
                  <h3>Daily Volume</h3>
                  <div class="graph-subtitle">Activity over time</div>
                </div>
                <div class="graph-content">
                  <div class="bar-chart-container">
                    <svg viewBox="0 0 400 200" class="bar-chart">
                      <!-- Grid lines -->
                      <rect width="400" height="200" fill="url(#grid)"></rect>
                      
                      <!-- Bars -->
                      <rect v-for="(bar, index) in barChartData" :key="index"
                            :x="bar.x" :y="bar.y" :width="bar.width" :height="bar.height"
                            fill="#8B5CF6" class="bar" :class="{ 'bar-highlight': bar.highlight }"></rect>
                      
                      <!-- Y-axis labels -->
                      <text x="10" y="20" class="axis-label">50</text>
                      <text x="10" y="60" class="axis-label">40</text>
                      <text x="10" y="100" class="axis-label">30</text>
                      <text x="10" y="140" class="axis-label">20</text>
                      <text x="10" y="180" class="axis-label">10</text>
                      
                      <!-- X-axis labels -->
                      <text x="50" y="195" class="axis-label">Mon</text>
                      <text x="100" y="195" class="axis-label">Tue</text>
                      <text x="150" y="195" class="axis-label">Wed</text>
                      <text x="200" y="195" class="axis-label">Thu</text>
                      <text x="250" y="195" class="axis-label">Fri</text>
                      <text x="300" y="195" class="axis-label">Sat</text>
                      <text x="350" y="195" class="axis-label">Sun</text>
                </svg>
                  </div>
                </div>
              </div>

              <!-- Status Distribution -->
              <div class="graph-card">
                <div class="graph-header">
                  <h3>Status Distribution</h3>
                  <div class="graph-subtitle">Current case status breakdown</div>
                </div>
                <div class="graph-content">
                  <div class="status-chart">
                    <div class="status-item" v-for="status in statusData" :key="status.name">
                      <div class="status-bar">
                        <div class="status-fill" :style="{ width: status.percentage + '%', backgroundColor: status.color }"></div>
                      </div>
                      <div class="status-info">
                        <div class="status-name">{{ status.name }}</div>
                        <div class="status-value">{{ status.count }} ({{ status.percentage }}%)</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Table View -->
          <div v-else class="table-view">
            <div v-if="loading" class="loading-state">
              <div class="spinner"></div>
              <p>Loading {{ categoryName }} data...</p>
            </div>
            <div v-else-if="error" class="error-state">
              <p>{{ error }}</p>
            </div>
            <div v-else>
              <div class="table-container">
                <table class="data-table">
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
              </div>
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
  // Generate trend points for line chart
  const n = 7
  const pts = Array.from({ length: n }, (_, i) => {
    const x = 50 + (i * 50) // 50, 100, 150, 200, 250, 300, 350
    const y = 180 - ((Math.sin(i * 0.8) + 1) * 60 + 20) // 20..140
    return `${x},${y}`
  })
  return pts.join(' ')
})

const trendDataPoints = computed(() => {
  // Generate data points for line chart
  const n = 7
  return Array.from({ length: n }, (_, i) => {
    const x = 50 + (i * 50)
    const y = 180 - ((Math.sin(i * 0.8) + 1) * 60 + 20)
    return { x, y }
  })
})

const barChartData = computed(() => {
  // Generate bar chart data
  const n = 7
  return Array.from({ length: n }, (_, i) => {
    const height = Math.random() * 120 + 20 // 20-140
    const x = 30 + (i * 50)
    const y = 180 - height
    const width = 30
    return { x, y, width, height, highlight: i === 2 } // Highlight Wednesday
  })
})

const statusData = computed(() => {
  // Generate status distribution data
  const mockData = {
    calls: [
      { name: 'Completed', count: 45, percentage: 75, color: '#10B981' },
      { name: 'In Progress', count: 12, percentage: 20, color: '#F59E0B' },
      { name: 'Failed', count: 3, percentage: 5, color: '#EF4444' }
    ],
    cases: [
      { name: 'Resolved', count: 35, percentage: 70, color: '#10B981' },
      { name: 'In Progress', count: 10, percentage: 20, color: '#3B82F6' },
      { name: 'Open', count: 5, percentage: 10, color: '#F59E0B' }
    ],
    counsellors: [
      { name: 'Active', count: 8, percentage: 67, color: '#10B981' },
      { name: 'Available', count: 3, percentage: 25, color: '#3B82F6' },
      { name: 'Offline', count: 1, percentage: 8, color: '#6B7280' }
    ],
    channels: [
      { name: 'Chat', count: 5, percentage: 50, color: '#3B82F6' },
      { name: 'WhatsApp', count: 3, percentage: 30, color: '#10B981' },
      { name: 'Phone', count: 2, percentage: 20, color: '#8B5CF6' }
    ],
    all: [
      { name: 'Active', count: 120, percentage: 60, color: '#10B981' },
      { name: 'Pending', count: 50, percentage: 25, color: '#F59E0B' },
      { name: 'Completed', count: 30, percentage: 15, color: '#3B82F6' }
    ]
  }
  return mockData[category.value] || mockData.all
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
/* Scrollable Container */
.scrollable-container {
  max-height: calc(100vh - 20px);
  overflow-y: auto;
  padding-right: 8px;
}

.scrollable-container::-webkit-scrollbar {
  width: 6px;
}

.scrollable-container::-webkit-scrollbar-track {
  background: var(--color-surface);
  border-radius: 3px;
}

.scrollable-container::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 3px;
}

.scrollable-container::-webkit-scrollbar-thumb:hover {
  background: var(--color-muted);
}

/* Modern ReportsCategory Styles */
.page-header {
  margin-bottom: 24px;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.header-content {
  text-align: left;
}

.page-h1 {
  margin: 0 0 8px 0;
  color: var(--color-fg);
  font-size: 28px;
  font-weight: 700;
}

.page-sub {
  margin: 0;
  color: var(--color-muted);
  font-size: 16px;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.kpi-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  transition: all 0.2s ease;
}

.kpi-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.kpi-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  background: color-mix(in oklab, var(--color-primary) 10%, var(--color-surface));
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  flex-shrink: 0;
}

.kpi-content {
  flex: 1;
}

.kpi-value {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-fg);
  margin-bottom: 4px;
}

.kpi-label {
  font-size: 14px;
  color: var(--color-muted);
  font-weight: 500;
}

/* Search and Controls */
.search-and-controls-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
  margin-bottom: 24px;
}

.search-container {
  margin-bottom: 16px;
}

.search-input {
  width: 100%;
  max-width: 400px;
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-fg);
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px color-mix(in oklab, var(--color-primary) 10%, transparent);
}

.controls-group {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.filter-tabs {
  display: flex;
  gap: 8px;
}

.filter-tab {
  padding: 8px 16px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-muted);
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-tab:hover {
  background: color-mix(in oklab, var(--color-primary) 5%, var(--color-surface));
  border-color: var(--color-primary);
}

.filter-tab.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.view-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.view-toggle {
  display: flex;
  gap: 4px;
}

/* Date Range Section */
.date-range-section {
  margin-bottom: 24px;
}

.date-range-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 20px;
}

.date-inputs {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  align-items: end;
}

.date-input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.date-input-group label {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-fg);
}

.date-input {
  padding: 12px 16px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-fg);
  font-size: 14px;
}

.date-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px color-mix(in oklab, var(--color-primary) 10%, transparent);
}

/* Content Section */
.content-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

/* Graph View */
.graph-view {
  padding: 24px;
}

.graph-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
}

.graph-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 24px;
  transition: all 0.2s ease;
}

.graph-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.graph-header {
  margin-bottom: 20px;
  text-align: center;
}

.graph-header h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--color-fg);
}

.graph-subtitle {
  font-size: 14px;
  color: var(--color-muted);
  font-weight: 500;
}

.graph-content {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Donut Chart */
.donut-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.donut-chart {
  width: 200px;
  height: 200px;
}

.donut-percentage {
  font-size: 24px;
  font-weight: 700;
  fill: var(--color-fg);
}

.donut-label {
  font-size: 12px;
  font-weight: 500;
  fill: var(--color-muted);
}

.success-segment {
  transition: stroke-dasharray 0.5s ease;
}

.donut-legend {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: var(--color-fg);
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-color.success {
  background-color: #10B981;
}

.legend-color.failure {
  background-color: #EF4444;
}

/* Line Chart */
.line-chart-container {
  width: 100%;
  max-width: 500px;
}

.line-chart {
  width: 100%;
  height: 250px;
}

.axis-label {
  font-size: 12px;
  fill: var(--color-muted);
  font-weight: 500;
}

.trend-line {
  filter: drop-shadow(0 2px 4px rgba(59, 130, 246, 0.3));
}

.data-point {
  transition: r 0.2s ease;
}

.data-point:hover {
  r: 6;
}

/* Bar Chart */
.bar-chart-container {
  width: 100%;
  max-width: 500px;
}

.bar-chart {
  width: 100%;
  height: 250px;
}

.bar {
  transition: all 0.2s ease;
}

.bar:hover {
  opacity: 0.8;
}

.bar-highlight {
  fill: #F59E0B !important;
  filter: drop-shadow(0 2px 4px rgba(245, 158, 11, 0.3));
}

/* Status Chart */
.status-chart {
  width: 100%;
  max-width: 400px;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.status-bar {
  flex: 1;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.status-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.status-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 100px;
}

.status-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--color-fg);
}

.status-value {
  font-size: 12px;
  color: var(--color-muted);
}

/* Table View */
.table-view {
  padding: 0;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background: color-mix(in oklab, var(--color-primary) 5%, var(--color-surface));
  color: var(--color-fg);
  font-weight: 600;
  font-size: 14px;
  padding: 16px 20px;
  text-align: left;
  border-bottom: 1px solid var(--color-border);
}

.data-table td {
  padding: 16px 20px;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-fg);
  font-size: 14px;
}

.data-table tbody tr:hover {
  background: color-mix(in oklab, var(--color-primary) 2%, var(--color-surface));
}

/* Loading and Error States */
.loading-state, .error-state, .empty-state {
  padding: 40px 20px;
  text-align: center;
  color: var(--color-muted);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--color-border);
  border-top: 3px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Dropdown Menu */
.download-dropdown {
  position: relative;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  z-index: 1000;
  min-width: 180px;
  margin-top: 4px;
}

.dropdown-item {
  width: 100%;
  padding: 12px 16px;
  border: none;
  background: none;
  color: var(--color-fg);
  font-size: 14px;
  text-align: left;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: background-color 0.2s ease;
}

.dropdown-item:hover {
  background: color-mix(in oklab, var(--color-primary) 5%, var(--color-surface));
}

.dropdown-item:first-child {
  border-radius: var(--radius-md) var(--radius-md) 0 0;
}

.dropdown-item:last-child {
  border-radius: 0 0 var(--radius-md) var(--radius-md);
}

.dropdown-arrow {
  margin-left: 8px;
  transition: transform 0.2s ease;
}

.dropdown-toggle:hover .dropdown-arrow {
  transform: rotate(180deg);
}

/* Responsive Design */
@media (max-width: 768px) {
  .header-top {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .controls-group {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-tabs {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .view-controls {
    justify-content: center;
  }
  
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  
  .date-inputs {
    grid-template-columns: 1fr;
  }
  
  .graph-grid {
    grid-template-columns: 1fr;
  }
}
</style>

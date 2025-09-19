<template>
  <div>
    <!-- SidePanel Component -->
    <SidePanel :userRole="userRole" :isInQueue="isInQueue" :isProcessingQueue="isProcessingQueue"
      :currentCall="currentCall" @toggle-queue="handleQueueToggle" @logout="handleLogout"
      @sidebar-toggle="handleSidebarToggle" />

    <!-- Add router-view -->
    <router-view></router-view>

    <!-- Main Content -->
    <div class="main-content">
      <div class="header">
        <h1 class="page-title">Dashboard</h1>
        
      </div>

      <div class="main-scroll-content">
        <!-- Call Status Card -->
        <div class="call-status-container" :class="{ 'active-call': activeCall }">
          <div class="call-status-card">
            <div class="call-status-header">
              <div class="call-status-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path
                    d="M22 16.92V19C22 20.1046 21.1046 21 20 21C10.6112 21 3 13.3888 3 4C3 2.89543 3.89543 2 5 2H7.08C7.55607 2 7.95823 2.33718 8.02513 2.80754L8.7 7.5C8.76694 7.97036 8.53677 8.42989 8.12 8.67L6.5 9.5C7.84 12.16 11.84 16.16 14.5 17.5L15.33 15.88C15.5701 15.4632 16.0296 15.2331 16.5 15.3L21.1925 16.0249C21.6628 16.0918 22 16.4939 22 16.97V16.92Z"
                    stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </div>
              <div class="call-status-title">
                {{ callStatusText }}
              </div>
            </div>

            <!-- Incoming Call UI -->
            <div v-if="incomingCall" class="incoming-call-controls">
              <div class="caller-info">
                <div class="caller-name">{{ incomingCall.callerName || 'Unknown Caller' }}</div>
                <div class="caller-number">{{ incomingCall.callerNumber || 'Private Number' }}</div>
              </div>
              <div class="call-buttons">
                <button class="answer-btn" @click="answerIncomingCall">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path
                      d="M22 16.92V19C22 20.1046 21.1046 21 20 21C10.6112 21 3 13.3888 3 4C3 2.89543 3.89543 2 5 2H7.08C7.55607 2 7.95823 2.33718 8.02513 2.80754L8.7 7.5C8.76694 7.97036 8.53677 8.42989 8.12 8.67L6.5 9.5C7.84 12.16 11.84 16.16 14.5 17.5L15.33 15.88C15.5701 15.4632 16.0296 15.2331 16.5 15.3L21.1925 16.0249C21.6628 16.0918 22 16.4939 22 16.97V16.92Z"
                      stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                  Answer
                </button>
                <button class="reject-btn" @click="rejectIncomingCall">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M18 6L6 18M6 6L18 18" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                      stroke-linejoin="round" />
                  </svg>
                  Reject
                </button>
              </div>
            </div>

            <!-- Active Call UI -->
            <div v-if="activeCall" class="active-call-controls">
              <div class="call-info">
                <div class="call-duration">{{ callDuration }}</div>
                <div class="caller-info">
                  <div class="caller-name">{{ activeCall.callerName || 'Unknown Caller' }}</div>
                  <div class="caller-number">{{ activeCall.callerNumber || 'Private Number' }}</div>
                </div>
              </div>
              <div class="call-actions">
                <button class="mute-btn" @click="toggleMute" :class="{ active: isMuted }">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path
                      d="M12 1C13.1046 1 14 1.89543 14 3V8C14 9.10457 13.1046 10 12 10H10C8.89543 10 8 9.10457 8 8V3C8 1.89543 8.89543 1 10 1H12Z"
                      stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                    <path d="M6 8H4C2.89543 8 2 8.89543 2 10V14C2 15.1046 2.89543 16 4 16H6L10 20V4L6 8Z"
                      stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                    <path v-if="isMuted" d="M16 10L22 4M22 10L16 4" stroke="currentColor" stroke-width="2"
                      stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </button>
                <button class="transfer-btn" @click="showTransferDialog">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M17 2L22 7L17 12M7 12L2 7L7 2" stroke="currentColor" stroke-width="2"
                      stroke-linecap="round" stroke-linejoin="round" />
                    <path
                      d="M22 7H9C7.89543 7 7 7.89543 7 9V15C7 16.1046 7.89543 17 9 17H15C16.1046 17 17 16.1046 17 15V9"
                      stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </button>
                <button class="hangup-btn" @click="endCall">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path
                      d="M22 16.92V19C22 20.1046 21.1046 21 20 21C10.6112 21 3 13.3888 3 4C3 2.89543 3.89543 2 5 2H7.08C7.55607 2 7.95823 2.33718 8.02513 2.80754L8.7 7.5C8.76694 7.97036 8.53677 8.42989 8.12 8.67L6.5 9.5C7.84 12.16 11.84 16.16 14.5 17.5L15.33 15.88C15.5701 15.4632 16.0296 15.2331 16.5 15.3L21.1925 16.0249C21.6628 16.0918 22 16.4939 22 16.97V16.92Z"
                      stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                    <path d="M17 7L7 17M7 7L17 17" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                      stroke-linejoin="round" />
                  </svg>
                </button>
              </div>
            </div>

            <!-- Queue Status -->
            <!-- (REMOVED from here, now at top) -->
          </div>
        </div>

        <!-- Dashboard Grid -->
        <div class="dashboard-grid">
          <div class="dashboard-card glass-card fine-border">
            <div class="card-header">
              <div class="card-title">Total Calls</div>
            </div>
            <div class="card-value gold-text">53</div>
            <div class="card-subtitle">+12% from last week</div>
          </div>

          <div class="dashboard-card glass-card fine-border">
            <div class="card-header">
              <div class="card-title">Active Cases</div>
            </div>
            <div class="card-value">24</div>
            <div class="card-subtitle">+5% from last week</div>
          </div>

          <div class="dashboard-card glass-card fine-border">
            <div class="card-header">
              <div class="card-title">Pending Calls</div>
            </div>
            <div class="card-value">5</div>
            <div class="card-subtitle">-2% from last week</div>
          </div>

          <div class="dashboard-card glass-card fine-border">
            <div class="card-header">
              <div class="card-title">Completed Calls</div>
            </div>
            <div class="card-value">42</div>
            <div class="card-subtitle">+8% from last week</div>
          </div>

          <!-- New Prank Calls Card -->
          <div class="dashboard-card glass-card fine-border">
            <div class="card-header">
              <div class="card-title">Prank Calls</div>
              <div class="card-icon prank-calls">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path d="M12 2L13.09 8.26L22 9L13.09 9.74L12 16L10.91 9.74L2 9L10.91 8.26L12 2Z" stroke="white"
                    stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                  <path d="M8 21L9 19L11 20L9 21L8 21Z" stroke="white" stroke-width="2" stroke-linecap="round"
                    stroke-linejoin="round" />
                  <path d="M19 21L20 19L22 20L20 21L19 21Z" stroke="white" stroke-width="2" stroke-linecap="round"
                    stroke-linejoin="round" />
                </svg>
              </div>
            </div>
            <div class="card-value">7</div>
            <div class="card-subtitle">-15% from last week</div>
          </div>

          <!-- New Counsellors Online Card -->
          <div class="dashboard-card glass-card fine-border">
            <div class="card-header">
              <div class="card-title">Counsellors Online</div>
              <div class="card-icon counsellors-online">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <path
                    d="M17 21V19C17 17.9391 16.5786 16.9217 15.8284 16.1716C15.0783 15.4214 14.0609 15 13 15H5C3.93913 15 2.92172 15.4214 2.17157 16.1716C1.42143 16.9217 1 17.9391 1 19V21"
                    stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                  <circle cx="9" cy="7" r="4" stroke="white" stroke-width="2" stroke-linecap="round"
                    stroke-linejoin="round" />
                  <path
                    d="M23 21V19C23 18.1645 22.7155 17.3541 22.2094 16.6977C21.7033 16.0414 20.9999 15.5735 20.2 15.3613"
                    stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                  <path
                    d="M16 3.13C16.8003 3.3422 17.5037 3.81014 18.0098 4.46645C18.5159 5.12277 18.8004 5.93317 18.8004 6.76875C18.8004 7.60433 18.5159 8.41473 18.0098 9.07105C17.5037 9.72736 16.8003 10.1953 16 10.4075"
                    stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </div>
            </div>
            <div class="card-value">12</div>
            <div class="card-subtitle">Currently available</div>
          </div>
        </div>

        <!-- Queue Activity -->
        <div class="queue-activity">
          <div class="section-header">
            <div class="section-title">Queue Activity</div>
          </div>

          <table class="queue-table">
            <thead>
              <tr>
                <th>Agent Name</th>
                <th>Current Status</th>
                <th>Calls Handled</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="agent in queueAgents" :key="agent.name">
                <td>{{ agent.name }}</td>
                <td><span class="agent-status" :class="agent.statusClass">{{ agent.status }}</span></td>
                <td>{{ agent.calls }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Recent Calls -->
  
  <div class="recent-calls">
    <div class="section-header">
      <div class="section-title">Recent Calls</div>
      <button class="view-all" @click="navigateToCalls">View All</button>
    </div>

    <div class="call-list">
      <div
        v-for="(call, index) in casesStore.cases.slice(0, 5)"
        :key="call[casesStore.cases_k?.id?.[0]] || index"
        class="call-item glass-card fine-border"
      >
       
        <div class="call-details">
          <div class="call-type">
            {{ call[casesStore.cases_k?.case_category?.[0]] || "N/A" }}
          </div>

          <div class="call-time">
            {{
              casesStore.cases_k?.dt
                        ? new Date(
                            call[casesStore.cases_k.hr[0]] < 10000000000
                              ? call[casesStore.cases_k.hr[0]] * 1000
                              : call[casesStore.cases_k.hr[0]] * 3600 * 1000
                          ).toLocaleString()
                        : "No Date"
            }}
          </div>

         <div class="call-status"
  :style="{ backgroundColor: getStatusColor(call[casesStore.cases_k.status[0]]) }"
>
  Status: {{ getStatusLabel(call[casesStore.cases_k.status[0]]) }}
</div>
        </div>
      </div>
    </div>
  </div>

        <!-- Enhanced Chart Container -->
        <div class="chart-container">
          <div class="chart-card">
            <div class="chart-header">
              <div class="section-title">Call Volume Trends</div>
              <div class="chart-controls">
                <button v-for="period in chartPeriods" :key="period.value" class="chart-period-btn"
                  :class="{ active: selectedPeriod === period.value }" @click="changePeriod(period.value)">
                  {{ period.label }}
                </button>
              </div>
            </div>
            <div class="chart-stats">
              <div class="chart-stat">
                <div class="stat-label">Total Calls</div>
                <div class="stat-value">{{ totalCalls }}</div>
                <div class="stat-change" :class="{ positive: callsChange > 0, negative: callsChange < 0 }">
                  <svg v-if="callsChange > 0" width="12" height="12" viewBox="0 0 24 24" fill="none"
                    xmlns="http://www.w3.org/2000/svg">
                    <path d="M7 14L12 9L17 14" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                      stroke-linejoin="round" />
                  </svg>
                  <svg v-else width="12" height="12" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M7 10L12 15L17 10" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                      stroke-linejoin="round" />
                  </svg>
                  {{ Math.abs(callsChange) }}%
                </div>
              </div>
              <div class="chart-stat">
                <div class="stat-label">Peak Hour</div>
                <div class="stat-value">{{ peakHour }}</div>
                <div class="stat-description">{{ peakCalls }} calls</div>
              </div>
              <div class="chart-stat">
                <div class="stat-label">Average Response</div>
                <div class="stat-value">{{ avgResponse }}</div>
                <div class="stat-description">Response time</div>
              </div>
            </div>
            <div class="chart-placeholder">
              <div class="enhanced-chart">
                <!-- Y-axis labels -->
                <div class="y-axis-labels">
                  <div v-for="(label, index) in yAxisLabels" :key="index" class="y-label"
                    :style="{ bottom: (index * 25) + '%' }">
                    {{ label }}
                  </div>
                </div>

                <!-- Chart grid -->
                <div class="chart-grid">
                  <div v-for="i in 5" :key="i" class="grid-line-horizontal" :style="{ bottom: ((i - 1) * 25) + '%' }">
                  </div>
                  <div v-for="i in chartData.length" :key="i" class="grid-line-vertical"
                    :style="{ left: ((i - 1) * (100 / (chartData.length - 1))) + '%' }"></div>
                </div>

                <!-- Chart area -->
                <div class="chart-area">
                  <!-- Area fill -->
                  <svg class="chart-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
                    <defs>
                      <linearGradient id="chartGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" :style="{ stopColor: 'var(--accent-color)', stopOpacity: 0.3 }" />
                        <stop offset="100%" :style="{ stopColor: 'var(--accent-color)', stopOpacity: 0.05 }" />
                      </linearGradient>
                    </defs>
                    <path :d="areaPath" fill="url(#chartGradient)" />
                    <path :d="linePath" stroke="var(--accent-color)" stroke-width="0.5" fill="none" />
                  </svg>

                  <!-- Data points -->
                  <div v-for="(point, index) in chartData" :key="index" class="chart-point" :style="{
                    left: (index * (100 / (chartData.length - 1))) + '%',
                    bottom: point.percentage + '%'
                  }" @mouseenter="showTooltip(point, $event)" @mouseleave="hideTooltip">
                    <div class="point-dot"></div>
                  </div>
                </div>

                <!-- X-axis labels -->
                <div class="x-axis-labels">
                  <div v-for="(point, index) in chartData" :key="index" class="x-label"
                    :style="{ left: (index * (100 / (chartData.length - 1))) + '%' }">
                    {{ point.label }}
                  </div>
                </div>
              </div>
            </div>

            <!-- Tooltip -->
            <div v-if="tooltip.show" class="chart-tooltip" :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }">
              <div class="tooltip-title">{{ tooltip.data.label }}</div>
              <div class="tooltip-value">{{ tooltip.data.value }} calls</div>
              <div class="tooltip-time">{{ tooltip.data.time }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Transfer Dialog -->
    <teleport to="body">
      <div v-if="transferDialog" class="transfer-dialog">
        <div class="transfer-dialog-content">
          <h3 class="transfer-dialog-title">Transfer Call</h3>
          <input v-model="transferTarget" class="transfer-input" placeholder="Enter extension number"
            @keyup.enter="transferCallToTarget">
          <div class="transfer-dialog-buttons">
            <button class="transfer-cancel-btn" @click="transferDialog = false">
              Cancel
            </button>
            <button class="transfer-confirm-btn" @click="transferCallToTarget">
              Transfer
            </button>
          </div>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script setup>
  import { ref, computed, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import SidePanel from '@/components/SidePanel.vue'
  import { joinQueue } from '@/utils/sipClient.js'
  import { useCaseStore } from '@/stores/cases'

const casesStore = useCaseStore()

onMounted(async () => {
  await casesStore.listCases({ src: 'call' }) // fetch only call-based cases
  console.log('Loaded cases:', casesStore.cases)
})

const statusMap = {
  0: { label: 'None', color: '#ffffff' },
  1: { label: 'Ongoing', color: '#8B4513' },
  2: { label: 'Closed', color: '#4eb151' },
  3: { label: 'Escalated', color: '#ff0000' }
}

function getStatusLabel(statusCode) {
  const status = statusMap[Number(statusCode)];
  return status ? status.label : 'Unknown';
}

function getStatusColor(statusCode) {
  const status = statusMap[Number(statusCode)];
  return status ? status.color : '#ccc';
}
  // Reactive state
  const route = useRoute()
  const router = useRouter()
  const currentTheme = ref('dark')
  const userRole = ref('super-admin')

  // Queue management state
  const isInQueue = ref(false)
  const isProcessingQueue = ref(false)
  const currentCall = ref(null)

  // Chart state
  const selectedPeriod = ref('7d')
  const tooltip = ref({
    show: false,
    x: 0,
    y: 0,
    data: {}
  })

  const chartPeriods = ref([
    { label: '7D', value: '7d' },
    { label: '30D', value: '30d' },
    { label: '3M', value: '3m' },
    { label: '1Y', value: '1y' }
  ])

  const queueAgents = ref([
    { name: 'Sarah Davis', status: 'Available', statusClass: 'status-available', calls: 34 },
    { name: 'Mark Reynolds', status: 'In Call', statusClass: 'status-in-call', calls: 28 },
    { name: 'Emily Chan', status: 'On Break', statusClass: 'status-on-break', calls: 15 },
    { name: 'David Lee', status: 'Available', statusClass: 'status-available', calls: 42 },
    { name: 'Sophia Clark', status: 'In Call', statusClass: 'status-in-call', calls: 30 }
  ])

  const recentCalls = ref([
    {
      id: 1,
      type: 'Emergency Crisis: Domestic Violence',
      time: 'Today, 09:00AM',
      status: 'In Progress',
      statusClass: 'status-in-progress'
    },
    {
      id: 2,
      type: 'Survivor Follow-Up: Safety Planning',
      time: 'Today, 10:30AM',
      status: 'Pending',
      statusClass: 'status-pending'
    },
    {
      id: 3,
      type: 'Wellness Check-In: Mental Health Support',
      time: 'Yesterday, 11:15AM',
      status: 'Completed',
      statusClass: 'status-completed'
    },
    {
      id: 4,
      type: 'Resource Request: Shelter Information',
      time: 'Today, 04:45PM',
      status: 'Unassigned',
      statusClass: 'status-unassigned'
    }
  ])

  const chartDataSets = ref({
    '7d': [
      { label: 'Mon', value: 15, time: '9:00 AM - 5:00 PM' },
      { label: 'Tue', value: 23, time: '9:00 AM - 5:00 PM' },
      { label: 'Wed', value: 31, time: '9:00 AM - 5:00 PM' },
      { label: 'Thu', value: 38, time: '9:00 AM - 5:00 PM' },
      { label: 'Fri', value: 25, time: '9:00 AM - 5:00 PM' },
      { label: 'Sat', value: 18, time: '10:00 AM - 4:00 PM' },
      { label: 'Sun', value: 12, time: '12:00 PM - 4:00 PM' }
    ],
    '30d': [
      { label: 'Week 1', value: 142, time: 'Jan 1-7' },
      { label: 'Week 2', value: 168, time: 'Jan 8-14' },
      { label: 'Week 3', value: 195, time: 'Jan 15-21' },
      { label: 'Week 4', value: 178, time: 'Jan 22-28' }
    ],
    '3m': [
      { label: 'Jan', value: 683, time: 'January 2024' },
      { label: 'Feb', value: 721, time: 'February 2024' },
      { label: 'Mar', value: 658, time: 'March 2024' }
    ],
    '1y': [
      { label: 'Q1', value: 2062, time: 'Jan-Mar 2024' },
      { label: 'Q2', value: 2341, time: 'Apr-Jun 2024' },
      { label: 'Q3', value: 2198, time: 'Jul-Sep 2024' },
      { label: 'Q4', value: 2456, time: 'Oct-Dec 2024' }
    ]
  })

  // Computed properties
  const chartData = computed(() => {
    const data = chartDataSets.value[selectedPeriod.value]
    const maxValue = Math.max(...data.map(d => d.value))
    return data.map(d => ({
      ...d,
      percentage: (d.value / maxValue) * 80 + 10 // 10% padding at bottom, 10% at top
    }))
  })

  const yAxisLabels = computed(() => {
    const data = chartDataSets.value[selectedPeriod.value]
    const maxValue = Math.max(...data.map(d => d.value))
    const step = Math.ceil(maxValue / 4)
    return [0, step, step * 2, step * 3, maxValue]
  })

  const linePath = computed(() => {
    const points = chartData.value.map((point, index) => {
      const x = (index * (100 / (chartData.value.length - 1)))
      const y = 100 - point.percentage
      return `${x},${y}`
    })
    return `M ${points.join(' L ')}`
  })

  const areaPath = computed(() => {
    const points = chartData.value.map((point, index) => {
      const x = (index * (100 / (chartData.value.length - 1)))
      const y = 100 - point.percentage
      return `${x},${y}`
    })
    const firstPoint = points[0].split(',')
    const lastPoint = points[points.length - 1].split(',')
    return `M ${firstPoint[0]},100 L ${points.join(' L ')} L ${lastPoint[0]},100 Z`
  })

  const totalCalls = computed(() => {
    return chartDataSets.value[selectedPeriod.value].reduce((sum, d) => sum + d.value, 0)
  })

  const callsChange = computed(() => {
    // Mock calculation - in real app this would compare with previous period
    return selectedPeriod.value === '7d' ? 12 : selectedPeriod.value === '30d' ? 8 : selectedPeriod.value === '3m' ? -3 : 15
  })

  const peakHour = computed(() => {
    const peaks = {
      '7d': '2:00 PM',
      '30d': 'Week 3',
      '3m': 'February',
      '1y': 'Q4'
    }
    return peaks[selectedPeriod.value]
  })

  const peakCalls = computed(() => {
    return Math.max(...chartDataSets.value[selectedPeriod.value].map(d => d.value))
  })

  const avgResponse = computed(() => {
    const responses = {
      '7d': '2.3m',
      '30d': '2.1m',
      '3m': '2.5m',
      '1y': '2.2m'
    }
    return responses[selectedPeriod.value]
  })

  // Methods
  const handleQueueToggle = async () => {
    if (currentCall.value) {
      // End call logic would go here
      return
    }

    isProcessingQueue.value = true

    try {
      if (isInQueue.value) {
        // Leave queue
        isInQueue.value = false
        console.log('Left queue')
      } else {
        // Join queue
        await joinQueue()
        isInQueue.value = true
        console.log('Joined queue')
      }
    } finally {
      isProcessingQueue.value = false
    }
  }

  const handleLogout = () => {
    console.log('Logging out...')
    alert('Logged out successfully!')
  }

  const handleSidebarToggle = (collapsed) => {
    console.log('Sidebar toggled:', collapsed)
  }

  const navigateToCalls = () => {
    router.push('/calls')
  }

  const changePeriod = (period) => {
    selectedPeriod.value = period
  }

  const showTooltip = (data, event) => {
    const rect = event.target.getBoundingClientRect()
    const container = event.target.closest('.chart-card').getBoundingClientRect()

    tooltip.value = {
      show: true,
      x: rect.left - container.left + rect.width / 2,
      y: rect.top - container.top - 10,
      data: data
    }
  }

  const hideTooltip = () => {
    tooltip.value.show = false
  }

  const applyTheme = (theme) => {
    const root = document.documentElement

    if (theme === 'light') {
      root.style.setProperty('--background-color', '#f5f5f5')
      root.style.setProperty('--sidebar-bg', '#ffffff')
      root.style.setProperty('--content-bg', '#ffffff')
      root.style.setProperty('--text-color', '#333')
      root.style.setProperty('--text-secondary', '#666')
      root.style.setProperty('--border-color', '#ddd')
      root.style.setProperty('--card-bg', '#ffffff')
      root.style.setProperty('--logo-bg', '#ffffff')
      root.style.setProperty('--logo-color', '#333')
      root.setAttribute('data-theme', 'light')
    } else {
      root.style.setProperty('--background-color', '#0a0a0a')
      root.style.setProperty('--sidebar-bg', '#111')
      root.style.setProperty('--content-bg', '#222')
      root.style.setProperty('--text-color', '#fff')
      root.style.setProperty('--text-secondary', '#aaa')
      root.style.setProperty('--border-color', '#333')
      root.style.setProperty('--card-bg', '#222')
      root.style.setProperty('--logo-bg', '#fff')
      root.style.setProperty('--logo-color', '#0a0a0a')
      root.setAttribute('data-theme', 'dark')
    }

    // Set common variables
    root.style.setProperty('--accent-color', '#8B4513')
    root.style.setProperty('--accent-hover', '#A0522D')
    root.style.setProperty('--danger-color', '#ff3b30')
    root.style.setProperty('--success-color', '#4CAF50')
    root.style.setProperty('--pending-color', '#FFA500')
    root.style.setProperty('--unassigned-color', '#808080')
    root.style.setProperty('--highlight-color', '#ff3b30')
    root.style.setProperty('--prank-color', '#9C27B0')
    root.style.setProperty('--counsellor-color', '#2196F3')
  }

  const toggleTheme = () => {
    currentTheme.value = currentTheme.value === 'dark' ? 'light' : 'dark'
    localStorage.setItem('theme', currentTheme.value)
    applyTheme(currentTheme.value)
  }

  // Lifecycle
  onMounted(() => {
    // Load saved theme
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme) {
      currentTheme.value = savedTheme
    }

    // Apply theme immediately
    applyTheme(currentTheme.value)
  })
</script>

<style scoped>
/* Dashboard styles moved to components.css */
</style>
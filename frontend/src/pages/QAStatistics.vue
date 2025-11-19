<template>
<div>
  <SidePanel :userRole="userRole" :isInQueue="isInQueue" :isProcessingQueue="isProcessingQueue" :currentCall="currentCall" @toggle-queue="handleQueueToggle" @logout="handleLogout" @sidebar-toggle="handleSidebarToggle" />
  <div class="main-content">
    <div class="page-header">
      <div class="header-top">
        <div class="header-left">
          <h1 class="page-title">Quality Assurance</h1>
          <p class="page-subtitle">Monitor and improve call center performance</p>
        </div>
        <div class="header-actions">
          <button class="btn btn--primary" @click="refreshData">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"/>
              <path d="M21 3v5h-5"/>
              <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"/>
              <path d="M3 21v-5h5"/>
            </svg>
            Refresh
          </button>
        </div>
      </div>
    </div>

    <!-- KPI Cards -->
    <div class="kpi-grid">
      <div class="kpi-card">
        <div class="kpi-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M22 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
        </div>
        <div class="kpi-content">
          <div class="kpi-value">{{ totalCounsellors }}</div>
          <div class="kpi-label">Active Counsellors</div>
        </div>
      </div>
      
              <div class="kpi-card">
                <div class="kpi-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                  </svg>
                </div>
                <div class="kpi-content">
                  <div class="kpi-value">{{ averageScore }}%</div>
                  <div class="kpi-label">Average Score</div>
                </div>
              </div>
      
      <div class="kpi-card">
        <div class="kpi-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 12l2 2 4-4"/>
            <path d="M21 12c-1 0-3-1-3-3s2-3 3-3 3 1 3 3-2 3-3 3"/>
            <path d="M3 12c1 0 3-1 3-3s-2-3-3-3-3 1-3 3 2 3 3 3"/>
            <path d="M12 3c0 1-1 3-3 3s-3-2-3-3 1-3 3-3 3 2 3 3"/>
            <path d="M12 21c0-1 1-3 3-3s3 2 3 3-1 3-3 3-3-2-3-3"/>
          </svg>
        </div>
        <div class="kpi-content">
          <div class="kpi-value">{{ totalEvaluations }}</div>
          <div class="kpi-label">Evaluations</div>
        </div>
      </div>
      
      <div class="kpi-card">
        <div class="kpi-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
          </svg>
        </div>
        <div class="kpi-content">
          <div class="kpi-value">{{ pendingEvaluations }}</div>
          <div class="kpi-label">Pending Reviews</div>
        </div>
      </div>
    </div>

    <!-- Main Content Tabs -->
    <div class="content-tabs">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        class="tab-button"
        :class="{ active: activeTab === tab.id }"
        @click="activeTab = tab.id"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path :d="tab.icon"/>
        </svg>
        {{ tab.name }}
      </button>
    </div>

    <!-- Tab Content -->
    <div class="tab-content">
      <!-- Dashboard Tab -->
      <div v-if="activeTab === 'dashboard'" class="dashboard-content">
        <div class="charts-grid">
          <div class="chart-card">
            <div class="chart-header">
              <h3>Performance Trends</h3>
              <div class="chart-controls">
                <button class="chart-btn" :class="{ active: chartPeriod === 'week' }" @click="chartPeriod = 'week'">Week</button>
                <button class="chart-btn" :class="{ active: chartPeriod === 'month' }" @click="chartPeriod = 'month'">Month</button>
                <button class="chart-btn" :class="{ active: chartPeriod === 'quarter' }" @click="chartPeriod = 'quarter'">Quarter</button>
              </div>
            </div>
            <div class="chart-placeholder">
              <div class="chart-mock">
                <div class="chart-line"></div>
                <div class="chart-points">
                  <div class="chart-point" style="left: 10%; bottom: 20%;"></div>
                  <div class="chart-point" style="left: 30%; bottom: 45%;"></div>
                  <div class="chart-point" style="left: 50%; bottom: 60%;"></div>
                  <div class="chart-point" style="left: 70%; bottom: 75%;"></div>
                  <div class="chart-point" style="left: 90%; bottom: 85%;"></div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="chart-card">
            <div class="chart-header">
              <h3>Score Distribution</h3>
            </div>
            <div class="score-distribution">
              <div class="score-bar">
                <div class="score-label">Excellent (90-100%)</div>
                <div class="score-progress">
                  <div class="score-fill" style="width: 25%; background: var(--color-success);"></div>
                </div>
                <div class="score-count">12</div>
              </div>
              <div class="score-bar">
                <div class="score-label">Good (80-89%)</div>
                <div class="score-progress">
                  <div class="score-fill" style="width: 40%; background: #4ade80;"></div>
                </div>
                <div class="score-count">19</div>
              </div>
              <div class="score-bar">
                <div class="score-label">Average (70-79%)</div>
                <div class="score-progress">
                  <div class="score-fill" style="width: 30%; background: #fbbf24;"></div>
                </div>
                <div class="score-count">14</div>
              </div>
              <div class="score-bar">
                <div class="score-label">Needs Improvement (<70%)</div>
                <div class="score-progress">
                  <div class="score-fill" style="width: 15%; background: var(--color-danger);"></div>
                </div>
                <div class="score-count">7</div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="top-performers">
          <h3>Top Performers</h3>
          <div class="performers-list">
            <div v-for="(performer, index) in topPerformers" :key="performer.id" class="performer-card">
              <div class="performer-rank">{{ index + 1 }}</div>
              <div class="performer-avatar">{{ getInitials(performer.name) }}</div>
              <div class="performer-info">
                <div class="performer-name">{{ performer.name }}</div>
                <div class="performer-stats">{{ performer.evaluations }} evaluations</div>
              </div>
              <div class="performer-score">{{ performer.score }}%</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Evaluations Tab -->
      <div v-if="activeTab === 'evaluations'" class="evaluations-content">
        <div class="evaluations-header">
          <div class="search-filters">
            <div class="search-box">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"/>
                <path d="M21 21l-4.35-4.35"/>
              </svg>
              <input v-model="searchQuery" placeholder="Search calls, counsellors..." />
            </div>
            <div class="filter-buttons">
              <button class="filter-btn" :class="{ active: statusFilter === 'all' }" @click="statusFilter = 'all'">All</button>
              <button class="filter-btn" :class="{ active: statusFilter === 'pending' }" @click="statusFilter = 'pending'">Pending</button>
              <button class="filter-btn" :class="{ active: statusFilter === 'evaluated' }" @click="statusFilter = 'evaluated'">Evaluated</button>
            </div>
          </div>
        </div>
        
        <div class="evaluations-table-container">
          <table class="evaluations-table">
            <thead>
              <tr>
                <th>Call ID</th>
                <th>Counsellor</th>
                <th>Date & Time</th>
                <th>Issue Type</th>
                <th>Score</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="call in filteredCalls" :key="call.id">
                <td class="call-id-cell">
                  <div class="call-id">#{{ call.id }}</div>
                </td>
                <td class="counsellor-cell">
                  <div class="counsellor-info">
                    <div class="counsellor-avatar">{{ getInitials(call.agent.name) }}</div>
                    <div class="counsellor-name">{{ call.agent.name }}</div>
                  </div>
                </td>
                <td class="date-cell">{{ formatDateTime(call.dateTime) }}</td>
                <td class="issue-cell">
                  <span class="issue-badge">{{ call.issueType }}</span>
                </td>
                <td class="score-cell">
                  <div v-if="call.evaluation" class="score-display">
                    <div class="score-circle" :class="getScoreClass(call.evaluation.overallScore)">
                      {{ call.evaluation.overallScore }}%
                    </div>
                  </div>
                  <div v-else class="score-pending">-</div>
                </td>
                <td class="status-cell">
                  <span class="status-badge" :class="call.isEvaluated ? 'evaluated' : 'pending'">
                    {{ call.isEvaluated ? 'Evaluated' : 'Pending' }}
                  </span>
                </td>
                <td class="actions-cell">
                  <div class="action-buttons">
                    <button class="action-btn view-btn" @click="viewCallDetails(call)">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                      </svg>
                    </button>
                    <button v-if="!call.isEvaluated" class="action-btn evaluate-btn" @click="startEvaluation(call)">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                      </svg>
                    </button>
                    <button v-else class="action-btn edit-btn" @click="editEvaluation(call)">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

              <!-- Counsellors Tab -->
              <div v-if="activeTab === 'counsellors'" class="counsellors-content">
                <div class="counsellors-grid">
                  <div v-for="counsellor in counsellors" :key="counsellor.name" class="counsellor-card">
            <div class="counsellor-header">
                      <div class="counsellor-avatar">{{ getInitials(counsellor.name) }}</div>
                      <div class="counsellor-info">
                <div class="counsellor-name">{{ counsellor.name }}</div>
                        <div class="counsellor-stats">{{ counsellor.evaluations.length }} evaluations</div>
              </div>
                      <div class="counsellor-score">{{ counsellor.avgScore }}%</div>
            </div>
                    <div class="counsellor-metrics">
                      <div class="metric">
                        <div class="metric-label">Avg Score</div>
                        <div class="metric-value">{{ counsellor.avgScore }}%</div>
          </div>
                      <div class="metric">
                        <div class="metric-label">Evaluations</div>
                        <div class="metric-value">{{ counsellor.evaluations.length }}</div>
        </div>
                      <div class="metric">
                        <div class="metric-label">Last Review</div>
                        <div class="metric-value">{{ formatDate(counsellor.lastReview) }}</div>
      </div>
                    </div>
                    <div class="counsellor-actions">
                      <button class="btn btn--secondary btn--sm" @click="viewCounsellorDetails(counsellor)">View Details</button>
                    </div>
                  </div>
                </div>
                
                <!-- Additional content to ensure scrolling -->
                <div class="scroll-indicator">
                  <div class="scroll-content">
                    <h3>Performance Analytics</h3>
                    <p>Detailed performance metrics and analytics for all counsellors are displayed above. Use the scroll functionality to view additional content and ensure all data is accessible.</p>
                    
                    <div class="analytics-summary">
                      <div class="summary-card">
                        <h4>Overall Performance</h4>
                        <p>Average performance across all counsellors: {{ averageScore }}%</p>
                      </div>
                      <div class="summary-card">
                        <h4>Total Evaluations</h4>
                        <p>Completed evaluations: {{ totalEvaluations }}</p>
                      </div>
                      <div class="summary-card">
                        <h4>Pending Reviews</h4>
                        <p>Reviews awaiting completion: {{ pendingEvaluations }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
    </div>

    <!-- Evaluation Modal -->
    <div v-if="showEvaluationModal" class="modal-overlay" @click="closeEvaluationModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>{{ isEditMode ? 'Edit Evaluation' : 'New Evaluation' }}</h2>
          <button class="close-btn" @click="closeEvaluationModal">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="evaluation-form">
            <div class="call-info">
              <h3>Call #{{ selectedCall?.id }}</h3>
              <p><strong>Counsellor:</strong> {{ selectedCall?.agent.name }}</p>
              <p><strong>Issue Type:</strong> {{ selectedCall?.issueType }}</p>
              <p><strong>Date:</strong> {{ formatDateTime(selectedCall?.dateTime) }}</p>
            </div>
            
            <div class="evaluation-criteria">
              <h4>Evaluation Criteria</h4>
              <div v-for="criterion in evaluationCriteria" :key="criterion.id" class="criterion-row">
                <div class="criterion-info">
                  <div class="criterion-name">{{ criterion.name }}</div>
                  <div class="criterion-description">{{ criterion.description }}</div>
                </div>
                <div class="criterion-score">
                  <input 
                    type="range" 
                    :min="0" 
                    :max="100" 
                    v-model.number="criterion.score"
                    class="score-slider"
                  />
                  <div class="score-display">{{ criterion.score }}%</div>
                </div>
              </div>
            </div>
            
                    <div class="overall-score" :class="getScoreClass(overallScore)">
                      <h4>Overall Score: {{ overallScore }}%</h4>
                      <div class="score-indicator">
                        <span v-if="overallScore >= 80">Excellent</span>
                        <span v-else-if="overallScore >= 60">Good</span>
                        <span v-else-if="overallScore >= 40">Average</span>
                        <span v-else>Needs Improvement</span>
                      </div>
                    </div>
            
            <div class="evaluation-notes">
              <label>Notes</label>
              <textarea v-model="evaluationNotes" placeholder="Add evaluation notes..." rows="4"></textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn--secondary" @click="closeEvaluationModal">Cancel</button>
          <button class="btn btn--primary" @click="submitEvaluation" :disabled="!canSubmitEvaluation">
            {{ isEditMode ? 'Update' : 'Submit' }} Evaluation
          </button>
        </div>
      </div>
    </div>

    <!-- Call Details Modal -->
    <div v-if="showCallDetailsModal" class="modal-overlay" @click="closeCallDetailsModal">
      <div class="modal" @click.stop>
        <div class="modal-header">
          <h2>Call Details</h2>
          <button class="close-btn" @click="closeCallDetailsModal">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div v-if="selectedCallDetails" class="call-details">
            <div class="call-header">
              <h3>Call #{{ selectedCallDetails.id }}</h3>
              <div class="call-status" :class="selectedCallDetails.isEvaluated ? 'evaluated' : 'pending'">
                {{ selectedCallDetails.isEvaluated ? 'Evaluated' : 'Pending Review' }}
            </div>
          </div>
            
            <div class="call-info-grid">
              <div class="info-item">
                <label>Counsellor</label>
                <div class="counsellor-info">
                  <div class="counsellor-avatar">{{ getInitials(selectedCallDetails.agent.name) }}</div>
                  <span>{{ selectedCallDetails.agent.name }}</span>
        </div>
      </div>
              <div class="info-item">
                <label>Date & Time</label>
                <span>{{ formatDateTime(selectedCallDetails.dateTime) }}</span>
            </div>
              <div class="info-item">
                <label>Duration</label>
                <span>{{ selectedCallDetails.duration }}</span>
            </div>
              <div class="info-item">
                <label>Issue Type</label>
                <span class="issue-badge">{{ selectedCallDetails.issueType }}</span>
            </div>
            </div>
            
            <div v-if="selectedCallDetails.evaluation" class="evaluation-details">
              <h4>Evaluation Results</h4>
              <div class="evaluation-scores">
                <div v-for="(score, key) in selectedCallDetails.evaluation.scores" :key="key" class="score-item">
                  <div class="score-label">{{ formatCategory(key) }}</div>
                  <div class="score-bar">
                    <div class="score-fill" :style="{ width: score + '%' }"></div>
            </div>
                  <div class="score-value">{{ score }}%</div>
        </div>
      </div>
              <div class="evaluation-notes">
                <label>Notes</label>
                <p>{{ selectedCallDetails.evaluation.notes }}</p>
    </div>
              <div class="evaluation-meta">
                <div class="meta-item">
                  <label>Evaluated By</label>
                  <span>{{ selectedCallDetails.evaluation.evaluatedBy }}</span>
                </div>
                <div class="meta-item">
                  <label>Evaluation Date</label>
                  <span>{{ formatDateTime(selectedCallDetails.evaluation.evaluationDate) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn--secondary" @click="closeCallDetailsModal">Close</button>
          <button v-if="!selectedCallDetails?.isEvaluated" class="btn btn--primary" @click="startEvaluationFromDetails">
            Start Evaluation
          </button>
          <button v-else class="btn btn--primary" @click="editEvaluationFromDetails">
            Edit Evaluation
          </button>
        </div>
      </div>
    </div>
  </div>
</div>
</template>

<script setup>
import SidePanel from '../components/SidePanel.vue'
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'

// Reactive state
const activeTab = ref('dashboard')
const showEvaluationModal = ref(false)
const showCallDetailsModal = ref(false)
const selectedCall = ref(null)
const selectedCallDetails = ref(null)
const searchQuery = ref('')
const statusFilter = ref('all')
const chartPeriod = ref('week')
const evaluationNotes = ref('')
const isEditMode = ref(false)

// Sidebar state
const isSidebarCollapsed = ref(false)
const userRole = ref('user')
const isInQueue = ref(false)
const isProcessingQueue = ref(false)
const currentCall = ref(null)

// Tabs configuration
const tabs = ref([
  { 
    id: 'dashboard', 
    name: 'Dashboard',
    icon: 'M3 3h18v18H3V3zm2 2v14h14V5H5zm2 2h10v2H7V7zm0 4h10v2H7v-2zm0 4h7v2H7v-2z'
  },
  { 
    id: 'evaluations', 
    name: 'Evaluations',
    icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z'
  },
  { 
    id: 'counsellors', 
    name: 'Counsellors',
    icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z'
  }
])

// Evaluation criteria
const evaluationCriteria = ref([
  {
    id: 1,
    name: 'Opening',
    description: 'Professional greeting, introduction, and call setup',
            score: 50
  },
  {
    id: 2,
    name: 'Active Listening',
    description: 'Demonstrates understanding and empathy',
            score: 50
  },
  {
    id: 3,
    name: 'Proactive Questioning',
    description: 'Asks relevant questions to understand the situation',
            score: 50
  },
  {
    id: 4,
    name: 'Problem Resolution',
    description: 'Provides appropriate solutions and resources',
            score: 50
  },
  {
    id: 5,
    name: 'Call Closing',
    description: 'Professional closure with follow-up information',
            score: 50
          }
        ])

// Sample calls database
const callsDatabase = ref([
  {
    id: '12345',
    agent: {
      name: 'Patience Williams',
      avatar: '/placeholder.svg?height=40&width=40'
    },
    caller: {
      name: 'Sarah Johnson',
      phone: '+1-555-0123'
    },
    dateTime: new Date('2024-12-07T09:30:00'),
    duration: '8:32',
    issueType: 'Domestic Violence',
    isEvaluated: false,
    recordingUrl: '/sample-recording.mp3'
  },
  {
    id: '12346',
    agent: {
      name: 'Berna Johnson',
      avatar: '/placeholder.svg?height=40&width=40'
    },
    caller: {
      name: 'Michael Davis',
      phone: '+1-555-0124'
    },
    dateTime: new Date('2024-12-07T10:15:00'),
    duration: '16:45',
    issueType: 'Crisis Support',
    isEvaluated: true,
    recordingUrl: '/sample-recording.mp3',
    evaluation: {
      overallScore: 72,
      scores: {
        opening: 75,
        listening: 78,
        proactive: 65,
        resolution: 75,
        closing: 70
      },
      notes: 'Good rapport building. Could improve on proactive questioning and resource offering.',
      evaluatedBy: 'Isaac Martinez',
      evaluationDate: new Date('2024-12-07T11:00:00')
    }
  },
  {
    id: '12347',
    agent: {
      name: 'Julie Smith',
      avatar: '/placeholder.svg?height=40&width=40'
    },
    caller: {
      name: 'Emily Wilson',
      phone: '+1-555-0125'
    },
    dateTime: new Date('2024-12-07T11:20:00'),
    duration: '7:35',
    issueType: 'Information Request',
    isEvaluated: false,
    recordingUrl: '/sample-recording.mp3'
  },
  {
    id: '12348',
    agent: {
      name: 'Viola Davis',
      avatar: '/placeholder.svg?height=40&width=40'
    },
    caller: {
      name: 'Robert Brown',
      phone: '+1-555-0126'
    },
    dateTime: new Date('2024-12-07T14:30:00'),
    duration: '12:18',
    issueType: 'Emergency Support',
    isEvaluated: true,
    recordingUrl: '/sample-recording.mp3',
    evaluation: {
      overallScore: 92,
      scores: {
        opening: 95,
        listening: 92,
        proactive: 90,
        resolution: 94,
        closing: 89
      },
      notes: 'Outstanding performance across all categories. Excellent crisis management and resource coordination.',
      evaluatedBy: 'Milly Rodriguez',
      evaluationDate: new Date('2024-12-07T15:15:00')
    }
  },
  {
    id: '12349',
    agent: {
      name: 'Charles Wilson',
      avatar: '/placeholder.svg?height=40&width=40'
    },
    caller: {
      name: 'Lisa Anderson',
      phone: '+1-555-0127'
    },
    dateTime: new Date('2024-12-07T16:45:00'),
    duration: '14:22',
    issueType: 'Legal Assistance',
    isEvaluated: false,
    recordingUrl: '/sample-recording.mp3'
  },
  {
    id: '12350',
    agent: {
      name: 'Patience Williams',
      avatar: '/placeholder.svg?height=40&width=40'
    },
    caller: {
      name: 'Thomas Wright',
      phone: '+1-555-0128'
    },
    dateTime: new Date('2024-12-08T08:15:00'),
    duration: '9:47',
    issueType: 'Mental Health Support',
    isEvaluated: true,
    recordingUrl: '/sample-recording.mp3',
    evaluation: {
      overallScore: 85,
      scores: {
        opening: 88,
        listening: 85,
        proactive: 82,
        resolution: 87,
        closing: 83
      },
      notes: 'Excellent empathy and active listening skills. Strong resource coordination.',
      evaluatedBy: 'Sarah Martinez',
      evaluationDate: new Date('2024-12-08T09:00:00')
    }
  },
  {
    id: '12351',
    agent: {
      name: 'Julie Smith',
      avatar: '/placeholder.svg?height=40&width=40'
    },
    caller: {
      name: 'Maria Garcia',
      phone: '+1-555-0129'
    },
    dateTime: new Date('2024-12-08T10:30:00'),
    duration: '13:25',
    issueType: 'Housing Assistance',
    isEvaluated: true,
    recordingUrl: '/sample-recording.mp3',
    evaluation: {
      overallScore: 68,
      scores: {
        opening: 70,
        listening: 72,
        proactive: 60,
        resolution: 68,
        closing: 70
      },
      notes: 'Good basic skills but needs improvement in proactive questioning and resource knowledge.',
      evaluatedBy: 'David Chen',
      evaluationDate: new Date('2024-12-08T11:15:00')
    }
  }
])

const topPerformers = ref([
  { id: 1, name: 'Viola Davis', score: 93, evaluations: 8 },
  { id: 2, name: 'Patience Williams', score: 85, evaluations: 6 },
  { id: 3, name: 'Charles Wilson', score: 78, evaluations: 4 },
  { id: 4, name: 'Berna Johnson', score: 77, evaluations: 5 },
  { id: 5, name: 'Julie Smith', score: 72, evaluations: 3 }
])

// Computed properties
const filteredCalls = computed(() => {
  let filtered = callsDatabase.value

  if (statusFilter.value !== 'all') {
    filtered = filtered.filter(call => {
      if (statusFilter.value === 'evaluated') {
        return call.isEvaluated
      } else {
        return !call.isEvaluated
      }
    })
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(call =>
      call.id.includes(query) ||
      call.agent.name.toLowerCase().includes(query) ||
      call.caller.name.toLowerCase().includes(query) ||
      call.issueType.toLowerCase().includes(query)
    )
  }

  return filtered
})

        const counsellors = computed(() => {
          const map = {}
          callsDatabase.value.forEach(call => {
            const name = call.agent.name
            if (!map[name]) {
              map[name] = {
                name,
                avatar: call.agent.avatar,
        evaluations: [],
                avgScore: 0,
                lastReview: null
              }
            }
            if (call.evaluation) {
              map[name].evaluations.push(call.evaluation)
              map[name].lastReview = call.evaluation.evaluationDate
            }
          })
          
          Object.values(map).forEach(c => {
            if (c.evaluations.length) {
              c.avgScore = Math.round(c.evaluations.reduce((sum, e) => sum + (e.overallScore || 0), 0) / c.evaluations.length)
            }
          })
          return Object.values(map).sort((a, b) => b.avgScore - a.avgScore)
        })

const totalCounsellors = computed(() => counsellors.value.length)
const totalEvaluations = computed(() => callsDatabase.value.filter(call => call.isEvaluated).length)
const pendingEvaluations = computed(() => callsDatabase.value.filter(call => !call.isEvaluated).length)

const averageScore = computed(() => {
  const evaluatedCalls = callsDatabase.value.filter(call => call.isEvaluated)
  if (evaluatedCalls.length === 0) return 0
  const total = evaluatedCalls.reduce((sum, call) => sum + call.evaluation.overallScore, 0)
  return Math.round(total / evaluatedCalls.length)
})

const overallScore = computed(() => {
  const total = evaluationCriteria.value.reduce((sum, criterion) => sum + parseInt(criterion.score || 0), 0)
  return Math.round(total / evaluationCriteria.value.length)
})

const canSubmitEvaluation = computed(() => {
          return evaluationCriteria.value.every(criterion => criterion.score >= 0 && criterion.score <= 100)
        })

// Methods
const refreshData = () => {
  // Simulate data refresh
  console.log('Refreshing QA data...')
}

const startEvaluation = (call) => {
  selectedCall.value = call
  isEditMode.value = false
  
          // Reset all criteria scores to 50 (neutral starting point)
  evaluationCriteria.value.forEach(criterion => {
            criterion.score = 50
  })
  
  evaluationNotes.value = ''
  showEvaluationModal.value = true
}

const editEvaluation = (call) => {
  selectedCall.value = call
  isEditMode.value = true

  if (call.evaluation && call.evaluation.scores) {
    // Map the scores back to the criteria
    evaluationCriteria.value[0].score = call.evaluation.scores.opening || 0
    evaluationCriteria.value[1].score = call.evaluation.scores.listening || 0  
    evaluationCriteria.value[2].score = call.evaluation.scores.proactive || 0
    evaluationCriteria.value[3].score = call.evaluation.scores.resolution || 0
    evaluationCriteria.value[4].score = call.evaluation.scores.closing || 0
    
    evaluationNotes.value = call.evaluation.notes || ''
  }

  showEvaluationModal.value = true
}

const submitEvaluation = () => {
  if (selectedCall.value && canSubmitEvaluation.value) {
    // Create evaluation object
    const evaluation = {
      overallScore: overallScore.value,
      scores: {},
      notes: evaluationNotes.value,
      evaluatedBy: 'Current User',
      evaluationDate: new Date()
    }
    
    // Map criteria scores
    evaluationCriteria.value.forEach(criterion => {
      let key = criterion.name.toLowerCase().replace(/\s+/g, '').replace('active', '').replace('problem', '')
      if (key === 'listening') key = 'listening'
      if (key === 'questioning') key = 'proactive'
      if (key === 'resolution') key = 'resolution'
      if (key === 'closing') key = 'closing'
      if (key === 'opening') key = 'opening'
      evaluation.scores[key] = parseInt(criterion.score)
    })
    
    // Update the call in database
    const callIndex = callsDatabase.value.findIndex(call => call.id === selectedCall.value.id)
    if (callIndex !== -1) {
      callsDatabase.value[callIndex].isEvaluated = true
      callsDatabase.value[callIndex].evaluation = evaluation
    }
    
    closeEvaluationModal()
  }
}

const closeEvaluationModal = () => {
  showEvaluationModal.value = false
  selectedCall.value = null
  isEditMode.value = false
}

const viewCallDetails = (call) => {
  selectedCallDetails.value = call
  showCallDetailsModal.value = true
}

const closeCallDetailsModal = () => {
  showCallDetailsModal.value = false
  selectedCallDetails.value = null
}

        const startEvaluationFromDetails = () => {
          if (selectedCallDetails.value) {
            selectedCall.value = selectedCallDetails.value
            isEditMode.value = false
            evaluationCriteria.value.forEach(criterion => {
              criterion.score = 50
            })
            evaluationNotes.value = ''
            closeCallDetailsModal()
            showEvaluationModal.value = true
          }
        }

const editEvaluationFromDetails = () => {
  if (selectedCallDetails.value) {
    editEvaluation(selectedCallDetails.value)
    closeCallDetailsModal()
  }
}

const viewCounsellorDetails = (counsellor) => {
  console.log('Viewing counsellor details:', counsellor.name)
  // Could open a modal or navigate to counsellor detail page
}

const getScoreClass = (score) => {
  if (score >= 80) return 'score-high'
  if (score >= 60) return 'score-medium'
  return 'score-low'
}

const formatCategory = (category) => {
  return category.charAt(0).toUpperCase() + category.slice(1)
}

        const formatDateTime = (date) => {
          if (!date) return 'N/A'
          return date.toLocaleString('en-US', {
    month: 'short', 
    day: 'numeric', 
            hour: '2-digit',
            minute: '2-digit'
          })
        }

        const formatDate = (date) => {
          if (!date) return 'N/A'
          return date.toLocaleDateString('en-US', {
            weekday: 'short',
    month: 'short',
    day: 'numeric',
            year: 'numeric'
          })
        }

const getInitials = (name) => {
  if (!name) return ''
  const parts = name.trim().split(' ')
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  return (parts[0][0] + parts[1][0]).toUpperCase()
}

// Sidebar methods
const handleQueueToggle = () => {
  isInQueue.value = !isInQueue.value
}

const handleLogout = () => {
  console.log('Logging out...')
}

const handleSidebarToggle = (collapsed) => {
  isSidebarCollapsed.value = collapsed
}

// Lifecycle
onMounted(() => {
  // Initialize component
})
</script>

<style>
@import url("@/styles/qa-statistics.css");

/* Ensure proper scrolling */
html, body {
  height: auto !important;
  min-height: 100vh;
  overflow-x: hidden;
  overflow-y: auto !important;
  position: relative;
}

/* Override any parent container constraints */
#app, .app-container, .main-wrapper {
  height: auto !important;
  min-height: 100vh;
  overflow-y: auto !important;
}

/* Enhanced QA Statistics Styles */
.main-content {
  margin-left: 250px;
  padding: 32px 32px 60px 32px;
  background: var(--color-bg);
  min-height: 100vh;
  height: auto;
  overflow: visible;
  transition: margin-left 0.3s ease;
  position: relative;
}

.page-header {
  margin-bottom: 40px;
}

.page-title {
  font-size: 36px;
  font-weight: 800;
  color: var(--color-fg);
  margin: 0 0 12px 0;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.page-subtitle {
  font-size: 18px;
  color: var(--color-muted);
  margin: 0;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 40px;
}

.kpi-card {
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: 20px;
  padding: 32px;
  display: flex;
  align-items: center;
  gap: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.kpi-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--color-primary);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  border-color: var(--color-primary);
}

.kpi-card:hover::before {
  opacity: 1;
}

.kpi-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  background: rgba(139, 69, 19, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-primary);
  flex-shrink: 0;
  box-shadow: 0 2px 8px rgba(139, 69, 19, 0.2);
}

.kpi-content {
  flex: 1;
}

.kpi-value {
  font-size: 32px;
  font-weight: 900;
  color: var(--color-fg);
  margin-bottom: 6px;
  line-height: 1;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.kpi-label {
  font-size: 13px;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  font-weight: 700;
}

/* Content Tabs */
.content-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 32px;
  border-bottom: 2px solid var(--color-border);
  background: var(--color-surface);
  border-radius: 12px 12px 0 0;
  padding: 8px 8px 0 8px;
}

.tab-button {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 24px;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  color: var(--color-muted);
  font-weight: 700;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s ease;
  border-radius: 8px 8px 0 0;
  position: relative;
}

.tab-button:hover {
  color: var(--color-fg);
  background: rgba(139, 69, 19, 0.05);
}

.tab-button.active {
  color: var(--color-primary);
  border-bottom-color: var(--color-primary);
  background: rgba(139, 69, 19, 0.08);
}

/* Dashboard Content */
.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 40px;
}

.charts-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}

.chart-card {
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.chart-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  border-color: var(--color-primary);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.chart-header h3 {
  font-size: 20px;
  font-weight: 800;
  color: var(--color-fg);
  margin: 0;
  letter-spacing: -0.01em;
}

.chart-controls {
  display: flex;
  gap: 8px;
}

.chart-btn {
  padding: 8px 16px;
  background: var(--color-surface-muted);
  border: 2px solid var(--color-border);
  border-radius: 10px;
  color: var(--color-muted);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.chart-btn:hover {
  color: var(--color-fg);
  border-color: var(--color-primary);
  background: rgba(139, 69, 19, 0.05);
}

.chart-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(139, 69, 19, 0.3);
}

.chart-placeholder {
  height: 240px;
  background: var(--color-surface-muted);
  border-radius: 16px;
  position: relative;
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.chart-mock {
  position: relative;
  width: 100%;
  height: 100%;
}

.chart-line {
  position: absolute;
  top: 50%;
  left: 10%;
  right: 10%;
  height: 2px;
  background: var(--color-primary);
  transform: translateY(-50%);
}

.chart-points {
  position: relative;
  width: 100%;
  height: 100%;
}

.chart-point {
  position: absolute;
  width: 8px;
  height: 8px;
  background: var(--color-primary);
  border-radius: 50%;
  transform: translate(-50%, 50%);
}

/* Score Distribution */
.score-distribution {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.score-bar {
  display: flex;
  align-items: center;
  gap: 16px;
}

.score-label {
  min-width: 160px;
  font-size: 15px;
  font-weight: 700;
  color: var(--color-fg);
}

.score-progress {
  flex: 1;
  height: 12px;
  background: var(--color-surface-muted);
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--color-border);
}

.score-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.4s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.score-count {
  min-width: 40px;
  text-align: right;
  font-weight: 800;
  font-size: 16px;
  color: var(--color-fg);
}

/* Top Performers */
.top-performers h3 {
  font-size: 24px;
  font-weight: 800;
  color: var(--color-fg);
  margin: 0 0 24px 0;
  letter-spacing: -0.01em;
}

.performers-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.performer-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: 16px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.performer-card:hover {
  transform: translateX(6px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border-color: var(--color-primary);
}

.performer-rank {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(139, 69, 19, 0.3);
}

.performer-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 18px;
  box-shadow: 0 2px 8px rgba(139, 69, 19, 0.3);
}

.performer-info {
  flex: 1;
}

.performer-name {
  font-weight: 700;
  font-size: 16px;
  color: var(--color-fg);
  margin-bottom: 6px;
}

.performer-stats {
  font-size: 14px;
  color: var(--color-muted);
  font-weight: 600;
}

.performer-score {
  font-size: 20px;
  font-weight: 800;
  color: var(--color-primary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Evaluations Content */
.evaluations-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.evaluations-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-filters {
  display: flex;
  gap: 20px;
  align-items: center;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-box svg {
  position: absolute;
  left: 16px;
  color: var(--color-muted);
  z-index: 1;
}

.search-box input {
  padding: 14px 16px 14px 48px;
  border: 2px solid var(--color-border);
  border-radius: 12px;
  background: var(--color-surface);
  color: var(--color-fg);
  font-size: 15px;
  font-weight: 500;
  width: 320px;
  transition: all 0.3s ease;
}

.search-box input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(139, 69, 19, 0.1);
}

.filter-buttons {
  display: flex;
  gap: 12px;
}

.filter-btn {
  padding: 12px 20px;
  background: var(--color-surface-muted);
  border: 2px solid var(--color-border);
  border-radius: 10px;
  color: var(--color-muted);
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.filter-btn:hover {
  color: var(--color-fg);
  border-color: var(--color-primary);
  background: rgba(139, 69, 19, 0.05);
}

.filter-btn.active {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(139, 69, 19, 0.3);
}

/* Evaluations Table */
.evaluations-table-container {
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.evaluations-table {
  width: 100%;
  border-collapse: collapse;
}

.evaluations-table th {
  background: var(--color-surface-muted);
  padding: 20px 24px;
  text-align: left;
  font-weight: 800;
  color: var(--color-fg);
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  border-bottom: 2px solid var(--color-border);
}

.evaluations-table td {
  padding: 20px 24px;
  border-bottom: 1px solid var(--color-border);
  color: var(--color-fg);
  font-size: 15px;
  font-weight: 500;
}

.evaluations-table tr:hover td {
  background: rgba(139, 69, 19, 0.03);
}

.evaluations-table tr:last-child td {
  border-bottom: none;
}

.call-id {
  font-weight: 800;
  font-size: 16px;
  color: var(--color-primary);
}

.counsellor-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.counsellor-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 14px;
  box-shadow: 0 2px 8px rgba(139, 69, 19, 0.3);
}

.counsellor-name {
  font-weight: 700;
  font-size: 15px;
  color: var(--color-fg);
}

.issue-badge {
  padding: 6px 12px;
  background: rgba(139, 69, 19, 0.15);
  color: var(--color-primary);
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  border: 1px solid rgba(139, 69, 19, 0.2);
}

.score-circle {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 14px;
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.score-circle.score-high {
  background: var(--color-success);
}

.score-circle.score-medium {
  background: #fbbf24;
}

.score-circle.score-low {
  background: var(--color-danger);
}

.score-pending {
  color: var(--color-muted);
  font-style: italic;
  font-weight: 600;
}

.status-badge {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  border: 1px solid transparent;
}

.status-badge.evaluated {
  background: rgba(21, 128, 61, 0.15);
  color: var(--color-success);
  border-color: rgba(21, 128, 61, 0.2);
}

.status-badge.pending {
  background: rgba(255, 149, 0, 0.15);
  color: #ff9500;
  border-color: rgba(255, 149, 0, 0.2);
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.action-btn {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.action-btn.view-btn {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.action-btn.evaluate-btn {
  background: rgba(139, 69, 19, 0.15);
  color: var(--color-primary);
  border: 1px solid rgba(139, 69, 19, 0.2);
}

.action-btn.edit-btn {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.action-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

/* Counsellors Content */
.counsellors-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.counsellors-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.counsellor-card {
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: 20px;
  padding: 32px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.counsellor-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: var(--color-primary);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.counsellor-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  border-color: var(--color-primary);
}

.counsellor-card:hover::before {
  opacity: 1;
}

.counsellor-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
}

.counsellor-header .counsellor-avatar {
  width: 56px;
  height: 56px;
  font-size: 20px;
  box-shadow: 0 4px 12px rgba(139, 69, 19, 0.3);
}

.counsellor-header .counsellor-name {
  font-size: 20px;
  font-weight: 800;
  color: var(--color-fg);
  letter-spacing: -0.01em;
}

.counsellor-stats {
  font-size: 15px;
  color: var(--color-muted);
  font-weight: 600;
}

.counsellor-score {
  font-size: 28px;
  font-weight: 900;
  color: var(--color-primary);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.counsellor-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.metric {
  text-align: center;
  padding: 16px;
  background: var(--color-surface-muted);
  border-radius: 12px;
  border: 1px solid var(--color-border);
}

.metric-label {
  font-size: 12px;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.8px;
  font-weight: 700;
  margin-bottom: 8px;
}

.metric-value {
  font-size: 18px;
  font-weight: 800;
  color: var(--color-fg);
}

.counsellor-actions {
  display: flex;
  justify-content: center;
}

/* Scroll Indicator and Additional Content */
.scroll-indicator {
  margin-top: 40px;
  padding: 32px;
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.scroll-content h3 {
  font-size: 24px;
  font-weight: 800;
  color: var(--color-fg);
  margin: 0 0 16px 0;
  letter-spacing: -0.01em;
}

.scroll-content p {
  font-size: 16px;
  color: var(--color-muted);
  line-height: 1.6;
  margin: 0 0 24px 0;
}

.analytics-summary {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.summary-card {
  background: var(--color-surface-muted);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 20px;
  text-align: center;
}

.summary-card h4 {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-fg);
  margin: 0 0 8px 0;
}

.summary-card p {
  font-size: 14px;
  color: var(--color-muted);
  margin: 0;
  font-weight: 600;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--color-surface);
  border-radius: 16px;
  width: min(600px, 90vw);
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid var(--color-border);
}

.modal-header h2 {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-fg);
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: none;
  background: var(--color-surface-muted);
  color: var(--color-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.close-btn:hover {
  background: var(--color-border);
  color: var(--color-fg);
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 24px;
  border-top: 1px solid var(--color-border);
}

/* Evaluation Form */
.evaluation-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.call-info {
  background: var(--color-surface-muted);
  border-radius: 12px;
  padding: 20px;
}

.call-info h3 {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-fg);
  margin: 0 0 12px 0;
}

.call-info p {
  margin: 0 0 8px 0;
  color: var(--color-fg);
}

.evaluation-criteria {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.evaluation-criteria h4 {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-fg);
  margin: 0 0 16px 0;
}

.criterion-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.criterion-info {
  flex: 1;
}

.criterion-name {
  font-weight: 600;
  color: var(--color-fg);
  margin-bottom: 4px;
}

.criterion-description {
  font-size: 14px;
  color: var(--color-muted);
}

.criterion-score {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 120px;
}

.score-slider {
  flex: 1;
  height: 6px;
  background: var(--color-surface-muted);
  border-radius: 3px;
  outline: none;
  appearance: none;
  -webkit-appearance: none;
}

.score-slider::-webkit-slider-thumb {
  appearance: none;
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  background: var(--color-primary);
  border-radius: 50%;
  cursor: pointer;
}

.score-display {
  min-width: 40px;
  text-align: center;
  font-weight: 700;
  color: var(--color-primary);
}

.overall-score {
  background: var(--color-primary);
  color: white;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.overall-score.score-high {
  background: var(--color-success);
}

.overall-score.score-medium {
  background: #fbbf24;
}

.overall-score.score-low {
  background: var(--color-danger);
}

.overall-score h4 {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 8px 0;
}

.score-indicator {
  font-size: 14px;
  font-weight: 600;
  opacity: 0.9;
}

.evaluation-notes label {
  display: block;
  font-weight: 600;
  color: var(--color-fg);
  margin-bottom: 8px;
}

.evaluation-notes textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background: var(--color-surface);
  color: var(--color-fg);
  font-size: 14px;
  resize: vertical;
}

.evaluation-notes textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

/* Call Details */
.call-details {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.call-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.call-header h3 {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-fg);
  margin: 0;
}

.call-status {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 600;
}

.call-status.evaluated {
  background: rgba(21, 128, 61, 0.1);
  color: var(--color-success);
}

.call-status.pending {
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
}

.call-info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-item label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-item span {
  font-weight: 600;
  color: var(--color-fg);
}

.evaluation-details {
  background: var(--color-surface-muted);
  border-radius: 12px;
  padding: 20px;
}

.evaluation-details h4 {
  font-size: 16px;
  font-weight: 700;
  color: var(--color-fg);
  margin: 0 0 16px 0;
}

.evaluation-scores {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-label {
  min-width: 100px;
  font-weight: 600;
  color: var(--color-fg);
}

.score-bar {
  flex: 1;
  height: 8px;
  background: var(--color-surface);
  border-radius: 4px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: 4px;
}

.score-value {
  min-width: 40px;
  text-align: right;
  font-weight: 700;
  color: var(--color-primary);
}

.evaluation-notes label {
  display: block;
  font-weight: 600;
  color: var(--color-fg);
  margin-bottom: 8px;
}

.evaluation-notes p {
  margin: 0;
  color: var(--color-fg);
  line-height: 1.5;
}

.evaluation-meta {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-top: 16px;
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.meta-item label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.meta-item span {
  font-weight: 600;
  color: var(--color-fg);
}

/* Responsive Design */
@media (max-width: 1024px) {
  .main-content {
    margin-left: 0;
    padding: 24px 24px 60px 24px;
    height: auto;
    overflow: visible;
  }
  
  .page-title {
    font-size: 32px;
  }
  
  .page-subtitle {
    font-size: 16px;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .counsellors-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 20px 20px 60px 20px;
    height: auto;
    overflow: visible;
  }
  
  .page-title {
    font-size: 28px;
  }
  
  .kpi-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .kpi-card {
    padding: 24px;
  }
  
  .counsellors-grid {
    grid-template-columns: 1fr;
  }
  
  .search-filters {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .search-box input {
    width: 100%;
  }
  
  .filter-buttons {
    justify-content: center;
  }
  
  .call-info-grid {
    grid-template-columns: 1fr;
  }
  
  .evaluation-meta {
    grid-template-columns: 1fr;
  }
  
  .criterion-row {
    flex-direction: column;
    align-items: stretch;
    gap: 16px;
  }
  
  .criterion-score {
    min-width: auto;
  }
  
  .counsellor-metrics {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .analytics-summary {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .scroll-indicator {
    padding: 24px;
  }
  
  .evaluations-table th,
  .evaluations-table td {
    padding: 16px 20px;
  }
}
</style>

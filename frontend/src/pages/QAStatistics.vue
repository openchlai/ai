<template>
<div class="app-container" :data-theme="currentTheme">
  <SidePanel :userRole="userRole" :isInQueue="isInQueue" :isProcessingQueue="isProcessingQueue" :currentCall="currentCall" @toggle-queue="handleQueueToggle" @logout="handleLogout" @sidebar-toggle="handleSidebarToggle" />
  <div class="qa-statistics-container" :class="{ 'sidebar-collapsed': isSidebarCollapsed }" overflow-y="auto" height="100vh">
    <div class="header">
      <button class="back-btn glass-btn" v-if="selectedCounsellor || selectedCall" @click="handleBack">Back</button>
      <div class="page-title">QA Management System</div>
      <div class="header-actions">
        <button class="theme-toggle" @click="toggleTheme">
          <svg v-if="currentTheme === 'dark'" width="16" height="16" viewBox="0 0 24 24" fill="none">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" stroke="currentColor" stroke-width="2"/>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="5" stroke="currentColor" stroke-width="2"/>
            <line x1="12" y1="1" x2="12" y2="3" stroke="currentColor" stroke-width="2"/>
            <line x1="12" y1="21" x2="12" y2="23" stroke="currentColor" stroke-width="2"/>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" stroke="currentColor" stroke-width="2"/>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" stroke="currentColor" stroke-width="2"/>
            <line x1="1" y1="12" x2="3" y2="12" stroke="currentColor" stroke-width="2"/>
            <line x1="21" y1="12" x2="23" y2="12" stroke="currentColor" stroke-width="2"/>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" stroke="currentColor" stroke-width="2"/>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" stroke="currentColor" stroke-width="2"/>
          </svg>
          <span>{{ currentTheme === 'dark' ? 'Light Mode' : 'Dark Mode' }}</span>
        </button>
      </div>
    </div>
    <div class="qa-main-content">
      <!-- Step 1: Counsellors List -->
      <div v-if="!selectedCounsellor && !selectedCall" class="counsellors-section">
        <h3 class="section-title">All Counsellors</h3>
        <div class="counsellors-list">
          <div v-for="counsellor in counsellors" :key="counsellor.name" class="counsellor-card qa-card fine-border" @click="selectCounsellor(counsellor)">
            <div class="counsellor-header">
              <template v-if="counsellor.avatar">
                <img :src="counsellor.avatar" class="counsellor-avatar" @error="counsellor.avatar = null" />
              </template>
              <template v-else>
                <div class="counsellor-avatar initials-avatar">{{ getInitials(counsellor.name) }}</div>
              </template>
              <div>
                <div class="counsellor-name">{{ counsellor.name }}</div>
                <div class="counsellor-score">Avg. Score: {{ counsellor.avgScore }}%</div>
              </div>
            </div>
            <div class="counsellor-evals">Evaluations: {{ counsellor.evaluations.length }}</div>
          </div>
        </div>
      </div>
      <!-- Step 2: Calls List for Selected Counsellor -->
      <div v-else-if="selectedCounsellor && !selectedCall" class="calls-section">
        <h3 class="section-title">Calls by {{ selectedCounsellor.name }}</h3>
        <div class="calls-list">
          <div v-for="call in counsellorCalls" :key="call.id" class="call-card qa-card fine-border" @click="selectCall(call)">
            <div class="call-header">
                <span class="call-id">Call #{{ call.id }}</span>
              <span class="call-date">{{ formatDateTime(call.dateTime) }}</span>
              </div>
            <div class="call-score">Score: {{ call.evaluation?.overallScore ?? '-' }}%</div>
            <div class="call-issue">Issue: {{ call.issueType }}</div>
                </div>
                </div>
              </div>
      <!-- Step 3: Evaluation Details for Selected Call -->
      <div v-else-if="selectedCall" class="evaluation-section">
        <h3 class="section-title">Evaluation for Call #{{ selectedCall.id }}</h3>
        <div class="evaluation-details qa-card fine-border">
          <form @submit.prevent="saveEvaluation">
            <div v-for="(score, key) in editableScores" :key="key" class="modal-field">
              <label><strong>{{ formatCategory(key) }}:</strong></label>
              <input type="number" v-model.number="editableScores[key]" min="0" max="100" />
              </div>
            <div class="modal-field">
              <label><strong>Notes:</strong></label>
              <textarea v-model="editableNotes" rows="3"></textarea>
            </div>
            <div class="modal-field">
              <label><strong>Evaluated By:</strong></label>
              <input v-model="editableEvaluator" />
          </div>
            <div class="modal-field">
              <label><strong>Date:</strong></label>
              <input type="datetime-local" v-model="editableDate" />
        </div>
            <div class="modal-actions">
              <button type="submit">Save</button>
              <button type="button" @click="handleBack">Back</button>
              </div>
          </form>
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
const currentTheme = ref('dark')
const activeView = ref('cards')
const selectedCard = ref(null)
const showEvaluationModal = ref(false)
const showViewModal = ref(false)
const showCallDetailsModal = ref(false)
const showAgentDetailModal = ref(false)
const showDeleteModal = ref(false)
const showSuccessToast = ref(false)
const showErrorToast = ref(false)
const selectedCall = ref(null)
const selectedEvaluationCall = ref(null)
const selectedCallDetails = ref(null)
const selectedAgentDetail = ref(null)
const callToDelete = ref(null)
const callSearchQuery = ref('')
const selectedEvaluationStatus = ref('all')
const selectedAgent = ref('all')
const selectedDateRange = ref('today')
const evaluationNotes = ref('')
const isPlaying = ref(false)
const playbackProgress = ref(0)
const currentTime = ref('0:00')
const totalTime = ref('5:32')
const isEditMode = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

// Sidebar state
const isSidebarCollapsed = ref(false)
const mobileOpen = ref(false)
const userRole = ref('user')
const isInQueue = ref(false)
const isProcessingQueue = ref(false)
const currentCall = ref(null)

// View tabs configuration
const viewTabs = ref([
  { id: 'cards', name: 'View as Cards' },
  { id: 'calls', name: 'Evaluate Calls' },
  { id: 'analytics', name: 'Analytics' }
])

// Evaluation criteria
const evaluationCriteria = ref([
  {
    id: 1,
    name: 'Opening',
    description: 'Professional greeting, introduction, and call setup',
    score: 0
  },
  {
    id: 2,
    name: 'Active Listening',
    description: 'Demonstrates understanding and empathy',
    score: 0
  },
  {
    id: 3,
    name: 'Proactive Questioning',
    description: 'Asks relevant questions to understand the situation',
    score: 0
  },
  {
    id: 4,
    name: 'Problem Resolution',
    description: 'Provides appropriate solutions and resources',
    score: 0
  },
  {
    id: 5,
    name: 'Call Closing',
    description: 'Professional closure with follow-up information',
    score: 0
  }
])

// Performance categories for analytics
const performanceCategories = ref([
  { name: 'Opening', score: 82 },
  { name: 'Listening', score: 79 },
  { name: 'Proactive', score: 70 },
  { name: 'Resolution', score: 78 },
  { name: 'Closing', score: 77 }
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
  { id: 1, name: 'Viola Davis', score: 93 },
  { id: 2, name: 'Patience Williams', score: 85 },
  { id: 3, name: 'Charles Wilson', score: 78 },
  { id: 4, name: 'Berna Johnson', score: 77 },
  { id: 5, name: 'Julie Smith', score: 72 }
])

// Computed properties
const filteredCalls = computed(() => {
  let filtered = callsDatabase.value

  if (selectedEvaluationStatus.value !== 'all') {
    filtered = filtered.filter(call => {
      if (selectedEvaluationStatus.value === 'evaluated') {
        return call.isEvaluated
      } else {
        return !call.isEvaluated
      }
    })
  }

  if (selectedAgent.value !== 'all') {
    filtered = filtered.filter(call => 
      call.agent.name.toLowerCase().includes(selectedAgent.value)
    )
  }

  if (callSearchQuery.value) {
    const query = callSearchQuery.value.toLowerCase()
    filtered = filtered.filter(call =>
      call.id.includes(query) ||
      call.agent.name.toLowerCase().includes(query) ||
      call.caller.name.toLowerCase().includes(query) ||
      call.issueType.toLowerCase().includes(query)
    )
  }

  return filtered
})

const agentEvaluations = computed(() => {
  const agentMap = new Map()
  
  callsDatabase.value.filter(call => call.isEvaluated).forEach(call => {
    const agentName = call.agent.name
    if (!agentMap.has(agentName)) {
      agentMap.set(agentName, {
        id: agentName,
        agent: call.agent,
        evaluations: [],
        callsEvaluated: 0,
        totalScore: 0,
        averageScore: 0,
        averageTalkTime: '0:00',
        lastEvaluationDate: null,
        bestCategory: '',
        improvementArea: ''
      })
    }
    
    const agentData = agentMap.get(agentName)
    agentData.evaluations.push(call.evaluation)
    agentData.callsEvaluated = agentData.evaluations.length
    agentData.totalScore = agentData.evaluations.reduce((sum, evaluation) => sum + evaluation.overallScore, 0)
    agentData.averageScore = Math.round(agentData.totalScore / agentData.evaluations.length)
    agentData.averageTalkTime = '11:26'
    agentData.lastEvaluationDate = call.evaluation.evaluationDate

    // Calculate best and worst categories
    const categoryScores = {
      opening: 0,
      listening: 0,
      proactive: 0,
      resolution: 0,
      closing: 0
    }

    agentData.evaluations.forEach(evaluation => {
      Object.keys(categoryScores).forEach(category => {
        categoryScores[category] += evaluation.scores[category] || 0
      })
    })
    
    Object.keys(categoryScores).forEach(category => {
      categoryScores[category] = Math.round(categoryScores[category] / agentData.evaluations.length)
    })
    
    const sortedCategories = Object.entries(categoryScores).sort((a, b) => b[1] - a[1])
    agentData.bestCategory = formatCategory(sortedCategories[0][0])
    agentData.improvementArea = formatCategory(sortedCategories[sortedCategories.length - 1][0])
  })
  
  return Array.from(agentMap.values())
})

const overallScore = computed(() => {
  const total = evaluationCriteria.value.reduce((sum, criterion) => sum + parseInt(criterion.score || 0), 0)
  return Math.round(total / evaluationCriteria.value.length)
})

const totalEvaluations = computed(() => {
  return callsDatabase.value.filter(call => call.isEvaluated).length
})

const averageScore = computed(() => {
  const evaluatedCalls = callsDatabase.value.filter(call => call.isEvaluated)
  if (evaluatedCalls.length === 0) return 0
  const total = evaluatedCalls.reduce((sum, call) => sum + call.evaluation.overallScore, 0)
  return Math.round(total / evaluatedCalls.length)
})

const averageTalkTime = computed(() => {
  return '11:26'
})

const activeCounselors = computed(() => {
  const uniqueAgents = new Set(callsDatabase.value.map(call => call.agent.name))
  return uniqueAgents.size
})

const canSubmitEvaluation = computed(() => {
  return evaluationCriteria.value.every(criterion => criterion.score > 0)
})

// Sidebar computed properties
const queueStatus = computed(() => {
  if (currentCall.value) {
    return currentCall.value.status === 'incoming' ? 'Incoming Call' : 'On Call'
  }
  return isInQueue.value ? 'In Queue' : 'Offline'
})

const queueButtonText = computed(() => {
  if (isProcessingQueue.value) return 'Processing...'
  if (currentCall.value) return 'End Call'
  return isInQueue.value ? 'Leave Queue' : 'Join Queue'
})

// Add computed for all counsellors and evaluated calls
const counsellors = computed(() => {
  // Aggregate all unique agents from callsDatabase
  const map = {};
  callsDatabase.value.forEach(call => {
    const name = call.agent.name;
    if (!map[name]) {
      map[name] = {
        name,
        avatar: call.agent.avatar,
        evaluations: [],
        avgScore: 0
      };
    }
    if (call.evaluation) {
      map[name].evaluations.push(call.evaluation);
    }
  });
  // Calculate avg score
  Object.values(map).forEach(c => {
    if (c.evaluations.length) {
      c.avgScore = Math.round(c.evaluations.reduce((sum, e) => sum + (e.overallScore || 0), 0) / c.evaluations.length);
    }
  });
  return Object.values(map);
});
const evaluatedCalls = computed(() => callsDatabase.value.filter(call => call.evaluation));

// Editable evaluation state
const editableScores = ref({})
const editableNotes = ref('')
const editableEvaluator = ref('')
const editableDate = ref('')

watch(selectedCall, (call) => {
  if (call && call.evaluation) {
    editableScores.value = { ...call.evaluation.scores }
    editableNotes.value = call.evaluation.notes
    editableEvaluator.value = call.evaluation.evaluatedBy
    // Format date for input[type=datetime-local]
    const d = call.evaluation.evaluationDate
    editableDate.value = d ? new Date(d).toISOString().slice(0,16) : ''
  }
})

function saveEvaluation() {
  if (selectedCall.value && selectedCall.value.evaluation) {
    selectedCall.value.evaluation.scores = { ...editableScores.value }
    selectedCall.value.evaluation.notes = editableNotes.value
    selectedCall.value.evaluation.evaluatedBy = editableEvaluator.value
    selectedCall.value.evaluation.evaluationDate = new Date(editableDate.value)
    showEvaluationModal.value = false
    showSuccessMessage('Evaluation updated!')
  }
}

// Methods
const toggleTheme = () => {
  currentTheme.value = currentTheme.value === 'dark' ? 'light' : 'dark'
}

const setActiveView = (viewId) => {
  activeView.value = viewId
}

const openAgentDetailModal = (agentEvaluation) => {
  console.log('Opening agent detail modal for:', agentEvaluation.agent.name)
  selectedAgentDetail.value = agentEvaluation
  showAgentDetailModal.value = true
}

const closeAgentDetailModal = () => {
  console.log('Closing agent detail modal')
  showAgentDetailModal.value = false
  selectedAgentDetail.value = null
}

const startEvaluation = (call) => {
  console.log('Starting evaluation for call:', call.id)
  selectedCall.value = call
  isEditMode.value = false
  
  // Reset all criteria scores to 0
  evaluationCriteria.value.forEach(criterion => {
    criterion.score = 0
  })
  
  evaluationNotes.value = ''
  showEvaluationModal.value = true
}

const viewEvaluation = (call) => {
  selectedEvaluationCall.value = call
  showViewModal.value = true
}

const viewEvaluationDetail = (call) => {
  selectedEvaluationCall.value = call
  closeAgentDetailModal()
  showViewModal.value = true
}

const confirmDeleteCall = (call) => {
  callToDelete.value = call
  showDeleteModal.value = true
}

const closeDeleteModal = () => {
  showDeleteModal.value = false
  callToDelete.value = null
}

const confirmDelete = () => {
  if (callToDelete.value) {
    const index = callsDatabase.value.findIndex(c => c.id === callToDelete.value.id)
    if (index !== -1) {
      callsDatabase.value.splice(index, 1)
      showSuccessMessage(`Call #${callToDelete.value.id} has been deleted successfully.`)
    }
  }
  closeDeleteModal()
}

const closeEvaluationModal = () => {
  console.log('Closing evaluation modal')
  showEvaluationModal.value = false
  selectedCall.value = null
  isEditMode.value = false
}

const closeViewModal = () => {
  showViewModal.value = false
  selectedEvaluationCall.value = null
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
      criterion.score = 0
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

const updateOverallScore = () => {
  // This will trigger the computed property to recalculate
}

const editEvaluation = (call) => {
  console.log('Editing evaluation for call:', call.id)
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

  // Close other modals first
  showViewModal.value = false
  showAgentDetailModal.value = false
  showCallDetailsModal.value = false
  
  // Open evaluation modal
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
    
    const action = isEditMode.value ? 'updated' : 'submitted'
    showSuccessMessage(`Evaluation ${action} successfully for Call #${selectedCall.value.id}`)
  }
}

const togglePlayback = () => {
  isPlaying.value = !isPlaying.value
  // Simulate audio playback progress
  if (isPlaying.value) {
    const interval = setInterval(() => {
      if (playbackProgress.value < 100 && isPlaying.value) {
        playbackProgress.value += 1
        const totalSeconds = 332 // 5:32 in seconds
        const currentSeconds = Math.floor((playbackProgress.value / 100) * totalSeconds)
        const minutes = Math.floor(currentSeconds / 60)
        const seconds = currentSeconds % 60
        currentTime.value = `${minutes}:${seconds.toString().padStart(2, '0')}`
      } else {
        clearInterval(interval)
        if (playbackProgress.value >= 100) {
          isPlaying.value = false
          playbackProgress.value = 0
          currentTime.value = '0:00'
        }
      }
    }, 100)
  }
}

const getScoreClass = (score) => {
  if (score >= 80) return 'score-high'
  if (score >= 60) return 'score-medium'
  return 'score-low'
}

const formatCategory = (category) => {
  return category.charAt(0).toUpperCase() + category.slice(1)
}

const formatDate = (date) => {
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric', 
    year: 'numeric' 
  })
}

const formatDateTime = (date) => {
  return date.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getAgentCategoryScores = (agentDetail) => {
  const categoryScores = {
    opening: 0,
    listening: 0,
    proactive: 0,
    resolution: 0,
    closing: 0
  }

  if (agentDetail.evaluations.length > 0) {
    agentDetail.evaluations.forEach(evaluation => {
      Object.keys(categoryScores).forEach(category => {
        categoryScores[category] += evaluation.scores[category] || 0
      })
    })
    
    Object.keys(categoryScores).forEach(category => {
      categoryScores[category] = Math.round(categoryScores[category] / agentDetail.evaluations.length)
    })
  }

  return categoryScores
}

const getAgentRecentCalls = (agentName) => {
  return callsDatabase.value
    .filter(call => call.agent.name === agentName && call.isEvaluated)
    .sort((a, b) => new Date(b.dateTime) - new Date(a.dateTime))
    .slice(0, 5)
}

const generateAgentReport = () => {
  if (selectedAgentDetail.value) {
    showSuccessMessage(`Performance report generated for ${selectedAgentDetail.value.agent.name}`)
    closeAgentDetailModal()
  }
}

const showSuccessMessage = (message) => {
  successMessage.value = message
  showSuccessToast.value = true
  setTimeout(() => {
    showSuccessToast.value = false
  }, 3000)
}

const showErrorMessage = (message) => {
  errorMessage.value = message
  showErrorToast.value = true
  setTimeout(() => {
    showErrorToast.value = false
  }, 3000)
}

// Sidebar methods
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const expandSidebar = () => {
  isSidebarCollapsed.value = false
}

const toggleMobileMenu = () => {
  mobileOpen.value = !mobileOpen.value
}

const handleQueueToggle = () => {
  isInQueue.value = !isInQueue.value
}

const handleLogout = () => {
  showSuccessMessage('Logged out successfully')
}

// Lifecycle
onMounted(() => {
  // Initialize component
})

const router = useRouter()
function handleSidebarToggle(collapsed) {
  isSidebarCollapsed.value = collapsed
}

const selectedCounsellor = ref(null)
const counsellorCalls = computed(() => {
  if (!selectedCounsellor.value) return []
  return callsDatabase.value.filter(call => call.agent.name === selectedCounsellor.value.name)
})
function selectCounsellor(counsellor) {
  selectedCounsellor.value = counsellor
  selectedCall.value = null
}
function selectCall(call) {
  selectedCall.value = call
  // Set up editable fields for evaluation
  if (call.evaluation) {
    editableScores.value = { ...call.evaluation.scores }
    editableNotes.value = call.evaluation.notes
    editableEvaluator.value = call.evaluation.evaluatedBy
    const d = call.evaluation.evaluationDate
    editableDate.value = d ? new Date(d).toISOString().slice(0,16) : ''
  } else {
    editableScores.value = {}
    editableNotes.value = ''
    editableEvaluator.value = ''
    editableDate.value = ''
  }
}
function handleBack() {
  if (selectedCall.value) {
    selectedCall.value = null
  } else if (selectedCounsellor.value) {
    selectedCounsellor.value = null
  }
}

function getInitials(name) {
  if (!name) return ''
  const parts = name.trim().split(' ')
  if (parts.length === 1) return parts[0].slice(0, 2).toLowerCase()
  return (parts[0][0] + parts[1][0]).toLowerCase()
}
</script>

<style scoped>
.qa-statistics-container {
  transition: margin-left 0.3s, width 0.3s;
  margin-left: 250px;
  width: calc(100% - 250px);
  min-height: 100vh;
  background: var(--background-color);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  height: 100vh;
}
.qa-statistics-container.sidebar-collapsed {
  margin-left: 20px;
  width: calc(100% - 20px);
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 2rem 2.5rem 1.5rem 2.5rem;
  background: transparent;
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  z-index: 10;
}
.page-title {
  font-size: 2rem;
  font-weight: 800;
  color: var(--text-color);
  letter-spacing: 1px;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.theme-toggle {
  background: var(--content-bg);
  border: 1px solid var(--border-color);
  border-radius: 24px;
  padding: 0.5rem 1rem;
  font-weight: 700;
  color: var(--text-color);
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: background 0.2s, border 0.2s;
}
.theme-toggle:hover {
  background: var(--card-bg);
  border-color: var(--accent-color);
}

.qa-main-content {
  padding: 2rem 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
.qa-cards-row {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.qa-card {
  flex: 1 1 220px;
  min-width: 220px;
  background: var(--card-bg);
  border-radius: 24px;
  box-shadow: 0 4px 24px 0 rgba(30,126,52,0.08);
  border: 1.5px solid var(--border-color);
  padding: 2rem 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  transition: box-shadow 0.2s, border 0.2s;
}
.qa-card.fine-border {
  border: 1.5px solid var(--accent-color);
}
.qa-card .qa-card-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--accent-color);
  margin-bottom: 0.5rem;
}
.qa-card .qa-card-value {
  font-size: 2.2rem;
  font-weight: 900;
  color: var(--text-color);
  letter-spacing: 1px;
}

.qa-analytics-section {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}
.qa-analytics-card {
  background: var(--card-bg);
  border-radius: 24px;
  box-shadow: 0 4px 24px 0 rgba(30,126,52,0.08);
  border: 1.5px solid var(--border-color);
  padding: 2rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.qa-analytics-title {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--accent-color);
  margin-bottom: 1rem;
}
.qa-analytics-chart {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.qa-analytics-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.qa-analytics-label {
  min-width: 90px;
  font-weight: 600;
  color: var(--text-color);
}
.qa-analytics-bar-bg {
  flex: 1;
  height: 18px;
  background: var(--background-color);
  border-radius: 12px;
  overflow: hidden;
  margin: 0 0.5rem;
  border: 1px solid var(--border-color);
}
.qa-analytics-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--accent-color) 0%, var(--accent-hover) 100%);
  border-radius: 12px;
  transition: width 0.5s;
}
.qa-analytics-score {
  font-weight: 700;
  color: var(--accent-color);
}

.back-btn.glass-btn {
  background: var(--content-bg);
  border: 1.5px solid var(--accent-color);
  border-radius: 18px;
  color: var(--accent-color);
  font-weight: 700;
  padding: 0.5rem 1.2rem;
  box-shadow: 0 2px 8px 0 rgba(30,126,52,0.08);
  transition: background 0.2s, border 0.2s;
}
.back-btn.glass-btn:hover {
  background: var(--card-bg);
  border-color: var(--accent-hover);
}

@media (max-width: 900px) {
  .qa-statistics-container {
    margin-left: 0;
  width: 100%;
    padding: 0;
  }
  .qa-main-content {
    padding: 1rem;
    gap: 1.2rem;
  }
  .header {
    padding: 1.2rem 1rem 1rem 1rem;
  }
  .qa-cards-row {
  flex-direction: column;
    gap: 1rem;
  }
}

.counsellors-section {
  margin-top: 2rem;
}
.counsellors-list {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  overflow-x: auto;
  padding-bottom: 1rem;
}
.counsellor-card {
  min-width: 220px;
  max-width: 300px;
  flex: 1 1 220px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.counsellor-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.counsellor-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  object-fit: cover;
  background: var(--card-bg);
  border: 2px solid var(--accent-color);
}
.counsellor-name {
  font-weight: 700;
  color: var(--text-color);
}
.counsellor-score {
  font-size: 0.95rem;
  color: var(--accent-color);
}
.counsellor-evals {
  font-size: 0.95rem;
  color: var(--text-secondary);
}
.evaluations-section {
  margin-top: 2rem;
}
.evaluations-table {
  width: 100%;
  border-collapse: collapse;
  background: var(--card-bg);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.evaluations-table th, .evaluations-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border-color);
  text-align: left;
  color: var(--text-color);
}
.evaluations-table th {
  background: var(--content-bg);
  color: var(--accent-color);
  font-weight: 700;
}
.evaluations-table tr:last-child td {
  border-bottom: none;
}
.evaluations-table button {
  background: var(--accent-color);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.3rem 0.8rem;
  margin-right: 0.5rem;
  cursor: pointer;
  font-size: 0.95rem;
  transition: background 0.2s;
}
.evaluations-table button:hover {
  background: var(--accent-hover);
}
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: var(--card-bg);
  border-radius: 18px;
  padding: 2rem 2.5rem;
  min-width: 320px;
  max-width: 90vw;
  box-shadow: 0 4px 24px rgba(0,0,0,0.12);
  color: var(--text-color);
}
.scrollable-modal {
  max-height: 80vh;
  overflow-y: auto;
}
.modal-field {
  margin-bottom: 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}
.modal-field input,
.modal-field textarea {
  background: var(--background-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 0.5rem;
  font-size: 1rem;
  width: 100%;
}
.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}
.modal-actions button {
  background: var(--accent-color);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.5rem 1.2rem;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.modal-actions button[type='button'] {
  background: var(--border-color);
  color: var(--text-color);
}
.modal-actions button:hover {
  background: var(--accent-hover);
}
@media (max-width: 900px) {
  .counsellors-list {
    flex-wrap: nowrap;
    overflow-x: auto;
    gap: 1rem;
  }
  .counsellor-card {
    min-width: 220px;
    max-width: 80vw;
    flex: 0 0 220px;
  }
}

.calls-list {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin-top: 1.5rem;
}
.call-card {
  min-width: 220px;
  max-width: 320px;
  flex: 1 1 220px;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  cursor: pointer;
  transition: box-shadow 0.2s, border 0.2s;
}
.call-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.10);
  border-color: var(--accent-hover);
}
.call-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: var(--text-color);
}
.call-score {
  color: var(--accent-color);
  font-weight: 700;
}
.call-issue {
  color: var(--text-secondary);
  font-size: 0.95rem;
}
.evaluation-details {
  max-width: 480px;
  margin: 2rem auto;
  padding: 2rem 2.5rem;
}

.counsellor-avatar.initials-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--accent-color);
  color: #fff;
  font-weight: 700;
  font-size: 1.2rem;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  text-transform: uppercase;
}
</style>

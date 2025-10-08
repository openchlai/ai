<template>
  <div class="main-scroll-content">
    <!-- Page Header -->
    <div class="page-header glass-card fine-border">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">Case Management</h1>
          <p class="page-subtitle">Manage and track all cases in the system</p>
        </div>
        <div class="header-stats">
          <div class="stat-item">
            <span class="stat-value">{{ totalCases }}</span>
            <span class="stat-label">Total Cases</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ activeCases }}</span>
            <span class="stat-label">Active</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ resolvedCases }}</span>
            <span class="stat-label">Resolved</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Table Controls -->
    <div class="table-card glass-card fine-border">
      <div class="table-controls">
        <button class="create-case-btn" @click="showCreateCaseModal = true">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          Create Case
        </button>
        <div class="controls-right">
          <button class="filter-btn" @click="toggleCaseFilters">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="22,3 2,3 10,12.46 10,19 14,21 14,12.46"></polygon>
            </svg>
            Filters
            <span v-if="activeFiltersCount > 0" class="filter-badge">{{ activeFiltersCount }}</span>
          </button>
          <button class="export-btn" @click="exportCases">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
              <polyline points="7,10 12,15 17,10"></polyline>
              <line x1="12" y1="15" x2="12" y2="3"></line>
            </svg>
            Export
          </button>
        </div>
      </div>

      <!-- Case Filters -->
      <div v-if="showCaseFilters" class="case-filters">
        <div class="filters-row">
          <div class="filter-group">
            <label class="filter-label">Status</label>
            <select class="filter-select" v-model="caseFilters.status">
              <option value="">All Status</option>
              <option value="Open">Open</option>
              <option value="In Progress">In Progress</option>
              <option value="Resolved">Resolved</option>
              <option value="Closed">Closed</option>
            </select>
          </div>
          <div class="filter-group">
            <label class="filter-label">Priority</label>
            <select class="filter-select" v-model="caseFilters.priority">
              <option value="">All Priority</option>
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
              <option value="Critical">Critical</option>
            </select>
          </div>
          <div class="filter-group">
            <label class="filter-label">Assignee</label>
            <select class="filter-select" v-model="caseFilters.assignedTo">
              <option value="">All Assignees</option>
              <option v-for="user in teamMembers" :key="user.id" :value="user.name">
                {{ user.name }}
              </option>
            </select>
          </div>
          <div class="filter-group">
            <label class="filter-label">Search</label>
            <input
              class="filter-input"
              type="text"
              placeholder="Search cases..."
              v-model="caseFilters.search"
            />
          </div>
        </div>
        <div class="filters-actions">
          <button class="clear-filters-btn" @click="clearFilters">Clear All</button>
          <button class="apply-filters-btn" @click="applyFilters">Apply Filters</button>
        </div>
      </div>

      <!-- Cases Table -->
      <div class="table-container">
        <div v-if="filteredCases.length === 0" class="empty-state">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14,2 14,8 20,8"></polyline>
            <line x1="16" y1="13" x2="8" y2="13"></line>
            <line x1="16" y1="17" x2="8" y2="17"></line>
            <polyline points="10,9 9,9 8,9"></polyline>
          </svg>
          <h3>No cases found</h3>
          <p v-if="hasActiveFilters">Try adjusting your filters or search terms</p>
          <p v-else>Get started by creating your first case</p>
          <button class="create-case-btn" @click="showCreateCaseModal = true">Create Case</button>
        </div>
        
        <table v-else class="cases-table">
          <thead>
            <tr>
              <th>Case</th>
              <th>Client</th>
              <th>Status</th>
              <th>Priority</th>
              <th>Assigned To</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="case_ in filteredCases" :key="case_.id" class="case-row">
              <td>
                <div class="case-cell">
                  <div class="case-info">
                    <div class="case-number">{{ case_.caseNumber }}</div>
                    <div class="case-title">{{ case_.title }}</div>
                    <div class="case-category">{{ case_.category }}</div>
                  </div>
                </div>
              </td>
              <td>
                <div class="client-info">
                  <div class="client-name">{{ case_.clientName }}</div>
                  <div class="client-email" v-if="case_.clientEmail">{{ case_.clientEmail }}</div>
                </div>
              </td>
              <td>
                <span class="status-badge" :class="case_.status.toLowerCase()">
                  {{ case_.status }}
                </span>
              </td>
              <td>
                <span class="priority-badge" :class="case_.priority.toLowerCase()">
                  {{ case_.priority }}
                </span>
              </td>
              <td>
                <div class="assignee-info">
                  <div class="assignee-avatar">
                    {{ getInitials(case_.assignedTo) }}
                  </div>
                  <span>{{ case_.assignedTo }}</span>
                </div>
              </td>
              <td>
                <div class="date-info">
                  <div class="created-date">{{ formatDate(case_.createdAt) }}</div>
                  <div class="due-date" v-if="case_.dueDate">
                    Due: {{ formatDate(case_.dueDate) }}
                  </div>
                </div>
              </td>
              <td>
                <div class="case-actions">
                  <button class="action-btn view-btn" @click="viewCase(case_.id)" title="View Case">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                      <circle cx="12" cy="12" r="3"></circle>
                    </svg>
                  </button>
                  <button class="action-btn edit-btn" @click="editCase(case_.id)" title="Edit Case">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Create Case Modal -->
    <div v-if="showCreateCaseModal" class="modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Create New Case</h2>
          <button class="close-btn" @click="showCreateCaseModal = false">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        <div class="modal-body">
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Case Title *</label>
              <input
                class="form-input"
                type="text"
                v-model="newCase.title"
                placeholder="Enter case title"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Client Name *</label>
              <input
                class="form-input"
                type="text"
                v-model="newCase.clientName"
                placeholder="Enter client name"
              />
            </div>
            <div class="form-group">
              <label class="form-label">Category *</label>
              <select class="form-select" v-model="newCase.category">
                <option value="">Select category</option>
                <option v-for="category in categories" :key="category.id" :value="category.name">
                  {{ category.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Priority</label>
              <select class="form-select" v-model="newCase.priority">
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
                <option value="Critical">Critical</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Assign To</label>
              <select class="form-select" v-model="newCase.assignedTo">
                <option value="">Unassigned</option>
                <option v-for="user in teamMembers" :key="user.id" :value="user.name">
                  {{ user.name }}
                </option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Due Date</label>
              <input
                class="form-input"
                type="date"
                v-model="newCase.dueDate"
              />
            </div>
            <div class="form-group full-width">
              <label class="form-label">Description</label>
              <textarea
                class="form-textarea"
                v-model="newCase.description"
                placeholder="Enter case description"
                rows="4"
              ></textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showCreateCaseModal = false">Cancel</button>
          <button class="submit-btn" @click="createCase">Create Case</button>
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
const showCreateCaseModal = ref(false)
const showCaseFilters = ref(false)
const caseFilters = ref({
  status: '',
  priority: '',
  assignedTo: '',
  search: ''
})

const newCase = ref({
  title: '',
  clientName: '',
  category: '',
  priority: 'Medium',
  assignedTo: '',
  dueDate: '',
  description: ''
})

// Mock categories
const categories = ref([
  { id: 1, name: 'Child Protection' },
  { id: 2, name: 'Education Support' },
  { id: 3, name: 'Healthcare Access' },
  { id: 4, name: 'Family Support' },
  { id: 5, name: 'Emergency Response' }
])

// Computed properties
const totalCases = computed(() => Array.isArray(caseStore.cases) ? caseStore.cases.length : 0)
const activeCases = computed(() => (Array.isArray(caseStore.cases) ? caseStore.cases : []).filter(c => c.status === 'Open' || c.status === 'In Progress').length)
const resolvedCases = computed(() => (Array.isArray(caseStore.cases) ? caseStore.cases : []).filter(c => c.status === 'Resolved').length)
const teamMembers = computed(() => Array.isArray(userStore.users) ? userStore.users : [])

const filteredCases = computed(() => {
  const base = Array.isArray(caseStore.cases) ? caseStore.cases : []
  let filtered = base

  if (caseFilters.value.status) {
    filtered = filtered.filter(c => c.status === caseFilters.value.status)
  }
  if (caseFilters.value.priority) {
    filtered = filtered.filter(c => c.priority === caseFilters.value.priority)
  }
  if (caseFilters.value.assignedTo) {
    filtered = filtered.filter(c => c.assignedTo === caseFilters.value.assignedTo)
  }
  if (caseFilters.value.search) {
    const search = caseFilters.value.search.toLowerCase()
    filtered = filtered.filter(c => 
      (c.title || '').toLowerCase().includes(search) ||
      (c.caseNumber || '').toLowerCase().includes(search) ||
      (c.clientName || '').toLowerCase().includes(search)
    )
  }

  return filtered
})

const activeFiltersCount = computed(() => {
  return Object.values(caseFilters.value).filter(value => value !== '').length
})

const hasActiveFilters = computed(() => activeFiltersCount.value > 0)

// Methods
const toggleCaseFilters = () => {
  showCaseFilters.value = !showCaseFilters.value
}

const clearFilters = () => {
  caseFilters.value = {
    status: '',
    priority: '',
    assignedTo: '',
    search: ''
  }
}

const applyFilters = () => {
  showCaseFilters.value = false
}

const createCase = () => {
  if (!newCase.value.title || !newCase.value.clientName || !newCase.value.category) {
    alert('Please fill in all required fields')
    return
  }

  const caseNumber = `CASE-${new Date().getFullYear()}-${String(caseStore.cases.length + 1).padStart(3, '0')}`
  const newCaseObj = {
    caseNumber,
    title: newCase.value.title,
    clientName: newCase.value.clientName,
    category: newCase.value.category,
    priority: newCase.value.priority,
    assignedTo: newCase.value.assignedTo || 'Unassigned',
    dueDate: newCase.value.dueDate,
    description: newCase.value.description,
    createdAt: new Date().toISOString()
  }

  caseStore.createCase(newCaseObj).then(() => {
    caseStore.listCases()
    alert('Case created successfully!')
  }).catch(error => {
    console.error('Error creating case:', error)
    alert('Failed to create case. Please try again.')
  })

  newCase.value = {
    title: '',
    clientName: '',
    category: '',
    priority: 'Medium',
    assignedTo: '',
    dueDate: '',
    description: ''
  }
  showCreateCaseModal.value = false
}

const viewCase = (caseId) => {
  router.push(`/admin/cases/${caseId}`)
}

const editCase = (caseId) => {
  router.push(`/admin/cases/${caseId}/edit`)
}

const exportCases = () => {
  console.log('Exporting cases...')
  alert('Exporting cases to CSV...')
}

const getInitials = (name) => {
  if (!name || typeof name !== 'string') return ''
  return name
    .split(' ')
    .map(part => part[0])
    .join('')
    .toUpperCase()
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}

onMounted(async () => {
  await caseStore.listCases()
  await userStore.listUsers()
})
</script>

<style scoped>
/* Cases specific styles are inherited from global components.css */
</style>

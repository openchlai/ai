image.png<template>
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
    <div class="cases-container">
      <div class="header">
        <div class="header-left">
          <h1>Cases</h1>
          <router-link to="/case-creation" class="add-new-case-btn">
            Add New Case
          </router-link>
        </div>
        <button class="theme-toggle" @click="toggleTheme">
          <svg v-show="currentTheme === 'dark'" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <svg v-show="currentTheme === 'light'" width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="12" cy="12" r="5" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="1" x2="12" y2="3" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="12" y1="21" x2="12" y2="23" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="18.36" y1="18.36" x2="19.78" y2="19.78" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="1" y1="12" x2="3" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="21" y1="12" x2="23" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            <line x1="18.36" y1="5.64" x2="19.78" y2="4.22" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <span>{{ currentTheme === 'dark' ? 'Light Mode' : 'Dark Mode' }}</span>
        </button>
      </div>

      <div class="search-container" style="position: relative;">
        <span class="search-icon">
          <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        </span>
        <input 
          v-model="searchQuery"
          class="search-input" 
          placeholder="Search case by title, assignee, or filer..." 
          type="text"
          @input="handleSearch"
        />
      </div>

      <div class="filter-tabs">
        <button 
          v-for="filter in filters" 
          :key="filter.id"
          :class="['filter-tab', { active: activeFilter === filter.id }]"
          @click="setActiveFilter(filter.id)"
        >
          {{ filter.name }}
        </button>
      </div>

      <div class="cases-container-inner">
        <div class="cases-list">
          <h2 class="cases-title">Cases</h2>
          
          <div 
            v-for="caseItem in filteredCases" 
            :key="caseItem.id"
            :class="['case-item glass-card fine-border', { selected: selectedCaseId === caseItem.id }]"
            @click="selectCase(caseItem.id)"
          >
            <div class="case-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 22C12 22 20 18 20 12V5L12 2L4 5V12C4 18 12 22 12 22Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </div>
            <div class="case-details">
              <div class="case-title">{{ caseItem.title }}</div>
              <div class="case-meta">
                <span class="case-priority">
                  <span :class="['priority-dot', caseItem.priority.toLowerCase()]" />
                  {{ caseItem.priority }} priority
                </span>
                <span class="case-date">{{ caseItem.date }}</span>
                <span class="case-assigned">{{ caseItem.assignedTo ? `Assigned: ${caseItem.assignedTo}` : 'Unassigned' }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Side Drawer for Case Details -->
        <div class="case-detail-drawer" v-if="selectedCaseDetails">
          <div class="case-detail-drawer-header">
            <div class="case-detail-title">{{ selectedCaseDetails.caseTitle || selectedCaseDetails.title }}</div>
            <div class="case-detail-id">Case ID: {{ selectedCaseDetails.id }}</div>
            <button class="close-details" @click="selectedCaseId = null">×</button>
          </div>
          <div class="case-detail-content">
            <div class="detail-item">
              <div class="detail-label">Case Filer</div>
              <div class="detail-value">{{ selectedCaseDetails.caseFiler || 'N/A' }}</div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">Caseer</div>
              <div class="detail-value">{{ selectedCaseDetails.caseer || 'N/A' }}</div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">Case Priority</div>
              <div :class="['detail-value', selectedCaseDetails.priority.toLowerCase()]">{{ selectedCaseDetails.priority }}</div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">Jurisdiction</div>
              <div class="detail-value">{{ selectedCaseDetails.jurisdiction || 'N/A' }}</div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">Disposition</div>
              <div :class="['detail-value', { abusive: selectedCaseDetails.disposition === 'Abusive Call' }]">
                {{ selectedCaseDetails.disposition || 'N/A' }}
              </div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">Date</div>
              <div class="detail-value">{{ selectedCaseDetails.date || 'N/A' }}</div>
            </div>
            
            <div class="detail-item">
              <div class="detail-label">Escalated to</div>
              <div class="detail-value">{{ selectedCaseDetails.escalatedTo || 'N/A' }}</div>
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
import { useRouter } from 'vue-router'
import SidePanel from '@/components/SidePanel.vue'

const router = useRouter()

// Reactive state
const searchQuery = ref('')
const activeFilter = ref('all')
const selectedCaseId = ref('123456') // Default to first case
const currentTheme = ref(localStorage.getItem('theme') || 'dark')

// SidePanel related state
const userRole = ref('super-admin')
const isInQueue = ref(false)
const isProcessingQueue = ref(false)
const currentCall = ref(null)

// Filter options
const filters = ref([
  { id: 'all', name: 'All' },
  { id: 'open', name: 'Open', status: 'open' },
  { id: 'pending', name: 'Pending', status: 'pending' },
  { id: 'assigned', name: 'Assigned' },
  { id: 'closed', name: 'Closed', status: 'closed' },
  { id: 'today', name: 'Today' },
  { id: 'priority', name: 'Priority' }
])

// Sample cases data
const cases = ref([
  {
    id: '123456',
    title: 'Case #123456-GBV request',
    priority: 'High',
    assignedTo: 'Robert Jackson',
    caseTitle: 'Emergency call',
    caseFiler: 'Nelson Adega',
    caseer: 'Mitch Ngugi',
    jurisdiction: 'Judge- in Court',
    disposition: 'Abusive Call',
    date: '15th Aug 2025',
    escalatedTo: 'Ntaate Kimani'
  },
  {
    id: '789012',
    title: 'Case #789012 - Assault',
    priority: 'Medium',
    assignedTo: 'Sarah Mitchell',
    caseTitle: 'Assault Case',
    caseFiler: 'Jane Doe',
    caseer: 'John Smith',
    jurisdiction: 'District Court',
    disposition: 'Under Investigation',
    date: '14th Aug 2025',
    escalatedTo: 'Senior Detective'
  },
  {
    id: '345678-1',
    title: 'Case #345678-In-transit medical support',
    priority: 'Low',
    assignedTo: null,
    caseTitle: 'Medical Support',
    caseFiler: 'Medical Team',
    caseer: 'Emergency Services',
    jurisdiction: 'Emergency Response',
    disposition: 'Resolved',
    date: '13th Aug 2025',
    escalatedTo: 'Hospital Administration'
  },
  {
    id: '901234-1',
    title: 'Case #901234-battery coordination',
    priority: 'High',
    assignedTo: 'Michael Lee',
    caseTitle: 'Battery Case',
    caseFiler: 'Police Department',
    caseer: 'Detective Brown',
    jurisdiction: 'Criminal Court',
    disposition: 'Active Investigation',
    date: '16th Aug 2025',
    escalatedTo: 'District Attorney'
  },
  {
    id: '345678-2',
    title: 'Case #345678-In-transit medical support',
    priority: 'High',
    assignedTo: 'Michael Lee',
    caseTitle: 'Medical Emergency',
    caseFiler: 'Paramedic Team',
    caseer: 'Emergency Coordinator',
    jurisdiction: 'Emergency Response',
    disposition: 'In Progress',
    date: '16th Aug 2025',
    escalatedTo: 'Medical Director'
  },
  {
    id: '901234-2',
    title: 'Case #901234-Transport coordination',
    priority: 'High',
    assignedTo: 'Michael Lee',
    caseTitle: 'Transport Coordination',
    caseFiler: 'Transport Authority',
    caseer: 'Logistics Team',
    jurisdiction: 'Transport Commission',
    disposition: 'Pending Review',
    date: '12th Aug 2025',
    escalatedTo: 'Operations Manager'
  },
  {
    id: '901234-3',
    title: 'Case #901234-Transport coordination',
    priority: 'High',
    assignedTo: 'Michael Lee',
    caseTitle: 'Transport Emergency',
    caseFiler: 'Emergency Services',
    caseer: 'Transport Coordinator',
    jurisdiction: 'Emergency Response',
    disposition: 'Active',
    date: '16th Aug 2025',
    escalatedTo: 'Emergency Director'
  }
])

// Computed properties
const filteredCases = computed(() => {
  let filtered = cases.value

  // Search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(c => 
      c.title.toLowerCase().includes(query) ||
      (c.assignedTo && c.assignedTo.toLowerCase().includes(query)) ||
      (c.caseFiler && c.caseFiler.toLowerCase().includes(query))
    )
  }

  // Status filter
  if (activeFilter.value !== 'all') {
    const filterStatus = filters.value.find(f => f.id === activeFilter.value)?.status
    if (filterStatus) {
      filtered = filtered.filter(c => c.status === filterStatus)
    } else if (activeFilter.value === 'assigned') {
      filtered = filtered.filter(c => c.assignedTo)
    } else if (activeFilter.value === 'priority') {
      filtered = filtered.filter(c => c.priority === 'High')
    } else if (activeFilter.value === 'today') {
      // Filter for today's cases (simplified for demo)
      filtered = filtered.filter(c => c.date && c.date.includes('16th Aug 2025'))
    }
  }

  return filtered
})

const selectedCaseDetails = computed(() => {
  return cases.value.find(caseItem => caseItem.id === selectedCaseId.value)
})

// SidePanel event handlers
const handleQueueToggle = () => {
  isInQueue.value = !isInQueue.value
  console.log('Queue toggled:', isInQueue.value)
}

const handleLogout = () => {
  router.push('/')
}

const handleSidebarToggle = (collapsed) => {
  console.log('Sidebar toggled:', collapsed)
}

// Methods
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
    root.style.setProperty('--header-bg', '#f0f0f0')
    root.style.setProperty('--input-bg', '#f0f0f0')
    root.setAttribute('data-theme', 'light')
  } else {
    root.style.setProperty('--background-color', '#0a0a0a')
    root.style.setProperty('--sidebar-bg', '#111')
    root.style.setProperty('--content-bg', '#222')
    root.style.setProperty('--text-color', '#fff')
    root.style.setProperty('--text-secondary', '#aaa')
    root.style.setProperty('--border-color', '#333')
    root.style.setProperty('--card-bg', '#222')
    root.style.setProperty('--header-bg', '#333')
    root.style.setProperty('--input-bg', '#1a1a1a')
    root.setAttribute('data-theme', 'dark')
  }

  // Set common variables
  root.style.setProperty('--accent-color', '#964B00')
  root.style.setProperty('--accent-hover', '#b25900')
  root.style.setProperty('--danger-color', '#ff3b30')
  root.style.setProperty('--success-color', '#4CAF50')
  root.style.setProperty('--pending-color', '#FFA500')
  root.style.setProperty('--unassigned-color', '#808080')
  root.style.setProperty('--highlight-color', '#ff3b30')
  root.style.setProperty('--high-priority', '#ff3b30')
  root.style.setProperty('--medium-priority', '#FFA500')
  root.style.setProperty('--low-priority', '#4CAF50')
}

const toggleTheme = () => {
  const newTheme = currentTheme.value === 'dark' ? 'light' : 'dark'
  localStorage.setItem('theme', newTheme)
  currentTheme.value = newTheme
  applyTheme(newTheme)
}

const setActiveFilter = (filterId) => {
  activeFilter.value = filterId
}

const selectCase = (caseId) => {
  selectedCaseId.value = caseId
}

const handleSearch = () => {
  // The filtering is handled by the computed property 'filteredCases'
}

// Lifecycle hooks
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

<style>
/* Global styles - not scoped */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Inter', sans-serif;
}

body {
  background-color: var(--background-color);
  color: var(--text-color);
  display: flex;
  min-height: 100vh;
  transition: background-color 0.3s, color 0.3s;
  overflow: hidden;
}

.main-content {
  flex: 1;
  margin-left: var(--sidebar-width, 250px);
  height: 100vh;
  background-color: var(--content-bg);
  transition: margin-left 0.3s ease, background-color 0.3s;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.cases-container {
  flex: 1;
  padding: 20px;
  height: auto;
  overflow: visible;
}

.cases-container::-webkit-scrollbar {
  width: 8px;
}

.cases-container::-webkit-scrollbar-track {
  background: transparent;
}

.cases-container::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.cases-container::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.5);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-shrink: 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header h1 {
  font-size: 24px;
  font-weight: 600;
}

.add-new-case-btn {
  background: var(--accent-color);
  color: #fff;
  border: none;
  border-radius: 20px;
  padding: 0.6rem 1.4rem;
  font-weight: 700;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
  text-decoration: none;
  display: inline-block;
}

.add-new-case-btn:hover {
  background: var(--accent-hover);
}

.theme-toggle {
  background-color: var(--content-bg);
  color: var(--text-color);
  border: 1px solid var(--border-color);
  border-radius: 30px;
  padding: 8px 15px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.3s, color 0.3s, border-color 0.3s;
}

.theme-toggle:hover {
  background-color: var(--border-color);
}

.theme-toggle svg {
  width: 16px;
  height: 16px;
}

.search-container {
  margin-bottom: 32px;
  flex-shrink: 0;
  margin-top: 18px;
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.search-input {
  width: 100%;
  padding: 12px 20px 12px 44px;
  border-radius: 30px;
  border: none;
  background-color: var(--content-bg);
  color: var(--text-color);
  font-size: 15px;
  transition: border-color 0.3s, box-shadow 0.3s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  position: relative;
}

.search-input::placeholder {
  color: var(--text-secondary);
  font-size: 15px;
  opacity: 1;
}

.search-icon {
  position: absolute;
  left: 22px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-size: 18px;
  pointer-events: none;
  z-index: 2;
}

.filter-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 28px;
  margin-top: 18px;
  overflow-x: auto;
  padding-bottom: 5px;
  flex-shrink: 0;
}

.filter-tab {
  background-color: var(--content-bg);
  color: var(--text-color);
  border: none;
  border-radius: 30px;
  padding: 8px 15px;
  font-size: 14px;
  cursor: pointer;
  white-space: nowrap;
  transition: background-color 0.3s;
  font-weight: 500;
}

.filter-tab.active {
  background-color: var(--accent-color);
  color: white;
}

.filter-tab:hover:not(.active) {
  background-color: rgba(150, 75, 0, 0.1);
}

.cases-container-inner {
  display: flex;
  gap: 20px;
  flex: 1;
  height: auto;
  overflow: visible;
}

.cases-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  /* Make cards stretch to container width */
  width: 100%;
}

.cases-list::-webkit-scrollbar {
  width: 8px;
}

.cases-list::-webkit-scrollbar-track {
  background: transparent;
}

.cases-list::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 4px;
}

.cases-list::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.5);
}

.cases-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 15px;
}

.case-item {
  display: flex;
  align-items: flex-start;
  cursor: pointer;
  padding: 18px 32px;
  border-radius: 18px;
  transition: all 0.3s ease;
  position: relative;
  background: var(--content-bg);
  color: var(--text-color);
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  border: 1.5px solid transparent;
  font-size: 15px;
  margin-bottom: 0;
  width: 100%;
  max-width: 900px;
  min-width: 400px;
  /* Center cards in container */
  align-self: center;
}

.case-item.selected {
  background-color: rgba(255, 59, 48, 0.1);
  border: 1.5px solid var(--highlight-color);
}

.case-item:hover {
  background-color: rgba(150,75,0,0.04);
  transform: translateX(5px);
}

.case-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--accent-color);
  display: flex;
  justify-content: center;
  align-items: center;
  margin-right: 15px;
  color: #fff;
  flex-shrink: 0;
}

.case-icon svg {
  width: 18px;
  height: 18px;
  stroke: #fff;
}

.case-details {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
  justify-content: center;
  width: 100%;
  overflow: hidden;
}

.case-title {
  font-size: 1.08rem;
  font-weight: 700;
  margin-bottom: 2px;
  width: 100%;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.case-meta {
  display: flex;
  gap: 18px;
  font-size: 14px;
  color: var(--text-secondary);
  align-items: center;
  flex-wrap: wrap;
  width: 100%;
  min-height: 28px;
  padding-top: 2px;
  padding-bottom: 2px;
}

.case-priority,
.case-date,
.case-assigned {
  flex: 1 1 0;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
}

.priority-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  flex-shrink: 0;
  border: 2px solid #fff;
  box-shadow: 0 0 0 2px rgba(0,0,0,0.08);
  margin-right: 2px;
  display: inline-block;
  vertical-align: middle;
}

.priority-dot.high {
  background-color: var(--high-priority);
}
.priority-dot.medium {
  background-color: var(--medium-priority);
}
.priority-dot.low {
  background-color: var(--low-priority);
}

.case-date {
  font-size: 12px;
  color: var(--text-secondary);
}

.case-assigned {
  font-size: 12px;
  color: #888;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.case-id {
  font-size: 0.95rem;
  color: #bbb;
  margin-bottom: 8px;
}
.case-detail-drawer {
  position: fixed;
  top: 0;
  right: 0;
  height: 100vh;
  width: 400px;
  max-width: 100vw;
  background: rgba(34,34,34,0.98);
  box-shadow: -4px 0 24px rgba(0,0,0,0.18);
  border-top-left-radius: 18px;
  border-bottom-left-radius: 18px;
  z-index: 1002;
  display: flex;
  flex-direction: column;
  padding: 0 0 0 0;
  animation: slideInDrawer 0.25s cubic-bezier(0.4,0,0.2,1);
}
@keyframes slideInDrawer {
  from { right: -400px; opacity: 0; }
  to { right: 0; opacity: 1; }
}
.case-detail-drawer-header {
  padding: 32px 24px 0 24px;
  position: relative;
  min-height: 56px;
}
.case-detail-drawer .case-detail-title {
  font-size: 1.35rem;
  font-weight: 800;
  margin-bottom: 2px;
  color: #fff;
  letter-spacing: 0.01em;
}
.case-detail-drawer .case-detail-id {
  font-size: 0.95rem;
  color: #bbb;
  margin-bottom: 8px;
}
.case-detail-drawer .close-details {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 40px;
  height: 40px;
  background: rgba(0,0,0,0.06);
  border: none;
  color: #222;
  font-size: 2.1rem;
  font-weight: bold;
  border-radius: 50%;
  cursor: pointer;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, color 0.2s;
}
[data-theme="dark"] .case-detail-drawer .close-details {
  background: rgba(255,255,255,0.08);
  color: #fff;
}
.case-detail-drawer .case-detail-content {
  padding: 18px 24px 24px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  scrollbar-width: thin;
  scrollbar-color: var(--accent-color) var(--content-bg);
  overflow-y: auto;
  max-height: calc(100vh - 100px);
}
.case-detail-drawer .detail-item {
  background: rgba(255,255,255,0.07);
  border-radius: 14px;
  padding: 16px 18px;
  margin-bottom: 0;
  box-shadow: 0 2px 8px rgba(0,0,0,0.07);
  border: 1px solid rgba(255,255,255,0.08);
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.case-detail-drawer .detail-label {
  font-size: 1.01rem;
  color: #bbb;
  font-weight: 700;
  margin-bottom: 2px;
  letter-spacing: 0.01em;
}
.case-detail-drawer .detail-value {
  font-size: 1.13rem;
  color: #fff;
  font-weight: 600;
  letter-spacing: 0.01em;
}
.case-detail-drawer .detail-value.high { color: #ff3b30; font-weight: 700; }
.case-detail-drawer .detail-value.medium { color: #FFA500; font-weight: 700; }
.case-detail-drawer .detail-value.low { color: #4CAF50; font-weight: 700; }
.case-detail-drawer .detail-value.abusive { color: #ff3b30; }
/* Responsive styles */
@media (max-width: 1024px) {
  .cases-container-inner {
    flex-direction: column;
  }
  .case-detail-drawer {
    width: 100vw;
    border-radius: 0;
    left: 0;
    right: 0;
  }
}
@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
    padding: 15px;
  }
  
  .header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .header-left {
    width: 100%;
    justify-content: space-between;
  }

  .header h1 {
    font-size: 20px;
  }

  .cases-container {
    padding: 10px;
  }

  .case-meta {
    font-size: 11px;
  }

  .cases-main-content {
    padding-top: 4px;
  }
}
.cases-main-content {
  padding-top: 8px;
}
:root {
  --drawer-bg-dark: rgba(34,34,34,0.98);
  --drawer-bg-light: #fff;
  --drawer-card-bg-dark: rgba(255,255,255,0.07);
  --drawer-card-bg-light: #f5f5f5;
  --drawer-card-border-dark: 1px solid rgba(255,255,255,0.08);
  --drawer-card-border-light: 1px solid #e0e0e0;
  --drawer-title-dark: #fff;
  --drawer-title-light: #222;
  --drawer-label-dark: #bbb;
  --drawer-label-light: #555;
  --drawer-value-dark: #fff;
  --drawer-value-light: #222;
  --drawer-value-high: #ff3b30;
  --drawer-value-medium: #FFA500;
  --drawer-value-low: #4CAF50;
  --priority-dot-border-dark: #fff;
  --priority-dot-border-light: #fff;
  --priority-dot-shadow: 0 0 0 2px rgba(0,0,0,0.08);
}
[data-theme="light"] .case-detail-drawer {
  background: var(--drawer-bg-light);
}
[data-theme="dark"] .case-detail-drawer {
  background: var(--drawer-bg-dark);
}
[data-theme="light"] .case-detail-drawer .detail-item {
  background: var(--drawer-card-bg-light);
  border: var(--drawer-card-border-light);
}
[data-theme="dark"] .case-detail-drawer .detail-item {
  background: var(--drawer-card-bg-dark);
  border: var(--drawer-card-border-dark);
}
[data-theme="light"] .case-detail-drawer .case-detail-title {
  color: var(--drawer-title-light);
}
[data-theme="dark"] .case-detail-drawer .case-detail-title {
  color: var(--drawer-title-dark);
}
[data-theme="light"] .case-detail-drawer .detail-label {
  color: var(--drawer-label-light);
}
[data-theme="dark"] .case-detail-drawer .detail-label {
  color: var(--drawer-label-dark);
}
[data-theme="light"] .case-detail-drawer .detail-value {
  color: var(--drawer-value-light);
}
[data-theme="dark"] .case-detail-drawer .detail-value {
  color: var(--drawer-value-dark);
}
[data-theme="light"] .case-detail-drawer .detail-value.high {
  color: var(--drawer-value-high);
}
[data-theme="light"] .case-detail-drawer .detail-value.medium {
  color: var(--drawer-value-medium);
}
[data-theme="light"] .case-detail-drawer .detail-value.low {
  color: var(--drawer-value-low);
}
[data-theme="dark"] .case-detail-drawer .detail-value.high {
  color: var(--drawer-value-high);
}
[data-theme="dark"] .case-detail-drawer .detail-value.medium {
  color: var(--drawer-value-medium);
}
[data-theme="dark"] .case-detail-drawer .detail-value.low {
  color: var(--drawer-value-low);
}
[data-theme="light"] .priority-dot {
  border: 1.5px solid var(--priority-dot-border-light);
  box-shadow: var(--priority-dot-shadow);
}
[data-theme="dark"] .priority-dot {
  border: 1.5px solid var(--priority-dot-border-dark);
  box-shadow: var(--priority-dot-shadow);
}
[data-theme="light"] .case-item.selected {
  border: 2px solid var(--accent-color);
  background: #fff8f0;
}
[data-theme="dark"] .case-item.selected {
  border: 2px solid var(--accent-color);
  background: rgba(150,75,0,0.08);
}
body.high-contrast .case-detail-drawer,
body.high-contrast .case-detail-drawer .detail-item,
body.high-contrast .case-detail-drawer .case-detail-title,
body.high-contrast .case-detail-drawer .detail-label,
body.high-contrast .case-detail-drawer .detail-value,
body.high-contrast .case-item.selected,
body.high-contrast .priority-dot {
  background: #000 !important;
  color: #fff !important;
  border-color: #fff !important;
}
body.high-contrast .priority-dot.high { background: #ff3b30 !important; }
body.high-contrast .priority-dot.medium { background: #FFA500 !important; }
body.high-contrast .priority-dot.low { background: #4CAF50 !important; }
@media (max-width: 900px) {
  .case-item {
    padding: 14px 10px;
    max-width: 100vw;
    min-width: 0;
  }
  .case-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
    white-space: normal;
  }
  .case-priority,
  .case-date,
  .case-assigned {
    max-width: 100%;
    width: 100%;
    display: block;
  }
}
@media (max-width: 600px) {
  .case-item {
    padding: 12px 6px 14px 6px;
    gap: 8px;
    border-radius: 12px;
  }
  .case-icon {
    width: 28px;
    height: 28px;
    min-width: 28px;
    min-height: 28px;
    max-width: 28px;
    max-height: 28px;
    margin-right: 6px;
  }
  .case-title {
    font-size: 0.95rem;
  }
  .case-meta {
    font-size: 11px;
  }
  .case-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
    white-space: normal;
  }
  .case-priority,
  .case-date,
  .case-assigned {
    max-width: 100%;
    width: 100%;
    display: block;
  }
}
</style>
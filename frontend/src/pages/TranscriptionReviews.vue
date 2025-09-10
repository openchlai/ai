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
        <h1>Transcription Reviews</h1>
            <p>Review and correct audio transcriptions marked as incorrect</p>
          </div>
        </div>

        <!-- Main content area -->
        <div class="content-grid">
          <!-- Current review section -->
          <div v-if="selectedItem" class="review-section">
            <div class="review-header">
              <h2>Reviewing Audio #{{ selectedItem.id }}</h2>
              <div class="item-meta">
                <span class="meta-item">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="currentColor" stroke-width="2"/>
                    <path d="M2 17L12 22L22 17" stroke="currentColor" stroke-width="2"/>
                    <path d="M2 12L12 17L22 12" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  {{ selectedItem.counsellor }}
                </span>
                <span class="meta-item">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/>
                    <polyline points="12,6 12,12 16,14" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  {{ formatDate(selectedItem.uploadedAt) }}
                </span>
              </div>
              <div class="header-actions">
                <button class="btn btn--secondary" @click="skipToNext">Skip to Next</button>
              </div>
            </div>

            <!-- Audio player -->
            <div class="audio-player-section">
              <h3>Audio Recording</h3>
              <div class="audio-player">
                <div class="audio-controls">
                  <button class="play-btn" @click="togglePlayback" :class="{ playing: isPlaying }">
                    <svg v-if="!isPlaying" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <polygon points="5,3 19,12 5,21" fill="currentColor"/>
                    </svg>
                    <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <rect x="6" y="4" width="4" height="16" fill="currentColor"/>
                      <rect x="14" y="4" width="4" height="16" fill="currentColor"/>
                    </svg>
                  </button>
                  <div class="audio-progress">
                    <div class="progress-bar">
                      <div class="progress-fill" :style="{ width: progressPercent + '%' }"></div>
                    </div>
                    <div class="time-display">
                      <span>{{ formatTime(currentTime) }}</span>
                      <span>{{ formatTime(duration) }}</span>
                    </div>
                  </div>
                  <button class="volume-btn" @click="toggleMute">
                    <svg v-if="!isMuted" width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <polygon points="11,5 6,9 2,9 2,15 6,15 11,19 11,5" stroke="currentColor" stroke-width="2"/>
                      <path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" stroke="currentColor" stroke-width="2"/>
                    </svg>
                    <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <polygon points="11,5 6,9 2,9 2,15 6,15 11,19 11,5" stroke="currentColor" stroke-width="2"/>
                      <line x1="23" y1="9" x2="17" y2="15" stroke="currentColor" stroke-width="2"/>
                      <line x1="17" y1="9" x2="23" y2="15" stroke="currentColor" stroke-width="2"/>
                    </svg>
                  </button>
                </div>
                <div v-if="!selectedItem.audioUrl" class="no-audio">
                  <svg width="32" height="32" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" stroke="currentColor" stroke-width="2"/>
                    <path d="M19 10v2a7 7 0 0 1-14 0v-2" stroke="currentColor" stroke-width="2"/>
                  </svg>
                  <span>No audio file available</span>
                </div>
              </div>
        </div>

            <!-- Transcription editor -->
            <div class="transcription-section">
              <h3>Transcription</h3>
              <div class="transcription-editor">
          <textarea
                  v-model="editingTranscription"
                  placeholder="Edit the transcription here..."
                  rows="8"
                  class="transcription-textarea"
          ></textarea>
                <div class="editor-actions">
                  <button class="btn btn--secondary" @click="resetTranscription">
                    Reset to Original
                  </button>
                  <button class="btn btn--primary" @click="submitReview">
                    Submit Review
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Queue section -->
          <div class="queue-section">
            <div class="queue-header">
              <h3>Review Queue</h3>
              <div class="filters">
                <div class="filter-group">
                  <label>Audio ID:</label>
                  <input 
                    v-model="filters.audioId" 
                    type="text" 
                    placeholder="Filter by ID..."
                    :class="['filter-input', { active: focusedFilter === 'audioId' || !!filters.audioId }]"
                    @focus="focusedFilter = 'audioId'"
                    @blur="focusedFilter = null"
                  />
                </div>
                <div class="filter-group">
                  <label>Counsellor:</label>
                  <input 
                    v-model="filters.counsellor" 
                    type="text" 
                    placeholder="Filter by name..."
                    :class="['filter-input', { active: focusedFilter === 'counsellor' || !!filters.counsellor }]"
                    @focus="focusedFilter = 'counsellor'"
                    @blur="focusedFilter = null"
                  />
                </div>
                <div class="filter-group">
                  <label>Sort by ID:</label>
                  <div class="sort-controls">
                    <button class="btn btn--secondary" :class="{ active: sortOrder === 'asc' }" @click="setSort('asc')">Smallest → Largest</button>
                    <button class="btn btn--secondary" :class="{ active: sortOrder === 'desc' }" @click="setSort('desc')">Largest → Smallest</button>
                  </div>
                </div>
                <button class="btn btn--secondary" @click="clearFilters">Clear Filters</button>
              </div>
            </div>

            <div class="queue-list">
              <div 
                v-for="item in pagedQueue" 
                :key="item.id" 
                class="queue-item"
                :class="{ active: selectedItem?.id === item.id }"
                @click="selectItem(item)"
              >
                <div class="item-info">
                  <div class="item-id">#{{ item.id }}</div>
                  <div class="item-details">
                    <div class="item-counsellor">{{ item.counsellor }}</div>
                    <div class="item-date">{{ formatDate(item.uploadedAt) }}</div>
                  </div>
                </div>
                <div class="item-status">
                  <span class="status-badge pending">Pending Review</span>
                </div>
                <button class="review-btn" @click.stop="selectItem(item)">
                  Review
                </button>
              </div>
            </div>

            <div class="pagination" v-if="sortedFilteredQueue.length > pageSize">
              <button class="btn btn--secondary" @click="prevPage" :disabled="currentPage === 1">Prev</button>
              <span class="page-indicator">Page {{ currentPage }} / {{ totalPages }}</span>
              <button class="btn btn--secondary" @click="nextPage" :disabled="currentPage === totalPages">Next</button>
            </div>

            <div v-if="filteredQueue.length === 0" class="empty-queue">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" stroke="currentColor" stroke-width="2"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2" stroke="currentColor" stroke-width="2"/>
              </svg>
              <h4>No items to review</h4>
              <p>All transcriptions have been reviewed or no items match your filters.</p>
            </div>
        </div>
        </div>
      </div>
    </div>
  </div>
 </template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useTranscriptionsStore } from '@/stores/transcriptionsStore'
import SidePanel from '@/components/SidePanel.vue'

const transStore = useTranscriptionsStore()

// SidePanel props and state
const userRole = ref('admin')
const isInQueue = ref(false)
const isProcessingQueue = ref(false)
const currentCall = ref(null)

// SidePanel event handlers
const handleQueueToggle = () => {
  isInQueue.value = !isInQueue.value
}

const handleLogout = () => {
  // Handle logout logic
  console.log('Logout clicked')
}

const handleSidebarToggle = () => {
  // Handle sidebar toggle logic
  console.log('Sidebar toggle clicked')
}

// State
const selectedItem = ref(null)
const editingTranscription = ref('')
const isPlaying = ref(false)
const isMuted = ref(false)
const currentTime = ref(0)
const duration = ref(0)
const audioElement = ref(null)

// Filters
const filters = ref({
  audioId: '',
  counsellor: ''
})
const focusedFilter = ref(null)

// Sorting
const sortOrder = ref('asc') // 'asc' | 'desc'

// Pagination
const pageSize = 8
const currentPage = ref(1)

// Computed
const queue = computed(() => transStore.pending)

const filteredQueue = computed(() => {
  return queue.value.filter(item => {
    const matchesId = !filters.value.audioId || 
      item.id.toString().includes(filters.value.audioId)
    const matchesCounsellor = !filters.value.counsellor || 
      item.counsellor.toLowerCase().includes(filters.value.counsellor.toLowerCase())
    return matchesId && matchesCounsellor
  })
})

const sortedFilteredQueue = computed(() => {
  const arr = [...filteredQueue.value]
  arr.sort((a, b) => sortOrder.value === 'asc' ? a.id - b.id : b.id - a.id)
  return arr
})

const totalPages = computed(() => Math.max(1, Math.ceil(sortedFilteredQueue.value.length / pageSize)))

const pagedQueue = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return sortedFilteredQueue.value.slice(start, start + pageSize)
})

const progressPercent = computed(() => {
  return duration.value > 0 ? (currentTime.value / duration.value) * 100 : 0
})

// Methods
const selectItem = (item) => {
  selectedItem.value = item
  editingTranscription.value = item.transcription
  resetAudio()
}

const skipToNext = () => {
  if (!selectedItem.value) return
  // Remove from queue visually by marking reviewed then immediately selecting next visible
  transStore.markReviewed(selectedItem.value.id)
  const currentIndex = sortedFilteredQueue.value.findIndex(i => i.id === selectedItem.value.id)
  // If we removed one, adjust page if needed
  if ((currentIndex + 1) >= sortedFilteredQueue.value.length && currentPage.value > 1 && pagedQueue.value.length === 1) {
    currentPage.value = Math.max(1, currentPage.value - 1)
  }
  // Pick next item from current page slice
  const next = sortedFilteredQueue.value[currentIndex + 1] || sortedFilteredQueue.value[currentIndex - 1]
  if (next) {
    selectItem(next)
  } else {
    selectedItem.value = null
    editingTranscription.value = ''
  }
}

const resetTranscription = () => {
  if (selectedItem.value) {
    editingTranscription.value = selectedItem.value.transcription
  }
}

const submitReview = () => {
  if (selectedItem.value) {
    transStore.updateTranscription(selectedItem.value.id, editingTranscription.value)
    transStore.markReviewed(selectedItem.value.id)
    
    // Remove from queue and select next item
    const currentIndex = filteredQueue.value.findIndex(item => item.id === selectedItem.value.id)
    const nextItem = filteredQueue.value[currentIndex + 1] || filteredQueue.value[currentIndex - 1]
    
    if (nextItem) {
      selectItem(nextItem)
    } else {
      selectedItem.value = null
      editingTranscription.value = ''
    }
  }
}

const clearFilters = () => {
  filters.value.audioId = ''
  filters.value.counsellor = ''
  currentPage.value = 1
}

const setSort = (order) => {
  sortOrder.value = order
  currentPage.value = 1
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value += 1
}

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value -= 1
}

// Audio controls
const togglePlayback = () => {
  if (!selectedItem.value?.audioUrl) return
  
  if (!audioElement.value) {
    audioElement.value = new Audio(selectedItem.value.audioUrl)
    audioElement.value.addEventListener('timeupdate', updateTime)
    audioElement.value.addEventListener('loadedmetadata', () => {
      duration.value = audioElement.value.duration
    })
    audioElement.value.addEventListener('ended', () => {
      isPlaying.value = false
      currentTime.value = 0
    })
  }
  
  if (isPlaying.value) {
    audioElement.value.pause()
    isPlaying.value = false
  } else {
    audioElement.value.play()
    isPlaying.value = true
  }
}

const toggleMute = () => {
  if (audioElement.value) {
    audioElement.value.muted = !isMuted.value
    isMuted.value = !isMuted.value
  }
}

const updateTime = () => {
  if (audioElement.value) {
    currentTime.value = audioElement.value.currentTime
  }
}

const resetAudio = () => {
  if (audioElement.value) {
    audioElement.value.pause()
    audioElement.value.currentTime = 0
  }
  isPlaying.value = false
  currentTime.value = 0
  duration.value = 0
}

const formatTime = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const formatDate = (ts) => {
  return new Date(ts).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Lifecycle
onMounted(() => {
  // Select first item if available
  if (sortedFilteredQueue.value.length > 0) {
    selectItem(sortedFilteredQueue.value[0])
  }
})

onUnmounted(() => {
  if (audioElement.value) {
    audioElement.value.pause()
    audioElement.value = null
  }
})
</script>

<style scoped>
/* Main content layout with SidePanel */
.main-content {
  margin-left: 280px;
  min-height: 100vh;
  background: var(--color-surface);
  transition: margin-left 0.3s ease;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }
}

.page-container {
  padding: 20px;
  min-height: 100vh;
}

/* Header */
.header {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 24px;
}

.header-content h1 {
  margin: 0;
  font-size: 26px;
  font-weight: 900;
  color: var(--text-color);
}

.header-content p {
  margin: 6px 0 0;
  color: var(--color-muted);
  font-size: 14px;
}

/* Content grid layout */
.content-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
}

@media (min-width: 1200px) {
  .content-grid {
    grid-template-columns: 1fr 420px;
  }
}

@media (min-width: 1400px) {
  .content-grid {
    grid-template-columns: 1fr 400px;
  }
}

/* Review section */
.review-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 28px;
  box-shadow: var(--shadow-sm);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-border);
}

.review-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  color: var(--text-color);
}

.item-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--color-muted);
  font-size: 13px;
  font-weight: 500;
}

/* Audio player */
.audio-player-section {
  margin-bottom: 20px;
}

.audio-player-section h3 {
  margin: 0 0 12px;
  font-size: 15px;
  font-weight: 700;
  color: var(--text-color);
}

.audio-player {
  background: var(--color-surface-muted);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 16px;
}

.audio-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.play-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--color-primary);
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.play-btn:hover {
  background: color-mix(in oklab, var(--color-primary) 80%, black);
  transform: scale(1.05);
}

.play-btn.playing {
  background: var(--success-color);
}

.audio-progress {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: var(--color-border);
  border-radius: 3px;
  overflow: hidden;
  cursor: pointer;
}

.progress-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: 3px;
  transition: width 0.1s ease;
}

.time-display {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--color-muted);
  font-weight: 500;
}

.volume-btn {
  background: none;
  border: none;
  color: var(--color-muted);
  cursor: pointer;
  padding: 8px;
  border-radius: 6px;
  transition: all 0.2s ease;
}

.volume-btn:hover {
  background: var(--color-surface-muted);
  color: var(--text-color);
}

.no-audio {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  color: var(--color-muted);
  padding: 24px 16px;
}

.no-audio svg {
  opacity: 0.5;
}

/* Transcription section */
.transcription-section h3 {
  margin: 0 0 12px;
  font-size: 15px;
  font-weight: 700;
  color: var(--text-color);
}

.transcription-editor {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.transcription-textarea {
  width: 100%;
  min-height: 240px;
  padding: 20px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  background: var(--color-surface);
  color: var(--text-color);
  font-family: inherit;
  font-size: 15px;
  line-height: 1.7;
  resize: vertical;
  transition: border-color 0.2s ease;
}

.transcription-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px color-mix(in oklab, var(--color-primary) 10%, transparent);
}

.editor-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* Queue section */
.queue-section {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--shadow-sm);
  min-width: 0;
}

.queue-header {
  margin-bottom: 16px;
}

.queue-header h3 {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 800;
  color: var(--text-color);
}

.filters {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-group label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-color);
}

.filter-input {
  padding: 6px 10px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  background: var(--color-surface);
  color: var(--text-color);
  font-size: 13px;
  transition: border-color 0.2s ease;
}

.filter-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.filter-input.active {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px color-mix(in oklab, var(--color-primary) 10%, transparent);
}

/* Queue list */
.queue-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 350px;
  overflow-y: auto;
}

.queue-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.queue-item:hover {
  background: var(--color-surface-muted);
  border-color: var(--color-primary);
}

.queue-item.active {
  background: color-mix(in oklab, var(--color-primary) 8%, transparent);
  border-color: var(--color-primary);
}

.item-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.item-id {
  font-weight: 800;
  color: var(--color-primary);
  font-size: 14px;
  min-width: 40px;
}

.item-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.item-counsellor {
  font-weight: 600;
  color: var(--text-color);
  font-size: 14px;
}

.item-date {
  color: var(--color-muted);
  font-size: 12px;
}

.item-status {
  flex-shrink: 0;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.pending {
  background: color-mix(in oklab, var(--warning-color, #f59e0b) 10%, transparent);
  color: var(--warning-color, #f59e0b);
}

.review-btn {
  background: var(--color-primary);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.review-btn:hover {
  background: color-mix(in oklab, var(--color-primary) 80%, black);
  transform: translateY(-1px);
}

/* Sort / Pagination */
.sort-controls {
  display: flex;
  gap: 8px;
}

.btn.btn--secondary.active {
  border-color: var(--color-primary);
  background: var(--color-surface);
  box-shadow: 0 0 0 3px color-mix(in oklab, var(--color-primary) 8%, transparent);
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 10px;
}

.page-indicator {
  font-size: 12px;
  color: var(--color-muted);
}

/* Empty state */
.empty-queue {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 40px 20px;
  text-align: center;
  color: var(--color-muted);
}

.empty-queue h4 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color);
}

.empty-queue p {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}

/* Buttons */
.btn {
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn--primary {
  background: var(--color-primary);
  color: white;
}

.btn--primary:hover {
  background: color-mix(in oklab, var(--color-primary) 80%, black);
  transform: translateY(-1px);
}

.btn--secondary {
  background: var(--color-surface-muted);
  color: var(--text-color);
  border: 1px solid var(--color-border);
}

.btn--secondary:hover {
  background: var(--color-surface);
  border-color: var(--color-primary);
  transform: translateY(-1px);
}
</style>



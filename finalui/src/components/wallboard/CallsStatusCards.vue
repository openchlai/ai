 <template>
  <div class="counsellors-section">
    <div class="section-header">
      <h2 class="section-title">Callers Online: {{ onlineCount }}</h2>
    </div>
    <div class="counsellors-table">
      <div class="table-header callers-header">
        <div class="col-caller-num">Caller Number</div>
        <div class="col-vector">Queue</div>
        <div class="col-wait-time">Wait Time</div>
        <div class="col-status">Status</div>
      </div>
      <div class="table-body" ref="tableContainer">
        <div v-if="callers.length === 0" class="no-counsellors-row">
          <div class="no-counsellors-text">No callers currently online</div>
        </div>
        <div 
          v-for="caller in callers" 
          :key="caller.id"
          class="table-row callers-row"
        >
          <div class="col-caller-num">{{ caller.callerNumber || '--' }}</div>
          <div class="col-vector">{{ caller.vector || '--' }}</div>
          <div class="col-wait-time">{{ caller.waitTime || '--' }}</div>
          <div :class="['col-status', getStatusClass(caller.queueStatus)]">
            {{ caller.queueStatus || 'Unknown' }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'

export default {
  name: 'CallersTable',
  props: {
    callers: {
      type: Array,
      required: true,
      default: () => []
    },
    onlineCount: {
      type: Number,
      required: true,
      default: 0
    }
  },
  setup(props) {
    const tableContainer = ref(null)
    let scrollInterval = null

    // Auto-scroll functionality
    const setupAutoScroll = (container, scrollSpeed = 0.8, pauseDuration = 2500) => {
      if (!container) return null
      
      let direction = 1 // 1 for down, -1 for up
      let isPaused = false
      
      return setInterval(() => {
        if (isPaused || !container) return
        
        const { scrollTop, scrollHeight, clientHeight } = container
        const maxScroll = scrollHeight - clientHeight
        
        if (maxScroll <= 0) return // No need to scroll if content fits
        
        // Check if we've reached the bottom or top
        if (scrollTop >= maxScroll - 3) {
          direction = -1
          isPaused = true
          setTimeout(() => { isPaused = false }, pauseDuration)
        } else if (scrollTop <= 3) {
          direction = 1
          isPaused = true
          setTimeout(() => { isPaused = false }, pauseDuration)
        }
        
        container.scrollBy(0, direction * scrollSpeed)
      }, 40)
    }

    // Start auto-scroll
    const startAutoScroll = () => {
      nextTick(() => {
        if (tableContainer.value) {
          scrollInterval = setupAutoScroll(tableContainer.value)
        }
      })
    }

    // Stop auto-scroll
    const stopAutoScroll = () => {
      if (scrollInterval) {
        clearInterval(scrollInterval)
        scrollInterval = null
      }
    }

    // Watch for data changes to restart auto-scroll
    watch(() => props.callers, () => {
      stopAutoScroll()
      setTimeout(startAutoScroll, 800)
    })

    // Lifecycle
    onMounted(() => {
      setTimeout(startAutoScroll, 1500)
    })

    onBeforeUnmount(() => {
      stopAutoScroll()
    })

    return {
      tableContainer
    }
  },
  methods: {
    getStatusClass(status) {
      const s = (status || 'Available').toString().toLowerCase()
      if (s.includes('on call')) return 'status-oncall'
      if (s.includes('ring')) return 'status-ringing'
      if (s.includes('queue')) return 'status-inqueue'
      if (s.includes('available')) return 'status-available'
      if (s.includes('offline')) return 'status-offline'
      return 'status-neutral'
    }
  }
}
</script>

<style scoped>
/* TV-Optimized Component styling */
.counsellors-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.section-header {
  flex-shrink: 0;
  margin-bottom: 8px;
}

.section-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.dark-mode .section-title {
  color: #f9fafb;
}

.counsellors-table {
  background: #ffffff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.dark-mode .counsellors-table {
  background: #2d3748;
}

.callers-header,
.callers-row {
  display: grid !important;
  grid-template-columns: 140px 100px 100px 1fr !important;
  gap: 8px !important;
}

.table-header {
  padding: 8px 10px;
  background: #f8fafc;
  font-weight: 600;
  font-size: 0.8rem;
  color: #374151;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  flex-shrink: 0;
}

.dark-mode .table-header {
  background: #374151;
  color: #d1d5db;
}

/* Table body with auto-scroll - TV optimized height */
.table-body {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  scroll-behavior: smooth;
  pointer-events: none;
  max-height: 160px; /* Height for exactly 4 rows at 40px per row */
  min-height: 160px;
}

/* Ultra-slim scrollbar for TV */
.table-body::-webkit-scrollbar {
  width: 1px;
}

.table-body::-webkit-scrollbar-track {
  background: transparent;
}

.table-body::-webkit-scrollbar-thumb {
  background: rgba(203, 213, 225, 0.2);
  border-radius: 1px;
}

.dark-mode .table-body::-webkit-scrollbar-thumb {
  background: rgba(107, 114, 128, 0.2);
}

.table-row {
  padding: 8px 10px;
  border-bottom: 1px solid #f3f4f6;
  font-size: 0.85rem;
  height: 40px;
  align-items: center;
  font-weight: 500;
}

.dark-mode .table-row {
  border-bottom-color: #4b5563;
  color: #e2e8f0;
}

.table-row:last-child {
  border-bottom: none;
}

.callers-header > div,
.callers-row > div {
  display: flex;
  align-items: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.no-counsellors-row {
  padding: 20px 8px;
  text-align: center;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-counsellors-text {
  color: #6b7280;
  font-style: italic;
  font-size: 0.75rem;
}

.dark-mode .no-counsellors-text {
  color: #9ca3af;
}

/* Status color classes */
.status-oncall {
  color: #10b981;
  font-weight: 600;
}

.status-ringing {
  color: #f59e0b;
  font-weight: 600;
  animation: blink 1.5s ease-in-out infinite;
}

.status-inqueue {
  color: #3b82f6;
  font-weight: 600;
}

.status-available {
  color: #6b7280;
  font-weight: 500;
}

.status-offline {
  color: #ef4444;
  font-weight: 600;
}

.status-neutral {
  color: #6b7280;
}

@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* TV Screen optimizations */
@media screen and (min-width: 1920px) {
  .section-title {
    font-size: 1rem;
  }
  
  .callers-header,
  .callers-row {
    grid-template-columns: 160px 120px 120px 1fr !important;
    gap: 10px !important;
  }
  
  .table-header {
    padding: 8px 10px;
    font-size: 0.75rem;
  }
  
  .table-body {
    max-height: 160px;
    min-height: 160px;
  }
  
  .table-row {
    padding: 8px 10px;
    font-size: 0.8rem;
    height: 40px;
  }
}

/* 4K TV optimization */
@media screen and (min-width: 3840px) {
  .section-title {
    font-size: 1.25rem;
  }
  
  .callers-header,
  .callers-row {
    grid-template-columns: 200px 150px 150px 1fr !important;
    gap: 15px !important;
  }
  
  .table-header {
    padding: 12px 15px;
    font-size: 0.9rem;
  }
  
  .table-body {
    max-height: 240px;
    min-height: 240px;
  }
  
  .table-row {
    padding: 12px 15px;
    font-size: 1rem;
    height: 60px;
  }
  
  .no-counsellors-row {
    height: 240px;
    padding: 30px 15px;
  }
  
  .no-counsellors-text {
    font-size: 1rem;
  }
}

/* Smaller TV screens */
@media screen and (max-width: 1600px) {
  .section-title {
    font-size: 0.8rem;
  }
  
  .callers-header,
  .callers-row {
    grid-template-columns: 120px 80px 80px 1fr !important;
    gap: 6px !important;
  }
  
  .table-header {
    padding: 5px 6px;
    font-size: 0.6rem;
  }
  
  .table-body {
    max-height: 120px;
    min-height: 120px;
  }
  
  .table-row {
    padding: 5px 6px;
    font-size: 0.65rem;
    height: 30px;
  }
  
  .no-counsellors-row {
    height: 120px;
    padding: 15px 6px;
  }
  
  .no-counsellors-text {
    font-size: 0.7rem;
  }
}

/* Very small screens */
@media screen and (max-width: 1200px) {
  .callers-header,
  .callers-row {
    grid-template-columns: 100px 70px 70px 1fr !important;
    gap: 5px !important;
  }
  
  .table-header,
  .table-row {
    font-size: 0.6rem;
  }
  
  .table-row {
    height: 28px;
  }
  
  .table-body {
    max-height: 112px;
    min-height: 112px;
  }
}

/* Mobile fallback */
@media screen and (max-width: 768px) {
  .counsellors-table {
    overflow-x: auto;
  }
  
  .callers-header,
  .callers-row {
    display: flex !important;
    min-width: 500px;
    gap: 10px !important;
  }
  
  .callers-header > div,
  .callers-row > div {
    flex: 1;
    min-width: 100px;
  }
  
  .col-caller-num {
    min-width: 130px;
  }
}
</style>
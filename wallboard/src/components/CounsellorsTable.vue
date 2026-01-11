<template>
  <div class="counsellors-section">
    <div class="minimal-section-header">
      <h2 class="title-slate">Counsellors Online</h2>
      <div class="count-circle-slate">{{ onlineCount }}</div>
    </div>
    <div class="counsellors-table">
      <div class="table-header">
        <div class="col-ext">EXT</div>
        <div class="col-name">NAME</div>
        <div class="col-icon"></div>
        <div class="col-caller">ACTIVE CALLER</div>
        <div class="col-stats">ANS</div>
        <div class="col-stats">MISSED</div>
        <div class="col-stats">TALK</div>
        <div class="col-status">STATUS</div>
        <div class="col-duration">TIME</div>
      </div>
      <div class="table-body" ref="tableContainer">
        <div v-if="counsellors.length === 0" class="no-counsellors-row">
          <div class="no-counsellors-text">No counsellors currently online</div>
        </div>
        <div 
          v-for="counsellor in counsellors" 
          :key="counsellor.id"
          :class="['table-row', getStatusClass(counsellor.queueStatus)]"
        >
          <div class="col-ext">{{ counsellor.extension }}</div>
          <div class="col-name agent-name-text">{{ counsellor.name }}</div>
          <div class="col-icon">
            <svg v-if="counsellor.caller !== '--'" class="caller-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <path d="M19 12H5M5 12L12 19M5 12L12 5"/>
            </svg>
          </div>
          <div class="col-caller highlight">{{ counsellor.caller }}</div>
          <div class="col-stats ans-val">{{ formatNumberWithCommas(counsellor.answered) }}</div>
          <div class="col-stats missed-val">{{ formatNumberWithCommas(counsellor.missed) }}</div>
          <div class="col-stats">{{ counsellor.talkTime }}</div>
          <div class="col-status">
            <span :class="['status-text', getStatusClass(counsellor.queueStatus)]">
              {{ counsellor.queueStatus }}
            </span>
          </div>
          <div :class="['col-duration', getStatusClass(counsellor.queueStatus)]">{{ counsellor.duration }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import { formatNumberWithCommas } from '../utils/formatters'

export default {
  name: 'CounsellorsTable',
  props: {
    counsellors: {
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

    const getInitials = (name) => {
      if (!name) return '?'
      return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase()
    }

    const getAvatarColor = (name) => {
      const colors = ['#f47c20', '#1d3e8a', '#0e7337', '#b95e06', '#c0392b', '#8b5cf6']
      let hash = 0
      for (let i = 0; i < name.length; i++) {
        hash = name.charCodeAt(i) + ((hash << 5) - hash)
      }
      return colors[Math.abs(hash) % colors.length]
    }

    // Auto-scroll functionality
    const setupAutoScroll = (container, scrollSpeed = 0.8, pauseDuration = 2500) => {
      if (!container) return null
      
      let direction = 1
      let isPaused = false
      
      return setInterval(() => {
        if (isPaused || !container) return
        
        const { scrollTop, scrollHeight, clientHeight } = container
        const maxScroll = scrollHeight - clientHeight
        
        if (maxScroll <= 0) return
        
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

    const startAutoScroll = () => {
      nextTick(() => {
        if (tableContainer.value) {
          scrollInterval = setupAutoScroll(tableContainer.value)
        }
      })
    }

    const stopAutoScroll = () => {
      if (scrollInterval) {
        clearInterval(scrollInterval)
        scrollInterval = null
      }
    }

    watch(() => props.counsellors, () => {
      stopAutoScroll()
      setTimeout(startAutoScroll, 800)
    })

    onMounted(() => {
      setTimeout(startAutoScroll, 1500)
    })

    onBeforeUnmount(() => {
      stopAutoScroll()
    })

    return {
      tableContainer,
      getInitials,
      getAvatarColor,
      formatNumberWithCommas
    }
  },
  methods: {
    getStatusClass(status) {
      const s = (status || 'Available').toString().toLowerCase()
      if (s.includes('wrapup')) return 'status-wrapup'
      if (s.includes('waiting')) return 'status-waiting'
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
.counsellors-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.minimal-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 5px 10px 5px;
  border-bottom: 2px solid #eee;
  margin-bottom: 5px;
}

.title-slate {
  color: #1e293b;
  font-size: 1.5rem;
  font-weight: 800;
  margin: 0;
}

.count-circle-slate {
  background: #1e293b;
  color: white;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 1.1rem;
}

.counsellors-table {
  background: white;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
}

.table-header {
  display: grid;
  grid-template-columns: 50px 140px 30px 1.2fr 60px 60px 70px 100px 70px;
  gap: 8px;
  padding: 12px 15px;
  background: #0f172a; /* Premium dark navy */
  font-weight: 800;
  font-size: 0.7rem;
  color: #94a3b8;
  text-transform: uppercase;
  flex-shrink: 0;
}

.table-body {
  flex: 1;
  overflow-y: auto;
  scroll-behavior: smooth;
  background: white;
}

.table-row {
  display: grid;
  grid-template-columns: 50px 140px 30px 1.2fr 60px 60px 70px 100px 70px;
  gap: 8px;
  padding: 12px 15px;
  border-bottom: 1px solid #e2e8f0;
  align-items: center;
  transition: all 0.2s ease;
  font-size: 0.95rem;
  font-weight: 600;
}

.col-ext { font-weight: 700; color: #64748b; }
.agent-name-text { font-weight: 800; color: #1e293b; text-transform: uppercase; }

.caller-arrow {
  width: 14px;
  height: 14px;
  color: #10b981;
}

.highlight {
  color: #10b981;
  font-weight: 700;
}

.ans-val { color: #64748b; }
.missed-val { color: #ef4444; }

.status-text {
  font-weight: 800;
  font-size: 0.75rem;
}

.status-oncall { color: #10b981; }
.status-ringing { color: #f59e0b; }
.status-wrapup { color: #f59e0b; }
.status-waiting { color: #3b82f6; }
.status-available { color: #3b82f6; }

.col-duration {
  font-weight: 900;
  text-align: right;
  color: #1e293b;
}

.col-duration.status-wrapup,
.col-duration.status-ringing {
  color: #f59e0b;
}

.col-duration.status-oncall {
  color: #10b981;
}

@keyframes blink {
  50% { opacity: 0.5; }
}

@keyframes pulse {
  50% { opacity: 0.6; }
}

.no-counsellors-row {
  padding: 40px;
  text-align: center;
}

.no-counsellors-text {
  color: var(--text-secondary);
  font-style: italic;
  font-size: 0.9rem;
}

/* TV Optimization */
@media screen and (min-width: 1920px) {
  .table-header, .table-row {
    grid-template-columns: 1fr 150px 80px 80px 80px 120px;
    padding: 16px 24px;
  }
}
</style>
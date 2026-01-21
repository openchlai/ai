<template>
  <div class="table-wrapper">
    <table class="agent-table">
      <thead>
        <tr>
          <th class="th-ext">EXT</th>
          <th class="th-agent">AGENT NAME</th>
          <th class="th-stat">ANS</th>
          <th class="th-stat">MISS</th>
          <th class="th-stat">TALK</th>
          <th class="th-status">STATUS</th>
          <th class="th-time">TIME</th>
        </tr>
      </thead>
      <tbody class="scrollable-tbody" ref="tableContainer">
        <tr v-if="counsellors.length === 0">
          <td colspan="7" class="no-agents">No agents currently online</td>
        </tr>
        <tr 
          v-for="counsellor in counsellors" 
          :key="counsellor.id"
          class="agent-row"
        >
          <td class="td-ext">#{{ counsellor.extension }}</td>
          <td class="td-agent">
            <div class="agent-info">
              <div class="agent-avatar" :style="{ backgroundColor: getAvatarColor(counsellor.name) }">
                {{ getInitials(counsellor.name) }}
              </div>
              <div class="agent-meta">
                <span class="agent-name">{{ counsellor.name }}</span>
              </div>
            </div>
          </td>
          <td class="td-stat">{{ counsellor.answered || 0 }}</td>
          <td class="td-stat">{{ counsellor.missed || 0 }}</td>
          <td class="td-stat">{{ counsellor.talkTime || '0:00' }}</td>
          <td class="td-status">
            <span :class="['status-pill', getStatusClass(counsellor.queueStatus)]">
              {{ counsellor.queueStatus }}
            </span>
          </td>
          <td class="td-time">{{ counsellor.duration }}</td>
        </tr>
      </tbody>
    </table>
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
    },
    availableCount: {
      type: Number,
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
.table-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow-x: auto;
}

.agent-table {
  width: 100%;
  border-collapse: collapse;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.agent-table thead, .agent-table tbody tr {
  display: table;
  width: 100%;
  table-layout: fixed;
}

.agent-table tbody {
  display: block;
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.agent-table thead th {
  background: var(--bg-color);
  color: var(--text-muted);
  padding: 10px 12px;
  text-align: left;
  font-size: 0.7rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 2px solid var(--border-color);
}

.agent-row td {
  padding: 12px;
  border-bottom: 1px solid var(--border-color);
  vertical-align: middle;
}

.th-ext, .td-ext { width: 60px; }
.th-stat, .td-stat { width: 45px; text-align: center !important; }
.th-status, .td-status { width: 100px; }
.th-time, .td-time { width: 70px; text-align: right !important; }

.td-ext {
  font-weight: 800;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.agent-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.agent-avatar {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 900;
  font-size: 0.75rem;
  flex-shrink: 0;
}

.agent-name {
  font-weight: 800;
  color: var(--text-main);
  font-size: 0.95rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: block;
}

.td-stat {
  font-weight: 700;
  color: var(--text-main);
  font-size: 0.9rem;
}

.status-pill {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.7rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.02em;
  white-space: nowrap;
}

/* Status Pill Colors - Brand Aligned */
.status-available { background: #E8F5E9; color: #0E7337; border: 1px solid #A5D6A7; }
.status-oncall { background: #FFF3E0; color: #D35400; border: 1px solid #FFCC80; }
.status-ringing { background: #FFEBEE; color: #C0392B; border: 1px solid #FFCDD2; }
.status-wrapup { background: #FFFDE7; color: #FBC02D; border: 1px solid #FFF59D; }
.status-offline { background: var(--bg-color); color: var(--text-muted); border: 1px solid var(--border-color); }

.td-time {
  font-weight: 800;
  color: var(--text-main);
  font-variant-numeric: tabular-nums;
  font-size: 0.95rem;
}

.no-agents {
  padding: 40px;
  text-align: center;
  color: var(--text-muted);
  font-style: italic;
}

.dark-mode .agent-table thead th { background: var(--card-bg); color: var(--text-muted); }
.dark-mode .agent-row td { border-bottom-color: var(--border-color); }
.dark-mode .agent-name, .dark-mode .td-stat, .dark-mode .td-time { color: white; }
</style>
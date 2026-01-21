<template>
  <div class="table-v-wrapper">
    <table class="caller-table">
      <thead>
        <tr>
          <th class="th-agent">AGENT</th>
          <th class="th-num">CALLER ID</th>
          <th class="th-status">STATUS</th>
          <th class="th-time">WAIT TIME</th>
        </tr>
      </thead>
      <tbody class="scrollable-tbody" ref="tableContainer">
        <tr v-if="callers.length === 0">
          <td colspan="4" class="no-callers">No active calls in queue</td>
        </tr>
        <tr 
          v-for="caller in callers" 
          :key="caller.id"
          class="caller-row"
        >
          <td class="td-agent">{{ caller.agentExtension || '-' }}</td>
          <td class="td-num">{{ formatNumber(caller.callerNumber) }}</td>
          <td class="td-status">
            <span :class="['status-pill', getStatusClass(caller.queueStatus)]">
              {{ caller.queueStatus }}
            </span>
          </td>
          <td class="td-time">{{ caller.waitTime }}</td>
        </tr>
      </tbody>
    </table>
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
    },
    queuedCount: {
      type: Number,
      default: 0
    }
  },
  setup(props) {
    const tableContainer = ref(null)
    let scrollInterval = null

    const formatNumber = (num) => {
      if (!num || num === '--') return '--'
      
      const countryCode = import.meta.env.VITE_COUNTRY_CODE || '255'
      
      // Remove all non-digit characters
      let clean = num.toString().replace(/\D/g, '')
      
      // Normalize specific patterns to International format
      if (clean.startsWith('0')) {
        clean = countryCode + clean.substring(1)
      } else if (!clean.startsWith(countryCode)) {
        clean = countryCode + clean
      }
      
      // Return with plus prefix: +255723456789
      return '+' + clean
    }

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

    watch(() => props.callers, () => {
      stopAutoScroll()
      setTimeout(startAutoScroll, 800)
    })

    onMounted(() => {
      setTimeout(startAutoScroll, 1500)
    })

    onBeforeUnmount(() => {
      stopAutoScroll()
    })

    return { tableContainer, formatNumber }
  },
  computed: {
    // Helper to find connected agent for UI display
    getConnectedAgent(caller) {
      return caller.agentExtension || '--'
    }
  },
  methods: {
    getStatusClass(status) {
      const s = (status || 'queue').toString().toLowerCase()
      if (s.includes('ring')) return 'status-ringing'
      if (s.includes('queue')) return 'status-inqueue'
      if (s.includes('connect')) return 'status-oncall'
      return 'status-neutral'
    }
  }
}
</script>

<style scoped>
.table-v-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow-x: auto;
}

.caller-table {
  width: 100%;
  border-collapse: collapse;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.caller-table thead, .caller-table tbody tr {
  display: table;
  width: 100%;
  table-layout: fixed;
}

.caller-table tbody {
  display: block;
  flex: 1;
  overflow-y: auto;
  min-height: 0;
}

.caller-table thead th {
  background: var(--bg-color);
  color: var(--text-muted);
  padding: 10px 12px;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 2px solid var(--border-color);
}

.caller-row td {
  padding: 14px 12px;
  border-bottom: 1px solid var(--border-color);
  vertical-align: middle;
}

.td-agent {
  font-weight: 800;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.td-num {
  font-weight: 900;
  color: var(--text-main);
  font-size: 1.1rem;
  letter-spacing: -0.02em;
}

.status-pill {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 0.7rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

/* Status Pill Colors - Brand Aligned */
.status-inqueue { background: #FFEBEE; color: #C0392B; border: 1px solid #FFCDD2; }
.status-ringing { background: #FFEBEE; color: #C0392B; border: 1px solid #FFCDD2; }
.status-oncall { background: #E8F5E9; color: #0E7337; border: 1px solid #A5D6A7; }
.status-neutral { background: var(--bg-color); color: var(--text-muted); border: 1px solid var(--border-color); }

.td-time {
  font-weight: 800;
  color: var(--text-main);
  font-variant-numeric: tabular-nums;
  text-align: right;
  font-size: 1rem;
}

.no-callers {
  padding: 40px;
  text-align: center;
  color: var(--text-muted);
  font-style: italic;
}

.dark-mode .caller-table thead th { background: var(--card-bg); color: var(--text-muted); }
.dark-mode .caller-row td { border-bottom-color: var(--border-color); }
.dark-mode .td-num, .dark-mode .td-time { color: white; }
</style>
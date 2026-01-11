<template>
  <div class="callers-section">
    <div class="minimal-section-header">
      <h2 class="title-red">Calls in Queue</h2>
      <div class="count-circle-red">{{ onlineCount }}</div>
    </div>
    <div class="callers-table minimal-table">
      <!-- Minimalist view: headers removed to match screenshot -->
      <div class="table-body" ref="tableContainer">
        <div v-if="callers.length === 0" class="no-callers-row">
          <div class="no-callers-text">No callers currently in queue</div>
        </div>
        <div 
          v-for="caller in callers" 
          :key="caller.id"
          :class="['minimal-row', { 
            'is-queueing': caller.queueStatus === 'In Queue',
            'is-connected': caller.queueStatus === 'On Call'
          }]"
        >
          <div class="minimal-col-num">{{ formatNumber(caller.callerNumber) }}</div>
          <div class="minimal-col-status">{{ caller.queueStatus }}</div>
          <div class="minimal-col-time">{{ caller.waitTime }}</div>
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

    const formatNumber = (num) => {
      if (!num || num === '--') return '--'
      // Basic formatting for visibility
      return num.replace(/(\d{3})(\d{3})(\d+)/, '$1-$2-$3')
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
.minimal-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 5px 10px 5px;
  border-bottom: 2px solid #eee;
  margin-bottom: 5px;
}

.title-red {
  color: #e11d48;
  font-size: 1.5rem;
  font-weight: 800;
  margin: 0;
}

.count-circle-red {
  background: #e11d48;
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

.minimal-table {
  background: transparent !important;
  box-shadow: none !important;
  border: none !important;
}

.minimal-row {
  display: grid;
  grid-template-columns: 1.5fr 1fr 100px;
  padding: 14px 10px;
  border-bottom: 1px solid #efefef;
  align-items: center;
  font-weight: 700;
  color: #334155;
  font-size: 1.1rem;
}

.is-queueing {
  color: #e11d48 !important;
}

.is-connected {
  color: #10b981 !important; /* Green for connected calls */
}

.minimal-col-num {
  text-align: left;
}

.minimal-col-status {
  text-align: right;
  padding-right: 20px;
}

.minimal-col-time {
  text-align: right;
  font-weight: 800;
}

.no-callers-row {
  padding: 40px;
  text-align: center;
}

.no-callers-text {
  color: #94a3b8;
  font-style: italic;
  font-size: 1rem;
}

/* TV Optimization */
@media screen and (min-width: 1920px) {
  .callers-grid {
    padding: 16px 24px;
    grid-template-columns: 1.5fr 1fr 120px 160px;
  }
}
</style>
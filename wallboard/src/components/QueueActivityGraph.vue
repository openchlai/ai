<template>
  <div class="analytics-card">
    <div v-if="loading" class="loading-indicator">Updating live trends...</div>
    <div v-if="error" class="error-indicator">{{ error }}</div>

    <div class="chart-container" v-if="rawData || (!loading && !error)">
      <div class="chart-scroll">
        <svg width="100%" height="100%" :viewBox="`0 0 ${viewWidth} ${logicalHeight}`" preserveAspectRatio="xMinYMid meet">
          <!-- Horizontal gridlines -->
          <g v-for="tick in yTicks" :key="'grid-' + tick">
            <line
              :x1="margin.left"
              :x2="viewWidth - margin.right"
              :y1="yScale(tick)"
              :y2="yScale(tick)"
              stroke="#e2e8f0"
              stroke-width="1"
              stroke-dasharray="4,4"
            />
          </g>

          <!-- Stacked Bars -->
          <g v-for="(hourData, hourIndex) in chartBars" :key="'hour-' + hourIndex">
            <!-- Stack segments for each status -->
            <rect
              v-for="(segment, segIndex) in hourData.segments"
              :key="'segment-' + segIndex"
              :x="margin.left + hourIndex * (barWidth + barSpacing)"
              :y="segment.y"
              :width="barWidth"
              :height="segment.height"
              :fill="segment.color"
              rx="2"
              ry="2"
              class="chart-bar"
            />
            
            <!-- X-axis labels (hours) -->
            <text
              :x="margin.left + hourIndex * (barWidth + barSpacing) + barWidth / 2"
              :y="logicalHeight - margin.bottom + 20"
              text-anchor="middle"
              font-size="12"
              font-weight="600"
              fill="#64748b"
            >
              {{ hourData.label }}
            </text>
          </g>

          <!-- Y-axis labels -->
          <g v-for="tick in yTicks" :key="'ylabel-' + tick">
            <text
              :x="margin.left - 10"
              :y="yScale(tick) + 4"
              text-anchor="end"
              font-size="11"
              font-weight="600"
              fill="#64748b"
            >
              {{ tick }}
            </text>
          </g>

          <!-- X-axis line -->
          <line
            :x1="margin.left"
            :x2="viewWidth - margin.right"
            :y1="logicalHeight - margin.bottom"
            :y2="logicalHeight - margin.bottom"
            stroke="#94a3b8"
            stroke-width="2"
          />

          <!-- Y-axis line -->
          <line
            :x1="margin.left"
            :x2="margin.left"
            :y1="margin.top"
            :y2="logicalHeight - margin.bottom"
            stroke="#94a3b8"
            stroke-width="2"
          />
        </svg>
      </div>
    </div>

    <!-- Dynamic Multi-Signal Legend -->
    <div class="chart-legend">
      <div 
        v-for="status in statusTypes" 
        :key="status.name"
        class="legend-item"
      >
        <span class="legend-indicator" :style="{ backgroundColor: status.color }"></span>
        <span class="legend-label">{{ status.label }}</span>
      </div>
    </div>
  </div>
</template>



<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'

export default {
  name: 'QueueActivityGraph',
  props: {
    axiosInstance: {
      type: [Object, Function],
      required: true
    }
  },
  setup(props) {
    const loading = ref(false)
    const error = ref(null)
    const rawData = ref(null)
    
    // Logical Dimensions (Coordinate System) - Scales via CSS
    const margin = { top: 20, right: 20, bottom: 50, left: 50 }
    const barWidth = 40
    const barSpacing = 12
    const logicalHeight = 400 // Canvas height for clearer resolution
    
    // Vibrant Data Signals
    const statusTypes = ref([
      { name: 'answered', label: 'Answered', color: '#0E7337', aliases: ['answered'] },
      { name: 'abandoned', label: 'Abandoned', color: '#D35400', aliases: ['abandoned'] },
      { name: 'ivr', label: 'IVR', color: '#1D3E8A', aliases: ['ivr'] },
      { name: 'missed', label: 'Missed', color: '#C0392B', aliases: ['missed'] },
      { name: 'noanswer', label: 'No Answer', color: '#E11D48', aliases: ['noanswer'] },
      { name: 'dump', label: 'Hangup', color: '#991B1B', aliases: ['dump', 'hangup', 'disconnect'] },
      { name: 'voicemail', label: 'Voicemail', color: '#10B981', aliases: ['voicemail'] }
    ])

    const fetchGraphData = async () => {
      loading.value = true
      error.value = null
      try {
        const response = await props.axiosInstance.get('/rpt', {
          params: {
            dash_period: 'today',
            type: 'bar',
            stacked: 'stacked',
            xaxis: 'hangup_status_txt',
            yaxis: 'h',
            vector: 1,
            rpt: 'call_count',
            metrics: 'call_count'
          }
        })
        rawData.value = response.data
      } catch (err) {
        console.error('Error fetching graph data:', err)
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    const chartBars = computed(() => {
      if (!rawData.value?.calls || !rawData.value?.calls_y?.[0]) return []
      
      const calls = rawData.value.calls
      const hours = rawData.value.calls_y[0]
      const hourData = {}
      
      // Initialize hours
      hours.forEach(hourSeconds => {
        const hSec = parseInt(hourSeconds)
        const hour = Math.floor(hSec / 3600)
        hourData[hSec] = {
          label: `${hour.toString().padStart(2, '0')}:00`,
          statusCounts: {},
          total: 0
        }
        statusTypes.value.forEach(s => hourData[hSec].statusCounts[s.name] = 0)
      })
      
      // Aggregate Data with Alias Support
      calls.forEach(([status, hourSeconds, count]) => {
        const hSec = parseInt(hourSeconds)
        const cNum = parseInt(count) || 0
        const sStr = String(status).toLowerCase()
        
        // Find matching status config by alias
        const config = statusTypes.value.find(type => type.aliases.some(alias => sStr.includes(alias)))
        
        if (hourData[hSec] && config) {
          hourData[hSec].statusCounts[config.name] += cNum
          hourData[hSec].total += cNum
        }
      })

      const sorted = Object.values(hourData).sort((a, b) => a.hourSeconds - b.hourSeconds)
      const maxTotal = Math.max(...sorted.map(h => h.total), 1)
      
      // Generate Segments
      return sorted.map((h, i) => {
        const segments = []
        let currentY = logicalHeight - margin.bottom
        const availH = logicalHeight - margin.top - margin.bottom
        
        statusTypes.value.forEach(s => {
          const count = h.statusCounts[s.name] || 0
          if (count > 0) {
            const segH = (count / maxTotal) * availH
            segments.push({
              color: s.color,
              height: segH,
              y: currentY - segH,
              value: count,
              status: s.label
            })
            currentY -= segH
          }
        })
        return { label: h.label, segments, total: h.total, index: i }
      })
    })

    const yScale = (value) => {
      const totals = chartBars.value.map(d => d.total)
      const maxTotal = Math.max(...totals, 5) // Ensure at least 5 lines
      const availH = logicalHeight - margin.top - margin.bottom
      return (logicalHeight - margin.bottom) - (value / maxTotal) * availH
    }

    const yTicks = computed(() => {
      const totals = chartBars.value.map(d => d.total)
      const maxTotal = Math.max(...totals, 5)
      const steps = 5
      const stepValue = Math.ceil(maxTotal / steps)
      return Array.from({ length: steps + 1 }, (_, i) => i * stepValue).filter(v => v <= maxTotal)
    })

    const viewWidth = computed(() => 
      Math.max(chartBars.value.length * (barWidth + barSpacing) + margin.left + margin.right, 600)
    )

    onMounted(() => {
      fetchGraphData()
      const interval = setInterval(fetchGraphData, 300000)
      onBeforeUnmount(() => clearInterval(interval))
    })

    return {
      loading, error, chartBars, statusTypes, margin,
      barWidth, barSpacing, viewWidth, logicalHeight,
      yScale, yTicks
    }
  }
}
</script>

<style scoped>
.analytics-card {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 24px;
  background: white;
}

.chart-container {
  flex: 1;
  width: 100%;
  position: relative;
  min-height: 0;
}

.chart-scroll {
  width: 100%;
  height: 100%;
  overflow-x: auto;
  overflow-y: hidden;
}

/* Institutional Axis & Grid */
.grid-line {
  stroke: var(--status-neutral);
  stroke-width: 1;
}

/* Institutional Legend Styling */
.chart-legend {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 20px 30px;
  padding: 20px 0;
  border-top: 1px solid var(--border-color, #e2e8f0);
  margin-top: auto;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.legend-indicator {
  display: inline-block;
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-label {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-main);
}

.loading-indicator, .error-indicator {
  padding: 40px;
  text-align: center;
  font-weight: 900;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 2px;
}

@media screen and (min-width: 1920px) {
  .legend-label { font-size: 1rem; }
}
</style>
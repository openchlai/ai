<template>
  <div class="analytics-card">
    <div class="card-header">
      <div class="section-title">Queue Activity - Today</div>
      <div v-if="loading" class="loading-indicator">Loading...</div>
      <div v-if="error" class="error-indicator">{{ error }}</div>
    </div>

    <div class="chart-container" v-if="!loading && !error">
      <div class="chart-scroll">
        <svg :width="svgWidth" :height="svgHeight">
          <defs>
            <filter id="barShadow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur in="SourceAlpha" stdDeviation="2" />
              <feOffset dx="0" dy="2" result="offsetblur" />
              <feComponentTransfer>
                <feFuncA type="linear" slope="0.2" />
              </feComponentTransfer>
              <feMerge>
                <feMergeNode />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          <!-- Horizontal gridlines -->
          <g v-for="tick in yTicks" :key="'grid-' + tick">
            <line
              :x1="margin.left"
              :x2="svgWidth - margin.right"
              :y1="yScale(tick)"
              :y2="yScale(tick)"
              stroke="#cbd5e1"
              stroke-width="0.5"
              stroke-dasharray="2,2"
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
              rx="4"
              ry="4"
              filter="url(#barShadow)"
              class="chart-bar"
            />
            
            <!-- X-axis labels (hours) -->
            <text
              :x="margin.left + hourIndex * (barWidth + barSpacing) + barWidth / 2"
              :y="svgHeight - margin.bottom + 15"
              text-anchor="middle"
              font-size="10"
              fill="#6b7280"
            >
              {{ hourData.label }}
            </text>
          </g>

          <!-- Y-axis labels -->
          <g v-for="tick in yTicks" :key="'ylabel-' + tick">
            <text
              :x="margin.left - 5"
              :y="yScale(tick) + 3"
              text-anchor="end"
              font-size="10"
              fill="#6b7280"
            >
              {{ tick }}
            </text>
          </g>

          <!-- X-axis line -->
          <line
            :x1="margin.left"
            :x2="svgWidth - margin.right"
            :y1="svgHeight - margin.bottom"
            :y2="svgHeight - margin.bottom"
            stroke="#374151"
            stroke-width="1.2"
          />

          <!-- Y-axis line -->
          <line
            :x1="margin.left"
            :x2="margin.left"
            :y1="margin.top"
            :y2="svgHeight - margin.bottom"
            stroke="#374151"
            stroke-width="1.2"
          />
        </svg>
      </div>
    </div>

    <!-- Legend -->
    <div class="chart-legend" v-if="!loading && !error">
      <div 
        v-for="status in statusTypes" 
        :key="status.name"
        class="legend-item"
      >
        <span 
          class="legend-color" 
          :style="{ backgroundColor: status.color }"
        ></span>
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
    
    // Chart dimensions & spacing
    const margin = { top: 20, right: 20, bottom: 40, left: 50 }
    const barWidth = 35
    const barSpacing = 8
    const svgHeight = 280 // Reduced from 450 to ensure 100vh fit
    
    // Status types with colors
    const statusTypes = ref([
      { name: 'answered', label: 'Answered', color: 'var(--success-color)' },
      { name: 'abandoned', label: 'Abandoned', color: 'var(--warning-color)' },
      { name: 'ivr', label: 'IVR', color: '#10b981' },
      { name: 'missed', label: 'Missed', color: 'var(--danger-color)' },
      { name: 'noanswer', label: 'No Answer', color: '#8b5cf6' },
      { name: 'dump', label: 'Dump', color: 'var(--dark-gray)' },
      { name: 'voicemail', label: 'Voicemail', color: '#06b6d4' }
    ])

    // Fetch graph data
    const fetchGraphData = async () => {
      loading.value = true
      error.value = null
      
      try {
        const response = await props.axiosInstance.get('api/wallonly/rpt', {
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
        
        // Display received data
        console.log('SVG Graph API Response:', response.data)
        console.log('Calls array:', response.data?.calls || [])
        console.log('Hours array (calls_y):', response.data?.calls_y?.[0] || [])
        
        rawData.value = response.data
        
      } catch (err) {
        console.error('Error fetching SVG graph data:', err)
        error.value = err.message
      } finally {
        loading.value = false
      }
    }

    // Process data into chart format
    const chartBars = computed(() => {
      if (!rawData.value?.calls || !rawData.value?.calls_y?.[0]) {
        return []
      }
      
      const calls = rawData.value.calls
      const hours = rawData.value.calls_y[0]
      const hourData = {}
      
      // First pass: aggregate data and find max total
      hours.forEach(hourSeconds => {
        const hourSecondsNum = parseInt(hourSeconds)
        const hour = Math.floor(hourSecondsNum / 3600)
        hourData[hourSecondsNum] = {
          label: `${hour.toString().padStart(2, '0')}:00`,
          statusCounts: {},
          total: 0
        }
        statusTypes.value.forEach(s => hourData[hourSecondsNum].statusCounts[s.name] = 0)
      })
      
      calls.forEach(([status, hourSeconds, count]) => {
        const hSec = parseInt(hourSeconds)
        const cNum = parseInt(count) || 0
        if (hourData[hSec] && statusTypes.value.find(s => s.name === status)) {
          hourData[hSec].statusCounts[status] += cNum
          hourData[hSec].total += cNum
        }
      })

      const sorted = Object.values(hourData).sort((a, b) => a.hourSeconds - b.hourSeconds)
      const maxTotal = Math.max(...sorted.map(h => h.total), 1)
      
      // Second pass: scale heights based on maxTotal
      return sorted.map(h => {
        const segments = []
        let currentY = svgHeight - margin.bottom
        const availH = svgHeight - margin.top - margin.bottom
        
        statusTypes.value.forEach(s => {
          const count = h.statusCounts[s.name] || 0
          if (count > 0) {
            const segH = (count / maxTotal) * availH
            segments.push({ color: s.color, height: segH, y: currentY - segH, value: count, status: s.label })
            currentY -= segH
          }
        })
        return { label: h.label, segments, total: h.total }
      })
    })
    
    // Y scale function helper for labels
    const yScale = (value) => {
      const totals = chartBars.value.map(d => d.total)
      const maxTotal = Math.max(...totals, 1)
      return svgHeight - margin.bottom - (value / maxTotal) * (svgHeight - margin.top - margin.bottom)
    }
    // Generate Y-axis ticks
    const yTicks = computed(() => {
      const totals = chartBars.value.map(d => d.total)
      const maxTotal = Math.max(...totals, 1)
      const steps = 5
      const stepValue = Math.ceil(maxTotal / steps)
      return Array.from({ length: steps + 1 }, (_, i) => i * stepValue)
    })

    // Dynamic width based on data count
    const svgWidth = computed(() =>
      Math.max(chartBars.value.length * (barWidth + barSpacing) + margin.left + margin.right, 600)
    )

    // Lifecycle
    onMounted(() => {
      fetchGraphData()
      
      // Auto-refresh every 5 minutes
      const refreshInterval = setInterval(fetchGraphData, 300000)
      
      onBeforeUnmount(() => {
        clearInterval(refreshInterval)
      })
    })

    return {
      loading,
      error,
      chartBars,
      statusTypes,
      margin,
      barWidth,
      barSpacing,
      svgWidth,
      svgHeight,
      yScale,
      yTicks
    }
  }
}
</script>

<style scoped>
.analytics-card {
  background: white;
  border-radius: var(--border-radius-lg);
  padding: 20px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.card-header {
  margin-bottom: 20px;
}

.section-title {
  font-size: 1.1rem;
  font-weight: 800;
  color: #1e293b;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.loading-indicator, .error-indicator {
  font-size: 0.875rem;
  padding: 8px 12px;
  border-radius: 6px;
}

.loading-indicator {
  color: #6b7280;
  background: #f3f4f6;
}

.error-indicator {
  color: #dc2626;
  background: #fef2f2;
}

.chart-container {
  overflow-x: auto;
  margin-bottom: 20px;
}

.chart-scroll {
  display: inline-block;
  min-width: 100%;
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  justify-content: center;
  border-top: 1px solid #e5e7eb;
  padding-top: 16px;
}

.dark-mode .chart-legend {
  border-top-color: #4b5563;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.legend-label {
  font-size: 0.875rem;
  color: #6b7280;
}

.dark-mode .legend-label {
  color: #9ca3af;
}

/* Dark mode styles */
.dark-mode .loading-indicator {
  background: #374151;
  color: #9ca3af;
}

.dark-mode .error-indicator {
  background: #450a0a;
  color: #f87171;
}

/* Responsive design */
@media (max-width: 768px) {
  .chart-legend {
    gap: 12px;
  }
  
  .legend-item {
    font-size: 0.75rem;
  }
}
</style>
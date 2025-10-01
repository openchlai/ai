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
          <!-- Horizontal gridlines -->
          <g v-for="tick in yTicks" :key="'grid-' + tick">
            <line
              :x1="margin.left"
              :x2="svgWidth - margin.right"
              :y1="yScale(tick)"
              :y2="yScale(tick)"
              stroke="#e5e7eb"
              stroke-width="1"
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
      type: Object,
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
    const svgHeight = 350
    
    // Status types with colors
    const statusTypes = ref([
      { name: 'answered', label: 'Answered', color: '#22c55e' },
      { name: 'abandoned', label: 'Abandoned', color: '#f59e0b' },
      { name: 'ivr', label: 'IVR', color: '#3b82f6' },
      { name: 'missed', label: 'Missed', color: '#ef4444' },
      { name: 'noanswer', label: 'No Answer', color: '#8b5cf6' },
      { name: 'dump', label: 'Dump', color: '#6b7280' },
      { name: 'voicemail', label: 'Voicemail', color: '#06b6d4' }
    ])

    // Fetch graph data
    const fetchGraphData = async () => {
      loading.value = true
      error.value = null
      
      try {
        console.log('📊 Fetching hardcoded SVG graph data...')
        
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
        
        console.log('📊 SVG Graph API Response:', response.data)
        
        // LOG THE CALLS ARRAY SPECIFICALLY
        console.log('='.repeat(60))
        console.log('📊 CALLS ARRAY DATA:')
        console.log('='.repeat(60))
        console.log('Calls array length:', response.data?.calls?.length || 0)
        console.log('Raw calls array:')
        console.log(JSON.stringify(response.data?.calls || [], null, 2))
        console.log('='.repeat(60))
        
        // Also log calls_y for hours reference
        console.log('📊 HOURS ARRAY (calls_y):')
        console.log('calls_y:', response.data?.calls_y)
        console.log('Hours array length:', response.data?.calls_y?.[0]?.length || 0)
        console.log('Raw hours:', response.data?.calls_y?.[0] || [])
        console.log('='.repeat(60))
        
        rawData.value = response.data
        
      } catch (err) {
        console.error('❌ Error fetching SVG graph data:', err)
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
      
      console.log('📊 Processing SVG chart data...')
      console.log('Calls:', calls.length)
      console.log('Hours:', hours.length)
      
      // Create hour labels and data structure
      const hourData = {}
      
      // Initialize hours
      hours.forEach(hourSeconds => {
        const hour = Math.floor(hourSeconds / 3600)
        const hourLabel = `${hour}:00`
        hourData[hourSeconds] = {
          label: hourLabel,
          hourSeconds: hourSeconds,
          statusCounts: {},
          total: 0
        }
        
        // Initialize all status counts to 0
        statusTypes.value.forEach(status => {
          hourData[hourSeconds].statusCounts[status.name] = 0
        })
      })
      
      // Fill in actual data
      calls.forEach(([status, hourSeconds, count]) => {
        const hourSecondsNum = parseInt(hourSeconds)
        if (hourData[hourSecondsNum] && statusTypes.value.find(s => s.name === status)) {
          hourData[hourSecondsNum].statusCounts[status] = parseInt(count) || 0
          hourData[hourSecondsNum].total += parseInt(count) || 0
        }
      })
      
      // Sort by hour and create bar segments
      const sortedHours = Object.values(hourData).sort((a, b) => b.hourSeconds - a.hourSeconds)
      
      // Log the processed data for verification
      console.log('📊 Processed hour data:')
      sortedHours.forEach(hourInfo => {
        console.log(`${hourInfo.label}: Total=${hourInfo.total}`, hourInfo.statusCounts)
      })
      
      return sortedHours.map(hourInfo => {
        const segments = []
        let currentY = svgHeight - margin.bottom
        const availableHeight = svgHeight - margin.top - margin.bottom
        
        // Calculate segments from bottom to top
        statusTypes.value.forEach(status => {
          const count = hourInfo.statusCounts[status.name] || 0
          if (count > 0) {
            // FIXED: Calculate segment height as proportion of max total
            const segmentHeight = (count / maxValue.value) * availableHeight
            segments.push({
              color: status.color,
              height: segmentHeight,
              y: currentY - segmentHeight,
              value: count,
              status: status.label
            })
            currentY -= segmentHeight
          }
        })
        
        return {
          label: hourInfo.label,
          segments: segments,
          total: hourInfo.total
        }
      })
    })
    
    // Dynamic width based on data count
    const svgWidth = computed(() =>
      Math.max(chartBars.value.length * (barWidth + barSpacing) + margin.left + margin.right, 600)
    )
    
    // Calculate max value for scaling
    const maxValue = computed(() => {
      const maxTotal = Math.max(...chartBars.value.map(d => d.total), 1)
      console.log('📊 Max value for scaling:', maxTotal)
      return maxTotal
    })
    
    // Y scale function
    const yScale = (value) =>
      svgHeight - margin.bottom - (value / maxValue.value) * (svgHeight - margin.top - margin.bottom)
    
    // Generate Y-axis ticks
    const yTicks = computed(() => {
      const steps = 5
      const stepValue = Math.ceil(maxValue.value / steps)
      return Array.from({ length: steps + 1 }, (_, i) => i * stepValue)
    })

    // Lifecycle
    onMounted(() => {
      console.log('📊 Hardcoded SVG Graph mounted')
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
  background: #ffffff;
  border-radius: 12px;
  padding: 20px;
  margin: 20px 0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.dark-mode .analytics-card {
  background: #2d3748;
  color: #e2e8f0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
}

.dark-mode .section-title {
  color: #f9fafb;
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
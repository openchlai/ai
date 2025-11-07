<script setup>
import { watch, ref, computed } from "vue";
import { useCaseStore } from "@/stores/cases";

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({})
  }
})

const store = useCaseStore();
const localData = ref([]);

const fetchData = async () => {
  await store.listCases({
    xaxis: "src",
    yaxis: "dt",
    metrics: "case_count",
    ...props.filters
  });
  // Copy data to local storage
  localData.value = [...store.cases];
}

// Convert unix timestamp to readable date
const formatDate = (unixTimestamp) => {
  const date = new Date(parseInt(unixTimestamp) * 1000);
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
};

// Process data for chart
const chartData = computed(() => {
  if (!localData.value || localData.value.length === 0) return { sources: [], dates: [], series: [] };
  
  // Group data by source and date
  const sourceMap = {};
  const datesSet = new Set();
  
  localData.value.forEach(row => {
    const source = row[0];
    const timestamp = row[1];
    const cases = parseInt(row[2]);
    
    if (!sourceMap[source]) {
      sourceMap[source] = {};
    }
    sourceMap[source][timestamp] = cases;
    datesSet.add(timestamp);
  });
  
  // Sort dates
  const sortedDates = Array.from(datesSet).sort((a, b) => parseInt(a) - parseInt(b));
  
  // Create series data for each source
  const colors = {
    'call': '#3B82F6',
    'ceemis': '#10B981',
    'chat': '#F59E0B',
    'safepal': '#EF4444',
    'walkin': '#8B5CF6',
    'webform': '#EC4899',
    'sms': '#14B8A6',
    'email': '#F97316',
    'social': '#6366F1'
  };
  
  const series = Object.keys(sourceMap).map(source => ({
    name: source,
    color: colors[source] || '#6B7280',
    data: sortedDates.map(date => sourceMap[source][date] || 0)
  }));
  
  return {
    sources: Object.keys(sourceMap),
    dates: sortedDates,
    series
  };
});

// Calculate total cases
const totalCases = computed(() => {
  if (!localData.value || localData.value.length === 0) return 0;
  return localData.value.reduce((sum, row) => sum + parseInt(row[2]), 0);
});

// Get max value for scaling
const maxValue = computed(() => {
  if (chartData.value.series.length === 0) return 0;
  return Math.max(...chartData.value.series.flatMap(s => s.data));
});

// Watch filters and refetch when they change
watch(() => props.filters, () => {
  fetchData();
}, { deep: true, immediate: true });
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-4">
      <h2 class="font-bold text-lg">Cases by Source Per Day</h2>
      <div class="text-2xl font-bold text-blue-600">
        {{ totalCases }} <span class="text-sm text-gray-500">Total</span>
      </div>
    </div>

    <div v-if="!localData || localData.length === 0" class="text-gray-500 text-center py-8">
      No data available
    </div>

    <div v-else class="space-y-4">
      <!-- Bar Chart -->
      <div class="w-full overflow-x-auto">
        <svg :viewBox="`0 0 ${Math.max(600, chartData.dates.length * 100)} 280`" class="w-full" :style="`min-width: ${Math.max(600, chartData.dates.length * 100)}px;`">
          <!-- Grid lines -->
          <g v-for="i in 5" :key="'grid-' + i">
            <line
              :x1="60"
              :y1="40 + (i - 1) * 40"
              :x2="Math.max(600, chartData.dates.length * 100) - 40"
              :y2="40 + (i - 1) * 40"
              stroke="#E5E7EB"
              stroke-width="1"
            />
            <!-- Y-axis labels -->
            <text
              :x="50"
              :y="44 + (i - 1) * 40"
              text-anchor="end"
              class="text-xs fill-gray-600"
              font-size="10"
            >
              {{ Math.round(maxValue - (i - 1) * (maxValue / 4)) }}
            </text>
          </g>
          
          <!-- Bars grouped by date -->
          <g v-for="(date, dateIndex) in chartData.dates" :key="'date-group-' + dateIndex">
            <g v-for="(serie, serieIndex) in chartData.series" :key="serie.name">
              <rect
                v-if="serie.data[dateIndex] > 0"
                :x="60 + dateIndex * 100 + serieIndex * (80 / chartData.series.length)"
                :y="240 - 40 - ((serie.data[dateIndex] / maxValue) * 160)"
                :width="80 / chartData.series.length - 2"
                :height="(serie.data[dateIndex] / maxValue) * 160"
                :fill="serie.color"
                class="hover:opacity-80 transition-opacity"
              >
                <title>{{ serie.name }}: {{ serie.data[dateIndex] }} on {{ formatDate(date) }}</title>
              </rect>
            </g>
            
            <!-- X-axis labels (dates) -->
            <text
              :x="60 + dateIndex * 100 + 40"
              y="265"
              text-anchor="middle"
              class="text-xs fill-gray-600"
              font-size="10"
            >
              {{ formatDate(date) }}
            </text>
          </g>
        </svg>
      </div>

      <!-- Legend -->
      <div class="flex flex-wrap gap-4 justify-center text-sm">
        <div 
          v-for="serie in chartData.series" 
          :key="serie.name"
          class="flex items-center gap-2"
        >
          <div 
            class="w-4 h-4 rounded"
            :style="{ backgroundColor: serie.color }"
          ></div>
          <span class="capitalize">{{ serie.name }}</span>
          <span class="text-gray-600">({{ serie.data.reduce((a, b) => a + b, 0) }})</span>
        </div>
      </div>
    </div>
  </div>
</template>
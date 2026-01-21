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
    xaxis: "cat_0",
    yaxis: "-",
    metrics: "case_count",
    ...props.filters
  });
  // Copy data to local storage
  localData.value = [...store.cases];
}

// Compute chart data from local data
const chartData = computed(() => {
  if (!localData.value || localData.value.length === 0) return [];
  
  const total = localData.value.reduce((sum, row) => sum + parseInt(row[1]), 0);
  let currentAngle = 0;
  
  const colors = [
    '#3B82F6', '#10B981', '#F59E0B', '#EF4444', 
    '#8B5CF6', '#EC4899', '#14B8A6', '#F97316'
  ];
  
  return localData.value.map((row, index) => {
    const value = parseInt(row[1]);
    const percentage = (value / total) * 100;
    const angle = (value / total) * 360;
    
    const slice = {
      label: row[0],
      value: value,
      percentage: percentage.toFixed(1),
      color: colors[index % colors.length],
      startAngle: currentAngle,
      endAngle: currentAngle + angle
    };
    
    currentAngle += angle;
    return slice;
  });
});

// Calculate total cases
const totalCases = computed(() => {
  if (!localData.value || localData.value.length === 0) return 0;
  return localData.value.reduce((sum, row) => sum + parseInt(row[1]), 0);
});

// Generate SVG path for pie slice
const getSlicePath = (startAngle, endAngle) => {
  const cx = 100;
  const cy = 100;
  const radius = 80;
  
  const startRad = (startAngle - 90) * Math.PI / 180;
  const endRad = (endAngle - 90) * Math.PI / 180;
  
  const x1 = cx + radius * Math.cos(startRad);
  const y1 = cy + radius * Math.sin(startRad);
  const x2 = cx + radius * Math.cos(endRad);
  const y2 = cy + radius * Math.sin(endRad);
  
  const largeArc = endAngle - startAngle > 180 ? 1 : 0;
  
  return `M ${cx} ${cy} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z`;
};

// Watch filters and refetch when they change
watch(() => props.filters, () => {
  fetchData();
}, { deep: true, immediate: true });
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-4">
      <h2 class="font-bold text-lg">Case Categories</h2>
      <div class="text-2xl font-bold text-blue-600">
        {{ totalCases }} <span class="text-sm text-gray-500">Total</span>
      </div>
    </div>

    <div v-if="!localData || localData.length === 0" class="text-gray-500 text-center py-8">
      No data available
    </div>

    <div v-else class="space-y-4">
      <!-- SVG Pie Chart -->
      <div class="flex justify-center">
        <svg viewBox="0 0 200 200" class="w-64 h-64">
          <g v-for="(slice, index) in chartData" :key="index">
            <path
              :d="getSlicePath(slice.startAngle, slice.endAngle)"
              :fill="slice.color"
              class="hover:opacity-80 transition-opacity cursor-pointer"
              stroke="white"
              stroke-width="2"
            >
              <title>{{ slice.label }}: {{ slice.value }} ({{ slice.percentage }}%)</title>
            </path>
          </g>
        </svg>
      </div>

      <!-- Legend -->
      <div class="grid grid-cols-2 gap-2 text-sm">
        <div 
          v-for="(slice, index) in chartData" 
          :key="index"
          class="flex items-center gap-2"
        >
          <div 
            class="w-4 h-4 rounded"
            :style="{ backgroundColor: slice.color }"
          ></div>
          <span class="truncate">{{ slice.label }}</span>
          <span class="text-gray-600 ml-auto">{{ slice.value }}</span>
        </div>
      </div>
    </div>
  </div>
</template>
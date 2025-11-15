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
    xaxis: "final_status,priority",
    yaxis: "-",
    metrics: "case_count",
    ...props.filters
  });
  // Copy data to local storage
  localData.value = [...store.cases];
}

// Process data for status and priority
const processedData = computed(() => {
  if (!localData.value || localData.value.length === 0) {
    return { status: [], priority: [] };
  }
  
  // Aggregate by status (first column)
  const statusMap = {
    '1': { label: 'Ongoing', value: 0, color: '#3B82F6' },
    '2': { label: 'Closed', value: 0, color: '#10B981' },
    '3': { label: 'Escalated', value: 0, color: '#EF4444' }
  };
  
  // Aggregate by priority (second column)
  const priorityMap = {
    '1': { label: 'Low', value: 0, color: '#10B981' },
    '2': { label: 'Medium', value: 0, color: '#F59E0B' },
    '3': { label: 'High', value: 0, color: '#EF4444' }
  };
  
  localData.value.forEach(row => {
    const status = row[0];
    const priority = row[1];
    const cases = parseInt(row[2]);
    
    if (statusMap[status]) {
      statusMap[status].value += cases;
    }
    
    if (priorityMap[priority]) {
      priorityMap[priority].value += cases;
    }
  });
  
  return {
    status: Object.values(statusMap),
    priority: Object.values(priorityMap)
  };
});

// Calculate totals
const totalCases = computed(() => {
  if (!localData.value || localData.value.length === 0) return 0;
  return localData.value.reduce((sum, row) => sum + parseInt(row[2]), 0);
});

const statusTotal = computed(() => {
  return processedData.value.status.reduce((sum, item) => sum + item.value, 0);
});

const priorityTotal = computed(() => {
  return processedData.value.priority.reduce((sum, item) => sum + item.value, 0);
});

// Watch filters and refetch when they change
watch(() => props.filters, () => {
  fetchData();
}, { deep: true, immediate: true });
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-4">
      <h2 class="font-bold text-lg">Case Status & Priority</h2>
      <div class="text-2xl font-bold text-blue-600">
        {{ totalCases }} <span class="text-sm text-gray-500">Total</span>
      </div>
    </div>

    <div v-if="!localData || localData.length === 0" class="text-gray-500 text-center py-8">
      No data available
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Status Section -->
      <div class="space-y-3">
        <h3 class="font-semibold text-gray-700 text-sm">By Status</h3>
        
        <div v-for="item in processedData.status" :key="item.label" class="space-y-1">
          <div class="flex justify-between text-sm">
            <span class="font-medium">{{ item.label }}</span>
            <span class="text-gray-600">{{ item.value }} ({{ ((item.value / statusTotal) * 100).toFixed(1) }}%)</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-6 relative overflow-hidden">
            <div 
              class="h-full rounded-full transition-all duration-500 flex items-center justify-end pr-2"
              :style="{ 
                width: `${(item.value / statusTotal) * 100}%`,
                backgroundColor: item.color
              }"
            >
              <span class="text-white text-xs font-semibold">{{ item.value }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Priority Section -->
      <div class="space-y-3">
        <h3 class="font-semibold text-gray-700 text-sm">By Priority</h3>
        
        <div v-for="item in processedData.priority" :key="item.label" class="space-y-1">
          <div class="flex justify-between text-sm">
            <span class="font-medium">{{ item.label }}</span>
            <span class="text-gray-600">{{ item.value }} ({{ ((item.value / priorityTotal) * 100).toFixed(1) }}%)</span>
          </div>
          <div class="w-full bg-gray-200 rounded-full h-6 relative overflow-hidden">
            <div 
              class="h-full rounded-full transition-all duration-500 flex items-center justify-end pr-2"
              :style="{ 
                width: `${(item.value / priorityTotal) * 100}%`,
                backgroundColor: item.color
              }"
            >
              <span class="text-white text-xs font-semibold">{{ item.value }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
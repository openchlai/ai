<script setup>
import { watch, ref, computed, inject } from "vue"
import { useCaseStore } from "@/stores/cases"

// Inject theme
const isDarkMode = inject('isDarkMode')

const props = defineProps({
  filters: {
    type: Object,
    default: () => ({})
  }
})

const store = useCaseStore()
const localData = ref([])

const fetchData = async () => {
  await store.listCases({
    xaxis: "final_status,priority",
    yaxis: "-",
    metrics: "case_count",
    ...props.filters
  })
  localData.value = [...store.cases]
}

// Theme-aware status and priority colors
const statusColors = computed(() => {
  if (isDarkMode.value) {
    return {
      '1': { label: 'Ongoing', color: '#3B82F6' },   // Blue
      '2': { label: 'Closed', color: '#10B981' },    // Green
      '3': { label: 'Escalated', color: '#EF4444' }  // Red
    }
  } else {
    return {
      '1': { label: 'Ongoing', color: '#2563EB' },   // Blue-600 (stands out in light mode)
      '2': { label: 'Closed', color: '#059669' },    // Emerald-600
      '3': { label: 'Escalated', color: '#DC2626' }  // Red-600
    }
  }
})

const priorityColors = computed(() => {
  if (isDarkMode.value) {
    return {
      '1': { label: 'Low', color: '#10B981' },    // Green
      '2': { label: 'Medium', color: '#F59E0B' }, // Amber
      '3': { label: 'High', color: '#EF4444' }    // Red
    }
  } else {
    return {
      '1': { label: 'Low', color: '#059669' },    // Emerald-600
      '2': { label: 'Medium', color: '#EA580C' }, // Orange-600
      '3': { label: 'High', color: '#DC2626' }    // Red-600
    }
  }
})

// Process data for status and priority
const processedData = computed(() => {
  if (!localData.value || localData.value.length === 0) {
    return { status: [], priority: [] }
  }
  
  // Aggregate by status
  const statusMap = {
    '1': { ...statusColors.value['1'], value: 0 },
    '2': { ...statusColors.value['2'], value: 0 },
    '3': { ...statusColors.value['3'], value: 0 }
  }
  
  // Aggregate by priority
  const priorityMap = {
    '1': { ...priorityColors.value['1'], value: 0 },
    '2': { ...priorityColors.value['2'], value: 0 },
    '3': { ...priorityColors.value['3'], value: 0 }
  }
  
  localData.value.forEach(row => {
    const status = row[0]
    const priority = row[1]
    const cases = parseInt(row[2])
    
    if (statusMap[status]) {
      statusMap[status].value += cases
    }
    
    if (priorityMap[priority]) {
      priorityMap[priority].value += cases
    }
  })
  
  return {
    status: Object.values(statusMap),
    priority: Object.values(priorityMap)
  }
})

// Calculate totals
const totalCases = computed(() => {
  if (!localData.value || localData.value.length === 0) return 0
  return localData.value.reduce((sum, row) => sum + parseInt(row[2]), 0)
})

const statusTotal = computed(() => {
  return processedData.value.status.reduce((sum, item) => sum + item.value, 0)
})

const priorityTotal = computed(() => {
  return processedData.value.priority.reduce((sum, item) => sum + item.value, 0)
})

// Watch filters and refetch when they change
watch(() => props.filters, () => {
  fetchData()
}, { deep: true, immediate: true })
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 
        class="font-semibold text-base"
        :class="isDarkMode ? 'text-gray-200' : 'text-gray-800'"
      >
        Case Status & Priority
      </h2>
      <div 
        class="text-3xl font-bold"
        :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
      >
        {{ totalCases }} 
        <span 
          class="text-sm font-normal"
          :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
        >
          Total
        </span>
      </div>
    </div>

    <div 
      v-if="!localData || localData.length === 0" 
      class="text-center py-12"
      :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
    >
      No data available
    </div>

    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-8">
      <!-- Status Section -->
      <div class="space-y-4">
        <h3 
          class="font-medium text-sm uppercase tracking-wide"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          By Status
        </h3>
        
        <div v-for="item in processedData.status" :key="item.label" class="space-y-2">
          <div class="flex justify-between text-sm">
            <span 
              class="font-medium"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              {{ item.label }}
            </span>
            <span 
              :class="isDarkMode ? 'text-gray-500' : 'text-gray-600'"
            >
              {{ item.value }} 
              <span 
                :class="isDarkMode ? 'text-gray-600' : 'text-gray-500'"
              >
                ({{ ((item.value / statusTotal) * 100).toFixed(1) }}%)
              </span>
            </span>
          </div>
          <div 
            class="w-full rounded-full h-7 relative overflow-hidden border"
            :class="isDarkMode 
              ? 'bg-gray-900/60 border-transparent' 
              : 'bg-gray-100 border-transparent'"
          >
            <div 
              class="h-full rounded-full transition-all duration-500 flex items-center justify-end pr-3"
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
      <div class="space-y-4">
        <h3 
          class="font-medium text-sm uppercase tracking-wide"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          By Priority
        </h3>
        
        <div v-for="item in processedData.priority" :key="item.label" class="space-y-2">
          <div class="flex justify-between text-sm">
            <span 
              class="font-medium"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              {{ item.label }}
            </span>
            <span 
              :class="isDarkMode ? 'text-gray-500' : 'text-gray-600'"
            >
              {{ item.value }} 
              <span 
                :class="isDarkMode ? 'text-gray-600' : 'text-gray-500'"
              >
                ({{ ((item.value / priorityTotal) * 100).toFixed(1) }}%)
              </span>
            </span>
          </div>
          <div 
            class="w-full rounded-full h-7 relative overflow-hidden border"
            :class="isDarkMode 
              ? 'bg-gray-900/60 border-transparent' 
              : 'bg-gray-100 border-transparent'"
          >
            <div 
              class="h-full rounded-full transition-all duration-500 flex items-center justify-end pr-3"
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
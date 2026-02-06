<template>
  <div class="space-y-8 animate-in fade-in duration-500">
    <!-- Header / Controls -->
    <div class="bg-white dark:bg-black border dark:border-gray-800 rounded-lg p-6 shadow-sm">
      <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 class="text-xl font-bold dark:text-white">CHI Core Data Reports</h2>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Standard reporting metrics aligned with Child Helpline International definitions.
          </p>
        </div>
        
        <!-- Date Filter -->
        <div class="flex items-center gap-2">
          <select 
            v-model="timeRange" 
            class="px-3 py-2 bg-gray-50 dark:bg-gray-800 border-none rounded-lg text-sm focus:ring-2 focus:ring-amber-500"
          >
            <option value="today">Today</option>
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
            <option value="year">This Year</option>
          </select>
          <button 
            @click="refreshData"
            class="p-2 text-amber-600 hover:bg-amber-50 dark:hover:bg-amber-900/20 rounded-lg transition-colors"
          >
            <i-mdi-refresh class="w-5 h-5" :class="{ 'animate-spin': loading }" />
          </button>
        </div>
      </div>
    </div>

    <!-- 1. Demographics Matrix (Age vs Gender) -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-white dark:bg-black border dark:border-gray-800 rounded-lg p-6 shadow-sm ring-1 ring-gray-950/5 hover:ring-gray-950/10 transition-all">
        <h3 class="font-semibold text-lg mb-4 flex items-center gap-2 dark:text-white">
          <i-mdi-account-group class="text-amber-500" />
          Demographics Matrix
        </h3>
        
        <div v-if="loading" class="h-64 flex items-center justify-center">
          <div class="animate-spin w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full"></div>
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm text-left">
            <thead class="bg-gray-50 dark:bg-gray-900 text-xs uppercase font-bold text-gray-500 dark:text-gray-400">
              <tr>
                <th class="px-4 py-3 rounded-tl-lg">Age Group</th>
                <th class="px-4 py-3 text-center">Male</th>
                <th class="px-4 py-3 text-center">Female</th>
                <th class="px-4 py-3 text-center">Other/Unknown</th>
                <th class="px-4 py-3 text-right rounded-tr-lg">Total</th>
              </tr>
            </thead>
            <tbody class="divide-y dark:divide-gray-800">
              <tr v-for="age in ageGroups" :key="age" class="hover:bg-gray-50 dark:hover:bg-gray-900/50">
                <td class="px-4 py-3 font-medium dark:text-gray-200">{{ age }}</td>
                <td class="px-4 py-3 text-center text-gray-600 dark:text-gray-400">{{ getMatrixValue(age, 'Male') }}</td>
                <td class="px-4 py-3 text-center text-gray-600 dark:text-gray-400">{{ getMatrixValue(age, 'Female') }}</td>
                <td class="px-4 py-3 text-center text-gray-600 dark:text-gray-400">{{ getMatrixValue(age, 'Other') }}</td>
                <td class="px-4 py-3 text-right font-bold dark:text-white">{{ getMatrixRowTotal(age) }}</td>
              </tr>
              <tr class="bg-gray-50 dark:bg-gray-900 font-bold border-t-2 dark:border-gray-800">
                <td class="px-4 py-3">Total</td>
                <td class="px-4 py-3 text-center">{{ getMatrixColTotal('Male') }}</td>
                <td class="px-4 py-3 text-center">{{ getMatrixColTotal('Female') }}</td>
                <td class="px-4 py-3 text-center">{{ getMatrixColTotal('Other') }}</td>
                <td class="px-4 py-3 text-right text-amber-600 dark:text-amber-500">{{ grandTotalContacts }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 2. Contacts by Method -->
      <div class="bg-white dark:bg-black border dark:border-gray-800 rounded-lg p-6 shadow-sm">
        <h3 class="font-semibold text-lg mb-4 flex items-center gap-2 dark:text-white">
          <i-mdi-phone-classic class="text-amber-500" />
          Contact Methods
        </h3>
        
        <div v-if="contactsByMethod.length === 0" class="h-64 flex items-center justify-center text-gray-400 text-sm">
           No data available
        </div>
        
        <div v-else class="space-y-4">
           <div v-for="item in contactsByMethod" :key="item.label" class="space-y-1">
              <div class="flex justify-between text-sm">
                 <span class="font-medium dark:text-gray-300 capitalize">{{ item.label }}</span>
                 <span class="text-gray-500">{{ item.value }} ({{ item.percent }}%)</span>
              </div>
              <div class="h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
                 <div class="h-full bg-amber-500 rounded-full" :style="{ width: item.percent + '%' }"></div>
              </div>
           </div>
        </div>
      </div>
    </div>

    <!-- 3. Top Issues (Categories) -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
       <!-- Pie Chart Container -->
       <div class="lg:col-span-2 bg-white dark:bg-black border dark:border-gray-800 rounded-lg p-6 shadow-sm">
          <h3 class="font-semibold text-lg mb-6 flex items-center gap-2 dark:text-white">
             <i-mdi-shape class="text-amber-500" />
             Main Reasons for Contact
          </h3>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">
             <!-- Chart Circle -->
             <div class="relative w-48 h-48 mx-auto">
                <svg viewBox="0 0 100 100" class="transform -rotate-90 w-full h-full">
                   <circle v-for="(slice, i) in categoryChart" :key="i"
                      cx="50" cy="50" r="40"
                      fill="transparent"
                      stroke-width="20"
                      :stroke="slice.color"
                      :stroke-dasharray="slice.dashArray"
                      :stroke-dashoffset="slice.dashOffset"
                      class="transition-all duration-1000 ease-out hover:opacity-80"
                   />
                </svg>
                <div class="absolute inset-0 flex items-center justify-center flex-col">
                   <span class="text-2xl font-bold dark:text-white">{{ totalIssues }}</span>
                   <span class="text-xs text-gray-500 uppercase">Issues</span>
                </div>
             </div>
             
             <!-- Legend -->
             <div class="space-y-3">
                <div v-for="(slice, i) in categoryChart" :key="i" class="flex items-center gap-3">
                   <div class="w-3 h-3 rounded-full" :style="{ backgroundColor: slice.color }"></div>
                   <div class="flex-1 min-w-0">
                      <div class="flex justify-between text-sm">
                         <span class="truncate font-medium dark:text-gray-300">{{ slice.label }}</span>
                         <span class="text-gray-500">{{ slice.value }}</span>
                      </div>
                   </div>
                </div>
             </div>
          </div>
       </div>

       <!-- 4. Referrals / Actions -->
       <div class="bg-white dark:bg-black border dark:border-gray-800 rounded-lg p-6 shadow-sm">
          <h3 class="font-semibold text-lg mb-4 flex items-center gap-2 dark:text-white">
             <i-mdi-hand-heart class="text-amber-500" />
             Actions Taken
          </h3>
          <div class="space-y-4">
            <div v-for="(action, i) in actionsList" :key="i" class="p-3 bg-gray-50 dark:bg-gray-900 rounded-lg flex items-center justify-between">
               <span class="text-sm dark:text-gray-300">{{ action.label }}</span>
               <span class="font-bold text-amber-600 dark:text-amber-500">{{ action.value }}</span>
            </div>
            <div v-if="actionsList.length === 0" class="text-center py-8 text-gray-400 text-sm">
               No actions recorded
            </div>
          </div>
       </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useCaseStore } from '@/stores/cases'

const store = useCaseStore()
const loading = ref(false)
const timeRange = ref('month')

const ageGroups = ['0-5', '6-9', '10-12', '13-15', '16-18', '19-24', 'Adult', 'Unknown']
const colors = ['#f59e0b', '#10b981', '#3b82f6', '#ef4444', '#8b5cf6', '#ec4899', '#6366f1']

// State for data
const demographicsData = ref([])
const methodsData = ref([])
const categoriesData = ref([])
const actionsData = ref([])

// Mock Matrix Generation (Until Backend fully supports cross-tab)
// Real implementation: We fetch 'age,sex' and 'metrics=count'
const getMatrixValue = (age, gender) => {
   // Find row matching age and gender
   // This assumes backend returns [age, gender, count]
   const match = demographicsData.value.find(r => r[0] === age && r[1] === gender)
   return match ? parseInt(match[2]) : 0
}

const getMatrixRowTotal = (age) => {
   return demographicsData.value
      .filter(r => r[0] === age)
      .reduce((sum, r) => sum + parseInt(r[2]), 0)
}

const getMatrixColTotal = (gender) => {
   return demographicsData.value
      .filter(r => r[1] === gender)
      .reduce((sum, r) => sum + parseInt(r[2]), 0)
}

const grandTotalContacts = computed(() => {
   return demographicsData.value.reduce((sum, r) => sum + parseInt(r[2] || 0), 0)
})

// Computed Props for Charts
const contactsByMethod = computed(() => {
   const total = methodsData.value.reduce((s, r) => s + parseInt(r[1]), 0)
   return methodsData.value.map(row => ({
      label: row[0],
      value: parseInt(row[1]),
      percent: total ? Math.round((parseInt(row[1]) / total) * 100) : 0
   })).sort((a,b) => b.value - a.value)
})

const totalIssues = computed(() => categoriesData.value.reduce((s, r) => s + parseInt(r[1]), 0))

const categoryChart = computed(() => {
   const total = totalIssues.value
   let accumulator = 0
   return categoriesData.value.slice(0, 6).map((row, i) => { // Top 6
      const val = parseInt(row[1])
      const pct = val / total
      const dashArray = `${pct * 251.2} 251.2`
      const dashOffset = -accumulator * 251.2
      accumulator += pct
      
      return {
         label: row[0],
         value: val,
         color: colors[i % colors.length],
         dashArray,
         dashOffset
      }
   })
})

const actionsList = computed(() => {
   return actionsData.value.map(row => ({
      label: row[0],
      value: row[1]
   }))
})

// Data Fetching
const refreshData = async () => {
   loading.value = true
   try {
      // 1. Demographics: Age x Sex
      // We fetch raw columns (yaxis) instead of grouping (xaxis) to ensure data retrieval
      // even if the backend doesn't support multi-level grouping.
      const demoRes = await store.getAnalytics({ 
          xaxis: '-', 
          yaxis: 'age,sex', 
          metrics: 'case_count', 
          _c: 9999 
      })
      
      const rawCases = demoRes.cases || []
      const matrixMap = []
      
      rawCases.forEach(row => {
          // Expected row: [timestamp, age, sex, count]
          // We extract Age and Sex safely
          const ageVal = String(row[1] || 'Unknown')
          const sexVal = String(row[2] || 'Unknown')
          const count = 1 // Count is 1 per row in raw list
          
          // Map Sex
          let gender = 'Other'
          const s = sexVal.toLowerCase()
          if (s === 'male' || s === 'm' || s === '115' || s === 'boy') gender = 'Male'
          else if (s === 'female' || s === 'f' || s === '116' || s === 'girl') gender = 'Female'
          
          // Map Age
          let ageGroup = 'Unknown'
          const ageNum = parseInt(ageVal)
          if (!isNaN(ageNum)) {
            if (ageNum <= 5) ageGroup = '0-5'
            else if (ageNum <= 9) ageGroup = '6-9'
            else if (ageNum <= 12) ageGroup = '10-12'
            else if (ageNum <= 15) ageGroup = '13-15'
            else if (ageNum <= 18) ageGroup = '16-18'
            else if (ageNum <= 24) ageGroup = '19-24'
            else ageGroup = 'Adult'
          } else {
             // If age is already a string range or empty
             if (ageVal && ageVal !== 'Unknown') ageGroup = ageVal
          }

          // Aggregate
          const existing = matrixMap.find(m => m[0] === ageGroup && m[1] === gender)
          if (existing) {
             existing[2] += count
          } else {
             matrixMap.push([ageGroup, gender, count])
          }
      })
      
      demographicsData.value = matrixMap

      // 2. Methods: Source
      const methodRes = await store.getAnalytics({ xaxis: 'src', metrics: 'case_count', _c: 9999 })
      methodsData.value = methodRes.cases || []

      // 3. Issues: Main Category
      const catRes = await store.getAnalytics({ xaxis: 'cat_0', metrics: 'case_count', _c: 9999 })
      categoriesData.value = catRes.cases || []
      
      // 4. Actions: Referrals
      // This might be 'referrals' or 'services' depending on backend
      const actRes = await store.getAnalytics({ xaxis: 'disposition', metrics: 'case_count', _c: 9999 })
      actionsData.value = actRes.cases || []

   } catch (e) {
      console.error('CHI Reports Error:', e)
   } finally {
      loading.value = false
   }
}

onMounted(() => {
   refreshData()
})
</script>

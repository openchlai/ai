<template>
  <div 
    class="w-full rounded-lg p-4 shadow-xl border border-transparent mb-4"
    :class="isDarkMode 
      ? 'bg-black' 
      : 'bg-white'"
  >
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Global Search -->
      <div class="flex flex-col">
        <label class="text-sm font-medium mb-1" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
          Search
        </label>
        <div class="relative">
          <input type="text" v-model="filters.q" placeholder="Keywords, narrative..."
            class="w-full rounded px-9 py-2 text-sm focus:outline-none focus:ring-2 focus:border-transparent" :class="isDarkMode
              ? 'bg-neutral-800 border border-transparent text-gray-100 placeholder-gray-500 focus:ring-amber-50'
              : 'bg-gray-50 border border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'" />
          <i-mdi-magnify class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
        </div>
      </div>

      <!-- Case ID -->
      <div class="flex flex-col">
        <label class="text-sm font-medium mb-1" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
          Case ID
        </label>
        <input type="text" v-model="filters.caseId" placeholder="Enter case ID"
          class="rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:border-transparent" :class="isDarkMode
            ? 'bg-neutral-800 border border-transparent text-gray-100 placeholder-gray-500 focus:ring-amber-500'
            : 'bg-gray-50 border border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'" />
      </div>

      <!-- Date Range From -->
      <div class="flex flex-col">
        <label class="text-sm font-medium mb-1" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
          From Date
        </label>
        <input type="date" v-model="filters.dateFrom"
          class="rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:border-transparent" :class="isDarkMode
            ? 'bg-neutral-800 border border-transparent text-gray-100 focus:ring-amber-500'
            : 'bg-gray-50 border border-transparent text-gray-900 focus:ring-amber-600'" />
      </div>

      <!-- Date Range To -->
      <div class="flex flex-col">
        <label class="text-sm font-medium mb-1" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
          To Date
        </label>
        <input type="date" v-model="filters.dateTo"
          class="rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:border-transparent" :class="isDarkMode
            ? 'bg-neutral-800 border border-transparent text-gray-100 focus:ring-amber-500'
            : 'bg-gray-50 border border-transparent text-gray-900 focus:ring-amber-600'" />
      </div>
    </div>

    <!-- Advanced Filters Toggle -->
    <div class="mt-4 flex items-center">
      <button @click="showAdvanced = !showAdvanced"
        class="text-xs font-semibold flex items-center gap-1 transition-colors"
        :class="isDarkMode ? 'text-amber-500 hover:text-amber-400' : 'text-amber-700 hover:text-amber-800'">
        <component :is="showAdvanced ? 'i-mdi-chevron-up' : 'i-mdi-chevron-down'" class="w-4 h-4" />
        {{ showAdvanced ? 'Hide Advanced Filters' : 'Show Advanced Filters' }}
      </button>
      <div class="h-[1px] flex-1 ml-4" :class="isDarkMode ? 'bg-neutral-800' : 'bg-gray-100'"></div>
    </div>

    <!-- Advanced Filters Content -->
    <Transition name="fade">
      <div v-if="showAdvanced" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
        <!-- Created By -->
        <div class="flex flex-col">
          <label class="text-sm font-medium mb-1" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            Created By
          </label>
          <input type="text" v-model="filters.createdBy" placeholder="Enter name"
            class="rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:border-transparent" :class="isDarkMode
              ? 'bg-neutral-800 border border-transparent text-gray-100 placeholder-gray-500 focus:ring-amber-500'
              : 'bg-gray-50 border border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'" />
        </div>

        <!-- Source -->
        <div class="flex flex-col">
          <label class="text-sm font-medium mb-1" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            Source
          </label>
          <select v-model="filters.source"
            class="rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:border-transparent" :class="isDarkMode
              ? 'bg-neutral-800 border border-transparent text-gray-100 focus:ring-amber-500'
              : 'bg-gray-50 border border-transparent text-gray-900 focus:ring-amber-600'">
            <option value="">All</option>
            <option value="walkin">Walk-in</option>
            <option value="call">Call</option>
            <option value="sms">SMS</option>
            <option value="email">Email</option>
            <option value="chat">Chat</option>
            <option value="whatsApp">WhatsApp</option>
            <option value="FACEBOOK">Facebook</option>
            <option value="TWITTER">Twitter</option>
            <option value="WENI">Weni</option>
            <option value="safepal">SafePal</option>
            <option value="ai">AI</option>
            <option value="aii">AII</option>
          </select>
        </div>

        <!-- Department -->
        <div class="flex flex-col">
          <label class="text-sm font-medium mb-1" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            Department
          </label>
          <select v-model="filters.dept"
            class="rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:border-transparent" :class="isDarkMode
              ? 'bg-neutral-800 border border-transparent text-gray-100 focus:ring-amber-500'
              : 'bg-gray-50 border border-transparent text-gray-900 focus:ring-amber-600'">
            <option value="">All</option>
            <option value="1">116</option>
            <option value="2">Labor</option>
          </select>
        </div>

        <!-- GBV Related -->
        <div class="flex flex-col">
          <label class="text-sm font-medium mb-1" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            GBV Related
          </label>
          <select v-model="filters.gbv_related"
            class="rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:border-transparent" :class="isDarkMode
              ? 'bg-neutral-800 border border-transparent text-gray-100 focus:ring-amber-500'
              : 'bg-gray-50 border border-transparent text-gray-900 focus:ring-amber-600'">
            <option value="">All</option>
            <option value="1">Yes</option>
            <option value="0">No</option>
          </select>
        </div>

        <!-- Priority -->
        <div class="flex flex-col">
          <label class="text-sm font-medium mb-1" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            Priority
          </label>
          <select v-model="filters.priority"
            class="rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:border-transparent" :class="isDarkMode
              ? 'bg-neutral-800 border border-transparent text-gray-100 focus:ring-amber-500'
              : 'bg-gray-50 border border-transparent text-gray-900 focus:ring-amber-600'">
            <option value="">All</option>
            <option value="1">Low</option>
            <option value="2">Medium</option>
            <option value="3">High</option>
          </select>
        </div>

        <!-- Status -->
        <div class="flex flex-col">
          <label class="text-sm font-medium mb-1" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
            Status
          </label>
          <select v-model="filters.status"
            class="rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:border-transparent" :class="isDarkMode
              ? 'bg-neutral-800 border border-transparent text-gray-100 focus:ring-amber-500'
              : 'bg-gray-50 border border-transparent text-gray-900 focus:ring-amber-600'">
            <option value="">All</option>
            <option value="1">Open</option>
            <option value="2">Closed</option>
          </select>
        </div>

        <!-- Category -->
        <div class="flex flex-col">
          <BaseSelect v-model="filters.case_category_id" label="Category" placeholder="Select category"
            :category-id="362557" />
        </div>

        <!-- Justice System State -->
        <div class="flex flex-col">
          <BaseSelect v-model="filters.justice_id" label="Justice State" placeholder="Select state"
            :category-id="236687" />
        </div>

        <!-- General Assessment -->
        <div class="flex flex-col">
          <BaseSelect v-model="filters.assessment_id" label="Assessment" placeholder="Select assessment"
            :category-id="236694" />
        </div>
      </div>
    </Transition>

    <!-- Action Buttons -->
    <div class="flex gap-2 mt-6">
      <button @click="applyFilters"
        class="text-white px-6 py-2 rounded-lg transition-all duration-200 font-semibold shadow-lg flex items-center gap-2 active:scale-95 active:shadow-md"
        :class="isDarkMode
          ? 'bg-amber-600 hover:bg-amber-700'
          : 'bg-amber-700 hover:bg-amber-800'">
        <i-mdi-filter class="w-4 h-4" />
        Apply Filters
      </button>

      <button @click="resetFilters"
        class="px-6 py-2 rounded-lg transition-all duration-200 font-semibold border flex items-center gap-2 active:scale-95"
        :class="isDarkMode
          ? 'bg-neutral-800 text-gray-300 border-transparent hover:bg-neutral-700'
          : 'bg-gray-200 text-gray-700 border-transparent hover:bg-gray-300'">
        <i-mdi-refresh class="w-4 h-4" />
        Reset
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, inject } from 'vue'

  const emit = defineEmits(['update:filters'])

  // Inject theme
  const isDarkMode = inject('isDarkMode')
  const showAdvanced = ref(false)

  const filters = reactive({
    q: '',
    caseId: '',
    dateFrom: '',
    dateTo: '',
    createdBy: '',
    source: '',
    dept: '',
    gbv_related: '',
    priority: '',
    status: '',
    case_category_id: '',
    justice_id: '',
    assessment_id: ''
  })

  // Helper to get unix timestamp from date string
  function getUnixTimestamp(dateString) {
    if (!dateString) return null
    const date = new Date(dateString)
    date.setHours(0, 0, 0, 0)
    return Math.floor(date.getTime() / 1000)
  }

  // Helper to get end of day timestamp
  function getEndOfDayTimestamp(dateString) {
    if (!dateString) return null
    const date = new Date(dateString)
    date.setHours(23, 59, 59, 999)
    return Math.floor(date.getTime() / 1000)
  }

  function applyFilters() {
    const params = {}

    // Global Search
    if (filters.q) {
      params.q = filters.q.trim()
    }

    // Case ID - using id field
    if (filters.caseId) {
      params.id = filters.caseId.trim()
    }

    // Date range - using created_on field
    if (filters.dateFrom || filters.dateTo) {
      const fromTs = filters.dateFrom ? getUnixTimestamp(filters.dateFrom) : 0
      const toTs = filters.dateTo ? getEndOfDayTimestamp(filters.dateTo) : Math.floor(Date.now() / 1000)
      params.created_on = `${fromTs};${toTs}`
    }

    // Created By - using created_by field
    if (filters.createdBy) {
      params.created_by = filters.createdBy.trim()
    }

    // Source - using src field
    if (filters.source) {
      params.src = filters.source
    }

    // Dept
    if (filters.dept) {
      params.dept = filters.dept
    }

    // GBV
    if (filters.gbv_related) {
      params.gbv_related = filters.gbv_related
    }

    // Priority - using priority field
    if (filters.priority) {
      params.priority = filters.priority
    }

    // Status - using status field
    if (filters.status) {
      params.status = filters.status
    }

    // Category
    if (filters.case_category_id) {
      params.case_category_id = filters.case_category_id
    }

    // Justice
    if (filters.justice_id) {
      params.justice_id = filters.justice_id
    }

    // Assessment
    if (filters.assessment_id) {
      params.assessment_id = filters.assessment_id
    }

    emit('update:filters', params)
  }

  function resetFilters() {
    Object.keys(filters).forEach(key => {
      filters[key] = ''
    })

    emit('update:filters', {})
  }
</script>

<style scoped>

  .fade-enter-active,
  .fade-leave-active {
    transition: all 0.3s ease;
  }

  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
    transform: translateY(-10px);
  }
</style>
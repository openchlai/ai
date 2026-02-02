<template>
  <div 
    class="space-y-6"
  >

    <!-- Filters -->
    <CasesFilter @update:filters="applyFilters" />
    
    <!-- Loading State -->
    <div 
      v-if="casesStore.loading" 
      class="flex justify-center items-center py-12 rounded-lg shadow-xl border"
      :class="isDarkMode 
        ? 'bg-black border-transparent' 
        : 'bg-white border-transparent'"
    >
      <div 
        :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
      >
        Loading cases...
      </div>
    </div>

    <!-- Content when loaded -->
    <div v-else>
      <!-- View Toggle Buttons and Stats Row -->
      <div class="flex justify-between items-center mb-6">
        <!-- Total Count with Pagination Info -->
        <div
          class="flex items-center gap-2"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          <i-mdi-folder-outline
            class="w-5 h-5"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-600'"
          />
          <span class="text-sm">
            Showing {{ casesStore.paginationInfo.rangeStart }} - {{ casesStore.paginationInfo.rangeEnd }} of
          </span>
          <span
            class="text-lg font-bold"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-600'"
          >
            {{ casesStore.paginationInfo.total }}
          </span>
          <span class="text-sm">cases</span>
        </div>

        <!-- View Toggle Buttons -->
        <div class="flex gap-3">
          <button
            @click="currentView = 'timeline'"
            :class="getViewButtonClass(currentView === 'timeline')"
          >
            <i-mdi-timeline-text-outline class="w-5 h-5" />
            Timeline
          </button>

          <button
            @click="currentView = 'table'"
            :class="getViewButtonClass(currentView === 'table')"
          >
            <i-mdi-table class="w-5 h-5" />
            Table
          </button>

          <button
            @click="createCase"
            class="px-5 py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 text-sm bg-green-600 text-white hover:bg-green-700 shadow-lg active:scale-95"
          >
            <i-mdi-plus-circle class="w-5 h-5" />
            Create Case
          </button>

          <button
            @click="refreshCases"
            :disabled="casesStore.loading"
            class="px-5 py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 text-sm border disabled:opacity-50 disabled:cursor-not-allowed"
            :class="isDarkMode 
              ? 'bg-black text-gray-300 border-transparent hover:border-green-500 hover:text-green-400' 
              : 'bg-white text-gray-700 border-transparent hover:border-green-600 hover:text-green-700'"
          >
            <i-mdi-refresh class="w-5 h-5" />
            Refresh
          </button>
        </div>
      </div>

      <!-- Timeline view -->
      <div v-if="currentView === 'timeline'">
        <Timeline
          :cases="casesStore.cases"
          :cases_k="casesStore.cases_k"
          @select-case="handleCaseSelect"
        />
      </div>

      <!-- Table view -->
      <div v-if="currentView === 'table'">
        <Table
          :cases="casesStore.cases"
          :cases_k="casesStore.cases_k"
          @select-case="handleCaseSelect"
        />
      </div>

      <!-- Pagination Controls -->
      <Pagination
        :paginationInfo="casesStore.paginationInfo"
        :hasNextPage="casesStore.hasNextPage"
        :hasPrevPage="casesStore.hasPrevPage"
        :loading="casesStore.loading"
        :pageSize="selectedPageSize"
        @prev="goToPrevPage"
        @next="goToNextPage"
        @goToPage="goToPage"
        @changePageSize="changePageSize"
      />
    </div>

    <!-- Case Details Panel -->
    <CaseDetailsPanel
      :show="showDetailsPanel"
      :caseItem="selectedCaseData?.caseItem"
      :cases_k="selectedCaseData?.cases_k || casesStore.cases_k"
      :loading="loadingCaseDetails"
      @close="closeDetailsPanel"
      @update="handleUpdateCase"
      @edit="handleEditCase"
      @history="handleCaseHistory"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, inject, watch } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { useCaseStore } from '@/stores/cases'
import { useAuthStore } from '@/stores/auth'
import { useSearchStore } from '@/stores/search'
import Table from '@/components/cases/Table.vue'
import Timeline from '@/components/cases/Timeline.vue'
import CasesFilter from '@/components/cases/CasesFilter.vue'
import CaseDetailsPanel from '@/components/cases/CaseDetailsPanel.vue'
import Pagination from '@/components/base/Pagination.vue'

const router = useRouter()
const casesStore = useCaseStore()
const authStore = useAuthStore()
const searchStore = useSearchStore()
const currentView = ref('timeline')
const currentFilters = ref({})
const selectedPageSize = ref(20)

// Debounce handle for global search
let searchDebounce = null

// Watch for global search query changes
watch(() => searchStore.query, (newQuery) => {
  clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => {
    // Merge search query with existing filters
    const searchParams = { ...currentFilters.value }
    if (newQuery) {
      searchParams.q = newQuery
    } else {
      delete searchParams.q
    }
    applyFilters(searchParams)
  }, 500)
})

// ✅ FIXED: Case details panel state
const showDetailsPanel = ref(false)
const selectedCase = ref(null) // For backward compatibility
const selectedCaseData = ref(null) // Full case data with mapping
const loadingCaseDetails = ref(false)

// Inject theme
const isDarkMode = inject('isDarkMode')

// Helper function to get value from case using cases_k structure
const getCaseValue = (caseItem, key) => {
  if (!caseItem || !casesStore.cases_k?.[key]) return null
  return caseItem[casesStore.cases_k[key][0]]
}

// Generate session tracking IDs
const generateSessionIds = () => {
  const timestamp = Date.now()
  const userId = authStore.user?.id || '100'
  const srcUid = `edit-${userId}-${timestamp}`
  
  return {
    src_uid: srcUid,
    src_uid2: `${srcUid}-1`,
    src_callid: `${srcUid}-1`,
    src_usr: userId
  }
}

// Dynamic button class for view toggle
const getViewButtonClass = (isActive) => {
  const baseClasses = 'px-5 py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 text-sm'
  
  if (isActive) {
    return isDarkMode.value
      ? `${baseClasses} bg-amber-600 text-white shadow-lg shadow-amber-900/50`
      : `${baseClasses} bg-amber-700 text-white shadow-lg shadow-amber-900/30`
  } else {
    return isDarkMode.value
      ? `${baseClasses} bg-black text-gray-300 border border-transparent hover:border-amber-600 hover:text-amber-500`
      : `${baseClasses} bg-white text-gray-700 border border-transparent hover:border-amber-600 hover:text-amber-700`
  }
}

// Fetch cases on mount
onMounted(async () => {
  try {
    console.log('Fetching cases...')
    await casesStore.listCases({ _o: 0, _c: selectedPageSize.value })
    console.log('Cases fetched:', casesStore.cases)
    console.log('Pagination info:', casesStore.paginationInfo)
  } catch (err) {
    console.error('Failed to fetch cases:', err)
    toast.error('Failed to load cases')
  }
})

// Apply filters and fetch cases (resets to first page)
async function applyFilters(filters) {
  currentFilters.value = filters
  try {
    console.log('Applying filters:', filters)
    casesStore.resetPagination()
    await casesStore.listCases({ ...filters, _o: 0, _c: selectedPageSize.value })
    
    // Auto-select if a single record is found via direct search
    if (filters.q && casesStore.cases.length === 1) {
      const caseItem = casesStore.cases[0]
      const idIndex = casesStore.cases_k?.id?.[0]
      if (idIndex !== undefined) {
        handleCaseSelect(caseItem[idIndex])
        toast.success(`Found and opened case: #${caseItem[idIndex]}`)
      }
    }
  } catch (err) {
    console.error('Error fetching filtered cases:', err)
    toast.error('Failed to apply filters')
  }
}

// Refresh cases with current filters (maintains current page)
async function refreshCases() {
  try {
    console.log('Refreshing cases...')
    await casesStore.listCases({
      ...currentFilters.value,
      _o: casesStore.pagination.offset,
      _c: casesStore.pagination.limit
    })
    console.log('Cases refreshed')
    toast.success('Cases refreshed successfully!')
  } catch (err) {
    console.error('Error refreshing cases:', err)
    toast.error('Failed to refresh cases')
  }
}

// Pagination handlers
async function goToNextPage() {
  try {
    await casesStore.nextPage(currentFilters.value)
  } catch (err) {
    console.error('Error going to next page:', err)
    toast.error('Failed to load next page.')
  }
}

async function goToPrevPage() {
  try {
    await casesStore.prevPage(currentFilters.value)
  } catch (err) {
    console.error('Error going to previous page:', err)
    toast.error('Failed to load previous page.')
  }
}

async function goToPage(page) {
  if (page === '...') return
  try {
    await casesStore.goToPage(page, currentFilters.value)
  } catch (err) {
    console.error('Error going to page:', err)
    toast.error('Failed to load page.')
  }
}

async function changePageSize(size) {
  selectedPageSize.value = size
  try {
    await casesStore.setPageSize(size, currentFilters.value)
  } catch (err) {
    console.error('Error changing page size:', err)
    toast.error('Failed to change page size.')
  }
}

// Navigate to Case Creation page
function createCase() {
  router.push({ name: 'CaseCreation' })
}

// ✅ FIXED: Handle case selection with API fetch
async function handleCaseSelect(caseId) {
  console.log('📥 Cases.vue received case ID:', caseId)
  
  if (!caseId) {
    console.error('❌ No case ID provided')
    return
  }
  
  try {
    loadingCaseDetails.value = true
    showDetailsPanel.value = true // Show panel immediately with loading state
    
    console.log('🔄 Fetching case details for ID:', caseId)
    
    // Fetch full case details from API
    const response = await casesStore.viewCase(caseId)
    
    console.log('📦 Full API response:', response)
    console.log('📋 Cases array:', response?.cases)
    console.log('🗺️ Cases_k mapping:', response?.cases_k)
    
    // Store the fetched case data locally
    if (response?.cases?.[0]) {
      selectedCaseData.value = {
        caseItem: response.cases[0],
        cases_k: response.cases_k
      }
      selectedCase.value = response.cases[0] // For backward compatibility
      
      console.log('✅ Selected case data set:', selectedCaseData.value)
    } else {
      console.error('❌ No case data in response')
      throw new Error('No case data returned')
    }
    
  } catch (error) {
    console.error('💥 Error fetching case details:', error)
    toast.error('Failed to load case details', {
      description: error.message
    })
    showDetailsPanel.value = false
  } finally {
    loadingCaseDetails.value = false
  }
}

// Close details panel
function closeDetailsPanel() {
  showDetailsPanel.value = false
  selectedCase.value = null
  selectedCaseData.value = null
}

// Handle update case
async function handleUpdateCase(payload) {
  const { caseItem, formData } = payload
  const caseId = selectedCaseData.value?.caseItem[selectedCaseData.value.cases_k.id[0]]
  
  console.log('Updating case:', caseId, formData)
  
  try {
    // Generate session tracking IDs
    const sessionIds = generateSessionIds()
    
    // Helper to get case value
    const getVal = (key) => {
      if (!selectedCaseData.value?.caseItem || !selectedCaseData.value?.cases_k?.[key]) return ''
      return selectedCaseData.value.caseItem[selectedCaseData.value.cases_k[key][0]] || ''
    }
    
    // Build complete update payload matching the API structure
    const updatePayload = {
      '.id': caseId,
      
      // User-edited fields from form
      'plan': formData.plan,
      'priority': formData.priority,
      'status': formData.status,
      'justice_id': formData.justice_id || '',
      'assessment_id': formData.assessment_id || '',
      'escalated_to_id': formData.escalated_to_id || '',
      'disposition_id': formData.disposition_id || '',
      
      // Preserve existing case data
      'case_category_id': getVal('case_category_id'),
      'gbv_related': getVal('gbv_related'),
      'reporter_id': getVal('reporter_id'),
      'narrative': getVal('narrative'),
      'dept': getVal('dept') || '0',
      
      // Session tracking - auto-generated
      'src': 'edit',
      'src_uid': sessionIds.src_uid,
      'src_uid2': sessionIds.src_uid2,
      'src_callid': sessionIds.src_callid,
      'src_usr': sessionIds.src_usr,
      'src_vector': '2',
      'src_address': '',
      'src_ts': '',
      
      // Default/empty values
      'activity_ca_id': '',
      'activity_id': '-1',
      'contact_uuid_id': '-1',
      'knowabout116_id': '',
      
      // Empty arrays
      'attachments_case': [],
      'clients_case': [],
      'perpetrators_case': [],
      'services': []
    }
    
    console.log('Update payload:', updatePayload)
    
    // Call the store method to update the case
    await casesStore.updateCase(caseId, updatePayload)
    
    // Show success message
    toast.success('Case updated successfully!')
    
    // Refresh the case details
    await handleCaseSelect(caseId)
    
    // Refresh the cases list
    await refreshCases()
    
  } catch (err) {
    console.error('Error updating case:', err)
    toast.error(err.response?.data?.message || 'Failed to update case')
  }
}

// Handle edit case
async function handleEditCase(payload) {
  const { caseItem, formData } = payload
  const caseId = selectedCaseData.value?.caseItem[selectedCaseData.value.cases_k.id[0]]
  
  console.log('Editing case:', caseId, formData)
  
  try {
    // TODO: Build edit payload when EditCaseForm is complete
    toast.info('Edit functionality coming soon!')
  } catch (err) {
    console.error('Error editing case:', err)
    toast.error('Failed to save changes')
  }
}

// Handle case history
function handleCaseHistory(caseItem) {
  const caseId = selectedCaseData.value?.caseItem[selectedCaseData.value.cases_k.id[0]]
  console.log('Viewing history for case:', caseId)
}
</script>
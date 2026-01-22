<template>
  <!-- Overlay -->
  <div 
    v-if="show" 
    class="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 transition-opacity duration-300"
    @click="handleClose"
  ></div>

  <!-- Sliding Panel -->
  <div 
    v-if="show"
    class="fixed top-0 right-0 h-full shadow-2xl z-50 transform transition-all duration-300 ease-out overflow-hidden"
    :class="[
      panelWidthClass,
      isDarkMode ? 'bg-gray-900 border-l border-transparent' : 'bg-white border-l border-transparent'
    ]"
    @click.stop
  >
    <!-- Loading State -->
    <div 
      v-if="loading"
      class="h-full flex flex-col items-center justify-center gap-4"
    >
      <div 
        class="w-12 h-12 border-4 rounded-full animate-spin"
        :class="isDarkMode 
          ? 'border-transparent border-t-blue-500' 
          : 'border-transparent border-t-amber-700'"
      ></div>
      <p 
        class="text-sm font-medium"
        :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
      >
        Loading case details...
      </p>
    </div>

    <!-- Content (when loaded) -->
    <div v-else-if="caseItem" class="h-full flex flex-col">
      <!-- Header with breadcrumb -->
      <div 
        class="flex items-center justify-between px-6 py-4 border-b"
        :class="isDarkMode 
          ? 'bg-gray-800/50 border-transparent' 
          : 'bg-gray-50 border-transparent'"
      >
        <!-- Breadcrumb -->
        <div class="flex items-center gap-2 text-sm">
          <button 
            v-if="currentView !== 'details'"
            @click="currentView = 'details'"
            class="transition-colors"
            :class="isDarkMode 
              ? 'text-gray-400 hover:text-gray-200' 
              : 'text-gray-600 hover:text-gray-900'"
          >
            Case #{{ getCaseValue('id') }}
          </button>
          <span 
            v-else
            class="font-semibold"
            :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'"
          >
            Case #{{ getCaseValue('id') }}
          </span>
          
          <span 
            v-if="currentView !== 'details'"
            :class="isDarkMode ? 'text-gray-600' : 'text-gray-400'"
          >
            /
          </span>
          
          <span 
            v-if="currentView === 'update'"
            class="font-semibold"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
          >
            Update Case
          </span>
          <span 
            v-if="currentView === 'edit'"
            class="font-semibold"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
          >
            Edit Case
          </span>
          <span 
            v-if="currentView === 'history'"
            class="font-semibold"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
          >
            Case History
          </span>
        </div>

        <!-- Close button -->
        <button
          @click="handleClose"
          class="p-2 rounded-lg transition-colors"
          :class="isDarkMode 
            ? 'hover:bg-gray-700 text-gray-400 hover:text-gray-200' 
            : 'hover:bg-gray-100 text-gray-600 hover:text-gray-900'"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>

      <!-- Scrollable content area -->
      <div class="flex-1 overflow-y-auto">
        <!-- Details View -->
        <div v-if="currentView === 'details'" class="p-6 space-y-6">
          <!-- Status Cards -->
          <div class="grid grid-cols-2 gap-4">
            <!-- Priority Card -->
            <div 
              class="p-4 rounded-lg border"
              :class="getPriorityCardClass(getCaseValue('priority'))"
            >
              <div 
                class="text-xs font-semibold uppercase mb-1"
                :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
              >
                Priority
              </div>
              <div class="text-2xl font-bold">
                {{ formatPriority(getCaseValue('priority')) }}
              </div>
            </div>

            <!-- Status Card -->
            <div 
              class="p-4 rounded-lg border"
              :class="getStatusCardClass(getCaseValue('status'))"
            >
              <div 
                class="text-xs font-semibold uppercase mb-1"
                :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
              >
                Status
              </div>
              <div class="text-2xl font-bold">
                {{ formatStatus(getCaseValue('status')) }}
              </div>
            </div>
          </div>

          <!-- Case Information -->
          <div 
            class="border rounded-lg p-5"
            :class="isDarkMode 
              ? 'bg-gray-800 border-transparent' 
              : 'bg-white border-transparent'"
          >
            <h3 
              class="text-lg font-bold mb-4"
              :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
            >
              Case Information
            </h3>
            
            <div class="space-y-3">
              <div class="grid grid-cols-2 gap-4">
                <div>
                  <div 
                    class="text-xs font-semibold uppercase mb-1"
                    :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
                  >
                    Case ID
                  </div>
                  <div 
                    class="text-sm font-medium"
                    :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'"
                  >
                    {{ getCaseValue('id') || 'N/A' }}
                  </div>
                </div>

                <div>
                  <div 
                    class="text-xs font-semibold uppercase mb-1"
                    :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
                  >
                    Created On
                  </div>
                  <div 
                    class="text-sm font-medium"
                    :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'"
                  >
                    {{ formatDate(getCaseValue('dt')) }}
                  </div>
                </div>

                <div>
                  <div 
                    class="text-xs font-semibold uppercase mb-1"
                    :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
                  >
                    Created By
                  </div>
                  <div 
                    class="text-sm font-medium"
                    :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'"
                  >
                    {{ getCaseValue('created_by') || 'N/A' }}
                  </div>
                </div>

                <div>
                  <div 
                    class="text-xs font-semibold uppercase mb-1"
                    :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
                  >
                    Source
                  </div>
                  <div 
                    class="text-sm font-medium"
                    :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'"
                  >
                    {{ getCaseValue('src') || 'N/A' }}
                  </div>
                </div>
              </div>

              <!-- Narrative -->
              <div class="pt-3 border-t" :class="isDarkMode ? 'border-transparent' : 'border-transparent'">
                <div 
                  class="text-xs font-semibold uppercase mb-2"
                  :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
                >
                  Narrative
                </div>
                <div 
                  class="text-sm leading-relaxed whitespace-pre-wrap"
                  :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                >
                  {{ getCaseValue('narrative') || 'No narrative provided' }}
                </div>
              </div>

              <!-- Plan -->
              <div class="pt-3 border-t" :class="isDarkMode ? 'border-transparent' : 'border-transparent'">
                <div 
                  class="text-xs font-semibold uppercase mb-2"
                  :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
                >
                  Case Plan
                </div>
                <div 
                  class="text-sm leading-relaxed whitespace-pre-wrap"
                  :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
                >
                  {{ getCaseValue('plan') || 'No plan provided' }}
                </div>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="grid grid-cols-3 gap-3">
            <button
              @click="currentView = 'update'"
              class="px-4 py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 text-white"
              :class="isDarkMode 
                ? 'bg-amber-600 hover:bg-amber-700' 
                : 'bg-amber-700 hover:bg-amber-800'"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
              Update
            </button>

            <button
              @click="currentView = 'edit'"
              class="px-4 py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 border"
              :class="isDarkMode 
                ? 'bg-gray-800 text-gray-300 border-transparent hover:border-amber-500 hover:text-amber-500' 
                : 'bg-white text-gray-700 border-transparent hover:border-amber-600 hover:text-amber-700'"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              Edit
            </button>

            <button
              @click="currentView = 'history'"
              class="px-4 py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 border"
              :class="isDarkMode 
                ? 'bg-gray-800 text-gray-300 border-transparent hover:border-purple-500 hover:text-purple-400' 
                : 'bg-white text-gray-700 border-transparent hover:border-purple-600 hover:text-purple-700'"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              History
            </button>
          </div>
        </div>

        <!-- Update View -->
        <UpdateCaseForm
          v-if="currentView === 'update'"
          :caseItem="caseItem"
          :cases_k="cases_k"
          :isSubmitting="isSubmitting"
          @submit="handleUpdate"
          @cancel="currentView = 'details'"
        />

        <!-- Edit View -->
        <EditCaseForm
          v-if="currentView === 'edit'"
          :caseItem="caseItem"
          :cases_k="cases_k"
          :isSubmitting="isSubmitting"
          @submit="handleEdit"
          @cancel="currentView = 'details'"
        />

        <!-- History View -->
        <CaseHistoryView
          v-if="currentView === 'history'"
          :caseItem="caseItem"
          :cases_k="cases_k"
        />
      </div>
    </div>

    <!-- Error State -->
    <div 
      v-else
      class="h-full flex flex-col items-center justify-center gap-4 p-6"
    >
      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" class="text-red-500">
        <circle cx="12" cy="12" r="10"/>
        <line x1="15" y1="9" x2="9" y2="15"/>
        <line x1="9" y1="9" x2="15" y2="15"/>
      </svg>
      <p 
        class="text-center font-medium"
        :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
      >
        Failed to load case details
      </p>
      <button
        @click="handleClose"
        class="px-4 py-2 rounded-lg transition-colors"
        :class="isDarkMode 
          ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' 
          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'"
      >
        Close
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, inject } from 'vue'
import UpdateCaseForm from './UpdateCaseForm.vue'
import EditCaseForm from './EditCaseForm.vue'
import CaseHistoryView from './CaseHistoryView.vue'

const props = defineProps({
  show: Boolean,
  caseItem: Array, // Changed from Object to Array
  cases_k: Object,
  loading: Boolean
})

const emit = defineEmits(['close', 'update', 'edit', 'history'])

const isDarkMode = inject('isDarkMode')
const currentView = ref('details')
const isSubmitting = ref(false)

// Reset view when panel opens/closes
watch(() => props.show, (newVal) => {
  if (newVal) {
    currentView.value = 'details'
  }
})

// Dynamic panel width based on current view
const panelWidthClass = computed(() => {
  if (currentView.value === 'details') {
    return 'w-full md:w-2/3 lg:w-1/2'
  }
  return 'w-full md:w-3/4 lg:w-2/3'
})

// Helper to get case values
const getCaseValue = (key) => {
  if (!props.caseItem || !props.cases_k?.[key]) return null
  return props.caseItem[props.cases_k[key][0]]
}

// Format date
const formatDate = (timestamp) => {
  if (!timestamp) return 'N/A'
  const value = timestamp < 10000000000 ? timestamp * 1000 : timestamp * 3600 * 1000
  return new Date(value).toLocaleString()
}

// Format priority
const formatPriority = (priority) => {
  switch (String(priority)) {
    case '3': return 'High'
    case '2': return 'Medium'
    case '1': return 'Low'
    default: return 'Unknown'
  }
}

// Format status
const formatStatus = (status) => {
  switch (String(status)) {
    case '1': return 'Open'
    case '2': return 'Closed'
    default: return 'Unknown'
  }
}

// Priority card styling
const getPriorityCardClass = (priority) => {
  switch (String(priority)) {
    case '3': // High
      return isDarkMode.value
        ? 'bg-red-600/20 border-red-600/30 text-red-400'
        : 'bg-red-50 border-red-300 text-red-700'
    case '2': // Medium
      return isDarkMode.value
        ? 'bg-amber-600/20 border-amber-600/30 text-amber-400'
        : 'bg-amber-50 border-amber-300 text-amber-700'
    case '1': // Low
      return isDarkMode.value
        ? 'bg-green-600/20 border-green-600/30 text-green-400'
        : 'bg-green-50 border-green-300 text-green-700'
    default:
      return isDarkMode.value
        ? 'bg-gray-700 border-transparent text-gray-400'
        : 'bg-gray-100 border-transparent text-gray-600'
  }
}

// Status card styling
const getStatusCardClass = (status) => {
  switch (String(status)) {
    case '1': // Open
      return isDarkMode.value
        ? 'bg-amber-600/20 border-amber-600/30 text-amber-400'
        : 'bg-amber-50 border-amber-300 text-amber-700'
    case '2': // Closed
      return isDarkMode.value
        ? 'bg-green-600/20 border-green-600/30 text-green-400'
        : 'bg-green-50 border-green-300 text-green-700'
    default:
      return isDarkMode.value
        ? 'bg-gray-700 border-transparent text-gray-400'
        : 'bg-gray-100 border-transparent text-gray-600'
  }
}

// Handlers
const handleClose = () => {
  emit('close')
}

const handleUpdate = (formData) => {
  emit('update', { caseItem: props.caseItem, formData })
}

const handleEdit = (formData) => {
  emit('edit', { caseItem: props.caseItem, formData })
}
</script>
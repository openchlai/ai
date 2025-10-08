<template>
  <!-- Step 1: Reporter Selection -->
  <div v-show="currentStep === 1" class="step-content">
    <form class="case-form" @submit.prevent="handleFormSubmit">
      <div class="form-section">
        <div class="section-title">Select Reporter</div>
        <p class="section-description">
          Choose an existing contact or create a new reporter for this case.
        </p>

        <!-- Search Section -->
        <div class="search-section">
          <div class="search-row">
            <div class="search-box">
              <!-- Search Icon -->
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                <circle cx="11" cy="11" r="8" stroke="currentColor" stroke-width="2"/>
                <path d="m21 21-4.35-4.35" stroke="currentColor" stroke-width="2"/>
              </svg>

              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search by name or phone..."
                class="search-input"
                @input="handleSearchInput"
              />
            </div>
            <button
              type="button"
              class="btn btn--primary new-reporter-btn"
              @click="createNewReporter"
            >
              + New Reporter
            </button>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="isLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <span>Searching reporters...</span>
        </div>

        <!-- Search Results -->
        <div class="contacts-list" v-else-if="shouldShowResults && filteredContacts.length">
          <div class="results-header">
            <span>{{ filteredContacts.length }} reporter(s) found</span>
          </div>
          <div
            v-for="contact in filteredContacts"
            :key="getContactId(contact)"
            class="contact-item"
            :class="{ selected: isSelected(contact) }"
            @click="selectExistingReporter(contact)"
          >
            <!-- Avatar -->
            <div class="contact-avatar">
              <span>{{ getInitials(getValue(contact, 'fullname') || 'NA') }}</span>
            </div>

            <!-- Details -->
            <div class="contact-details">
              <div class="contact-main-info">
                <div class="contact-name">
                  {{ getValue(contact, 'fullname') || "Unnamed Reporter" }}
                </div>
                <div class="contact-phone">
                  {{ getValue(contact, 'phone') || 'No phone' }}
                </div>
              </div>
              <div class="contact-meta-info">
                <div class="contact-tags">
                  <span v-if="getValue(contact, 'age')" class="contact-tag">{{ getValue(contact, 'age') }}y</span>
                  <span v-if="getValue(contact, 'sex')" class="contact-tag">{{ getValue(contact, 'sex') }}</span>
                  <span v-if="getValue(contact, 'location')" class="contact-tag location">📍 {{ getValue(contact, 'location') }}</span>
                </div>
              </div>
            </div>

            <!-- Selection Indicator -->
            <div class="contact-select-indicator">
              <svg v-if="isSelected(contact)" width="20" height="20" viewBox="0 0 24 24" fill="none" class="selected-icon">
                <circle cx="12" cy="12" r="10" fill="var(--color-primary)" stroke="var(--color-primary)" stroke-width="2"/>
                <path d="M8 12l2 2 4-4" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none">
                <polyline points="9,18 15,12 9,6" stroke="currentColor" stroke-width="2"/>
              </svg>
            </div>
          </div>
        </div>

        <!-- No Results -->
        <div v-else-if="shouldShowResults && !filteredContacts.length" class="search-empty">
          <div class="empty-icon">🔍</div>
          <div class="empty-text">No reporters found</div>
          <div class="empty-subtext">Try searching with a different name or phone number</div>
        </div>

        <!-- Search Prompt -->
        <div v-else-if="!searchQuery.trim()" class="search-prompt">
          <div class="prompt-icon">👥</div>
          <div class="prompt-text">Start typing to search for existing reporters</div>
          <div class="prompt-subtext">Or click "New Reporter" to create a new one</div>
        </div>

        <!-- Selected Reporter Summary -->
        <div v-if="selectedReporter" class="selected-reporter-summary">
          <div class="summary-header">Selected Reporter:</div>
          <div class="summary-card">
            <div class="summary-avatar">
              <span>{{ getInitials(getValue(selectedReporter, 'fullname') || 'NR') }}</span>
            </div>
            <div class="summary-info">
              <div class="summary-name">{{ getValue(selectedReporter, 'fullname') || 'New Reporter' }}</div>
              <div class="summary-details">
                {{ getValue(selectedReporter, 'phone') || 'No phone' }} • 
                {{ getValue(selectedReporter, 'age') || 'Age unknown' }} • 
                {{ getValue(selectedReporter, 'sex') || 'Gender unknown' }}
              </div>
            </div>
            <button type="button" @click="clearSelection" class="clear-selection-btn">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2"/>
                <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <div class="form-actions">
        <button type="button" class="btn btn-cancel" @click="cancelForm">Cancel</button>
        <div>
          <BaseButton type="button" variant="secondary" @click="handleSkipStep">Skip</BaseButton>
          <BaseButton type="submit" :disabled="!selectedReporter && !isNewReporter">
            {{ selectedReporter ? 'Continue with Selected Reporter' : (isNewReporter ? 'Create New Reporter' : 'Select a Reporter') }}
          </BaseButton>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from "vue"
import { useReporterStore } from "@/stores/reporters"
import BaseButton from "@/components/base/BaseButton.vue"

const props = defineProps({
  currentStep: { type: Number, required: true },
  searchQuery: { type: String, default: '' },
  filteredContacts: { type: Array, default: () => [] },
  selectedReporter: { type: Object, default: null }
})

const emit = defineEmits([
  "validate-and-proceed", 
  "skip-step", 
  "cancel-form",
  "search-change",
  "select-reporter",
  "create-new-reporter"
])

const reportersStore = useReporterStore()

// Local state
const searchQuery = ref(props.searchQuery || "")
const debouncedQuery = ref("")
const selectedReporter = ref(props.selectedReporter)
const isLoading = ref(false)
const isNewReporter = ref(false)

// Fetch reporters on mount
onMounted(async () => {
  console.log('Step1: Component mounted, fetching reporters...')
  try {
    isLoading.value = true
    if (!reportersStore.reporters.length) {
      console.log('Step1: No reporters in store, calling listReporters()')
      await reportersStore.listReporters()
    }
    console.log('Step1: Reporters loaded:', reportersStore.reporters.length)
  } catch (error) {
    console.error('Step1: Error loading reporters:', error)
  } finally {
    isLoading.value = false
  }
})

// Debounce search input
let debounceTimeout
watch(searchQuery, (newVal) => {
  clearTimeout(debounceTimeout)
  debounceTimeout = setTimeout(() => {
    debouncedQuery.value = newVal.trim()
    console.log('Step1: Search query updated:', debouncedQuery.value)
    // Emit search change to parent
    emit('search-change', newVal.trim())
  }, 300)
})

onBeforeUnmount(() => clearTimeout(debounceTimeout))

// Watch for changes from parent (if parent controls the search)
watch(() => props.searchQuery, (newQuery) => {
  if (newQuery !== searchQuery.value) {
    searchQuery.value = newQuery
  }
})

watch(() => props.selectedReporter, (newReporter) => {
  selectedReporter.value = newReporter
})

// Helper functions to safely access reporter data using reporters_k mapping
const getFieldIndex = (fieldName) => {
  // reporters_k contains mappings like: { "contact_fullname": [1], "contact_phone": [5], etc. }
  const mapping = reportersStore.reporters_k?.[`contact_${fieldName}`]
  if (mapping && Array.isArray(mapping) && mapping.length > 0) {
    return mapping[0] // Get the first index
  }
  
  // Fallback: try without "contact_" prefix
  const fallbackMapping = reportersStore.reporters_k?.[fieldName]
  if (fallbackMapping && Array.isArray(fallbackMapping) && fallbackMapping.length > 0) {
    return fallbackMapping[0]
  }
  
  console.warn(`Field mapping not found for: contact_${fieldName} or ${fieldName}`)
  return null
}

const getValue = (contact, fieldName) => {
  if (!contact || !Array.isArray(contact)) return ""
  
  const idx = getFieldIndex(fieldName)
  if (idx !== null && idx >= 0 && idx < contact.length) {
    return contact[idx] || ""
  }
  
  return ""
}

const getContactId = (contact) => {
  if (!contact || !Array.isArray(contact)) return Math.random().toString()
  
  // Try to get ID from common ID field names
  const idFields = ['id', '_id', 'reporter_id']
  for (const fieldName of idFields) {
    const value = getValue(contact, fieldName)
    if (value) return value.toString()
  }
  
  // Fallback: use a combination of name and phone as unique identifier
  const name = getValue(contact, 'fullname')
  const phone = getValue(contact, 'phone')
  return `${name}-${phone}`.replace(/\s+/g, '-')
}

// Computed properties
const shouldShowResults = computed(() => {
  return debouncedQuery.value.length >= 2 // Only show results for 2+ characters
})

const filteredContacts = computed(() => {
  if (!shouldShowResults.value) return []
  
  const q = debouncedQuery.value.toLowerCase()
  const contacts = reportersStore.reporters || []
  
  console.log('Step1: Filtering contacts with query:', q)
  console.log('Step1: Available contacts:', contacts.length)
  console.log('Step1: reporters_k mapping:', reportersStore.reporters_k)
  
  // Debug: show field indices
  const fullnameIndex = getFieldIndex('fullname')
  const phoneIndex = getFieldIndex('phone')
  console.log('Step1: Field indices - fullname:', fullnameIndex, 'phone:', phoneIndex)
  
  const filtered = contacts.filter((contact) => {
    if (!Array.isArray(contact)) {
      console.warn('Step1: Contact is not an array:', contact)
      return false
    }
    
    const name = getValue(contact, "fullname").toLowerCase()
    const phone = getValue(contact, "phone").toLowerCase()
    
    console.log('Step1: Checking contact:', { 
      name, 
      phone, 
      rawContact: contact,
      nameIndex: getFieldIndex('fullname'),
      phoneIndex: getFieldIndex('phone')
    })
    
    const matches = name.includes(q) || phone.includes(q)
    
    if (matches) {
      console.log('Step1: Match found:', { name, phone })
    }
    
    return matches
  })
  
  console.log('Step1: Filtered results:', filtered.length)
  return filtered.slice(0, 10) // Limit to 10 results
})

// Event handlers
const handleSearchInput = (event) => {
  searchQuery.value = event.target.value
}

const selectExistingReporter = (contact) => {
  console.log('Step1: Reporter selected:', contact)
  selectedReporter.value = contact
  isNewReporter.value = false
  emit('select-reporter', contact)
}

const createNewReporter = () => {
  console.log('Step1: Creating new reporter')
  // Clear any selected reporter
  selectedReporter.value = null
  // Set flag that we're creating a new reporter
  isNewReporter.value = true
  // Emit to parent to clear form and navigate
  emit('create-new-reporter')
  // Proceed to step 2 for new reporter creation
  emit("validate-and-proceed", null)
}

const clearSelection = () => {
  selectedReporter.value = null
  isNewReporter.value = false
  emit('select-reporter', null)
}

const isSelected = (contact) => {
  if (!selectedReporter.value || !contact) return false
  return getContactId(contact) === getContactId(selectedReporter.value)
}

// Form submission
const handleFormSubmit = () => {
  console.log('Step1: Form submitted with reporter:', selectedReporter.value)
  if (selectedReporter.value || isNewReporter.value) {
    emit("validate-and-proceed", selectedReporter.value)
  }
}

const handleSkipStep = () => {
  console.log('Step1: Step skipped')
  emit("skip-step", 1)
}

const cancelForm = () => {
  emit("cancel-form")
}

// Utility functions
const getInitials = (name) => {
  if (!name || typeof name !== 'string') return 'NA'
  return name.split(" ")
    .map((n) => n[0] || "")
    .join("")
    .toUpperCase()
    .slice(0, 2)
}
</script>

<style scoped>
.step-content {
  min-height: 400px;
}

.case-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.search-section {
  margin-bottom: 20px;
}

.search-row {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 10px 12px;
  background: var(--color-surface);
  color: var(--color-text);
  flex: 1;
  max-width: 300px;
}

.search-box:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb), 0.1);
}

.search-input {
  border: 0;
  outline: 0;
  width: 100%;
  background: transparent;
  font-size: 14px;
  color: var(--color-text);
}

.search-input::placeholder {
  color: var(--color-muted);
}

.new-reporter-btn {
  height: 42px;
  padding: 0 16px;
  white-space: nowrap;
}

/* Loading State */
.loading-state {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  text-align: center;
  color: var(--color-muted);
}

.loading-spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-border);
  border-top: 2px solid var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Results */
.results-header {
  padding: 8px 0;
  font-size: 14px;
  color: var(--color-muted);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: 12px;
}

.contacts-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 12px;
  background: var(--color-surface);
  cursor: pointer;
  transition: all 0.2s ease;
}

.contact-item:hover {
  background: var(--color-surface-muted);
  border-color: var(--color-primary);
}

.contact-item.selected {
  border-color: var(--color-primary);
  background: rgba(var(--color-primary-rgb), 0.05);
}

.contact-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  font-weight: 600;
  font-size: 14px;
}

.contact-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.contact-main-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.contact-name {
  font-weight: 600;
  font-size: 16px;
  color: var(--color-text);
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.contact-phone {
  color: var(--color-muted);
  font-size: 14px;
  line-height: 1.2;
}

.contact-meta-info {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}

.contact-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.contact-tag {
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 500;
  background: var(--color-surface-muted);
  color: var(--color-text);
  white-space: nowrap;
}

.contact-tag.location {
  background: rgba(var(--color-primary-rgb), 0.1);
  color: var(--color-primary);
  border-color: rgba(var(--color-primary-rgb), 0.2);
}

.selected-icon {
  color: var(--color-primary);
}

/* Empty States */
.search-empty, .search-prompt {
  text-align: center;
  padding: 40px 20px;
  color: var(--color-muted);
}

.empty-icon, .prompt-icon {
  font-size: 48px;
  margin-bottom: 12px;
  opacity: 0.5;
}

.empty-text, .prompt-text {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 4px;
}

.empty-subtext, .prompt-subtext {
  font-size: 14px;
  opacity: 0.7;
}

/* Selected Reporter Summary */
.selected-reporter-summary {
  margin: 20px 0;
  padding: 16px;
  background: rgba(var(--color-primary-rgb), 0.05);
  border: 1px solid rgba(var(--color-primary-rgb), 0.2);
  border-radius: 12px;
}

.summary-header {
  font-size: 14px;
  font-weight: 600;
  color: var(--color-primary);
  margin-bottom: 12px;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 12px;
}

.summary-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-primary);
  color: white;
  font-weight: 600;
  font-size: 14px;
}

.summary-info {
  flex: 1;
}

.summary-name {
  font-weight: 600;
  color: var(--color-text);
}

.summary-details {
  font-size: 14px;
  color: var(--color-muted);
  margin-top: 2px;
}

.clear-selection-btn {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  padding: 6px;
  cursor: pointer;
  color: var(--color-muted);
  transition: all 0.2s;
}

.clear-selection-btn:hover {
  background: var(--color-surface-muted);
  border-color: var(--color-danger);
  color: var(--color-danger);
}

/* Form Actions */
.form-actions {
  display: flex;
  gap: 12px;
  justify-content: space-between;
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--color-border);
}

.form-actions > div {
  display: flex;
  gap: 12px;
}

.btn-cancel {
  background: transparent;
  color: var(--color-muted);
  border: 1px solid var(--color-border);
  padding: 10px 16px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: var(--color-surface-muted);
  border-color: var(--color-danger);
  color: var(--color-danger);
}

/* Responsive */
@media (max-width: 768px) {
  .search-row {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  
  .search-box {
    max-width: none;
  }
  
  .contact-details {
    grid-template-columns: 1fr;
  }
  
  .contact-meta-info {
    justify-content: flex-start;
  }
  
  .form-actions {
    flex-direction: column;
    gap: 12px;
  }
  
  .form-actions > div {
    justify-content: center;
  }
}
</style>
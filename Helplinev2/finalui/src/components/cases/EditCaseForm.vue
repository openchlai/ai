<template>
  <div class="p-6">
    <!-- Header with Save/Cancel buttons -->
    <div 
      class="flex items-center justify-between mb-6 pb-4 border-b sticky top-0 z-10 -mx-6 px-6 -mt-6 pt-6"
      :class="isDarkMode 
        ? 'bg-gray-900 border-transparent' 
        : 'bg-white border-transparent'"
    >
      <div>
        <h2 
          class="text-xl font-bold"
          :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
        >
          Edit Case #{{ getCaseValue('id') }}
        </h2>
        <p 
          class="text-sm mt-1"
          :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
        >
          Make changes to case details, clients, perpetrators, and attachments
        </p>
      </div>
      <div class="flex gap-3">
        <button
          @click="$emit('cancel')"
          type="button"
          class="px-4 py-2 border rounded-lg transition-colors font-medium"
          :class="isDarkMode 
            ? 'bg-gray-700 text-gray-300 border-transparent hover:bg-gray-600' 
            : 'bg-white text-gray-700 border-transparent hover:bg-gray-50'"
        >
          Cancel
        </button>
        <button
          @click="handleSave"
          :disabled="isSubmitting"
          type="button"
          class="px-4 py-2 text-white rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          :class="isDarkMode 
            ? 'bg-amber-600 hover:bg-amber-700' 
            : 'bg-amber-700 hover:bg-amber-800'"
        >
          <span v-if="isSubmitting" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
          {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </div>

    <!-- Accordion Sections -->
    <div class="space-y-4">
      <!-- 1. Case Information (Always Expanded First) -->
      <AccordionSection
        title="Case Information"
        :isOpen="openSections.caseInfo"
        :badge="null"
        @toggle="toggleSection('caseInfo')"
      >
        <div class="space-y-4">
          <!-- Narrative -->
          <div>
            <label 
              class="block text-sm font-semibold mb-2"
              :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
            >
              Narrative *
            </label>
            <textarea
              v-model="formData.narrative"
              rows="6"
              class="w-full px-3 py-2 border rounded-lg text-sm transition-all focus:outline-none focus:ring-2 focus:border-transparent resize-vertical"
              :class="isDarkMode 
                ? 'bg-gray-700 border-transparent text-gray-100 placeholder-gray-500 focus:ring-amber-500' 
                : 'bg-gray-50 border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'"
              placeholder="Describe the case details..."
            ></textarea>
          </div>

          <!-- Plan -->
          <div>
            <label 
              class="block text-sm font-semibold mb-2"
              :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
            >
              Case Plan *
            </label>
            <textarea
              v-model="formData.plan"
              rows="4"
              class="w-full px-3 py-2 border rounded-lg text-sm transition-all focus:outline-none focus:ring-2 focus:border-transparent resize-vertical"
              :class="isDarkMode 
                ? 'bg-gray-700 border-transparent text-gray-100 placeholder-gray-500 focus:ring-amber-500' 
                : 'bg-gray-50 border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'"
              placeholder="Outline planned interventions..."
            ></textarea>
          </div>

          <!-- Category & GBV -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <BaseSelect
              id="case-category"
              label="Case Category *"
              v-model="formData.case_category_id"
              placeholder="Select category"
              :category-id="362557"
              @change="handleCategoryChange"
            />

            <BaseSelect
              id="gbv-related"
              label="GBV Related *"
              v-model="formData.gbv_related"
              placeholder="Select option"
              :category-id="118"
              @change="handleGBVChange"
            />
          </div>

          <!-- Priority & Status -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label 
                class="block text-sm font-semibold mb-2"
                :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
              >
                Priority *
              </label>
              <select 
                v-model="formData.priority" 
                class="w-full px-3 py-2 border rounded-lg text-sm transition-all focus:outline-none focus:ring-2 focus:border-transparent"
                :class="isDarkMode 
                  ? 'bg-gray-700 border-transparent text-gray-100 focus:ring-amber-500' 
                  : 'bg-gray-50 border-transparent text-gray-900 focus:ring-amber-600'"
              >
                <option value="">Select priority</option>
                <option value="3">High</option>
                <option value="2">Medium</option>
                <option value="1">Low</option>
              </select>
            </div>

            <div>
              <label 
                class="block text-sm font-semibold mb-2"
                :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
              >
                Status *
              </label>
              <select 
                v-model="formData.status" 
                class="w-full px-3 py-2 border rounded-lg text-sm transition-all focus:outline-none focus:ring-2 focus:border-transparent"
                :class="isDarkMode 
                  ? 'bg-gray-700 border-transparent text-gray-100 focus:ring-amber-500' 
                  : 'bg-gray-50 border-transparent text-gray-900 focus:ring-amber-600'"
              >
                <option value="">Select status</option>
                <option value="1">Open</option>
                <option value="2">Closed</option>
              </select>
            </div>
          </div>

          <!-- Justice System & Assessment -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <BaseSelect
              id="justice-system"
              label="Justice System State"
              v-model="formData.justice_id"
              placeholder="Select option"
              :category-id="236687"
              @change="handleJusticeChange"
            />

            <BaseSelect
              id="assessment"
              label="General Assessment"
              v-model="formData.assessment_id"
              placeholder="Select option"
              :category-id="236694"
              @change="handleAssessmentChange"
            />
          </div>

          <!-- Escalated To & Disposition -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label 
                class="block text-sm font-semibold mb-2"
                :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
              >
                Escalated To
              </label>
              <select 
                v-model="formData.escalated_to_id" 
                class="w-full px-3 py-2 border rounded-lg text-sm transition-all focus:outline-none focus:ring-2 focus:border-transparent"
                :class="isDarkMode 
                  ? 'bg-gray-700 border-transparent text-gray-100 focus:ring-amber-500' 
                  : 'bg-gray-50 border-transparent text-gray-900 focus:ring-amber-600'"
              >
                <option value="0">None</option>
                <!-- Users will be populated from store -->
              </select>
            </div>

            <BaseSelect
              id="disposition"
              label="Disposition"
              v-model="formData.disposition_id"
              placeholder="Select disposition"
              :category-id="363034"
              @change="handleDispositionChange"
            />
          </div>
        </div>
      </AccordionSection>

      <!-- 2. Clients Section -->
      <AccordionSection
        title="Clients"
        :isOpen="openSections.clients"
        :badge="formData.clients_case.length"
        @toggle="toggleSection('clients')"
      >
        <div class="space-y-3">
          <!-- Client List -->
          <div v-if="formData.clients_case.length > 0" class="space-y-2">
            <div
              v-for="(client, index) in formData.clients_case"
              :key="index"
              class="flex items-center justify-between p-3 border rounded-lg"
              :class="isDarkMode 
                ? 'bg-gray-800 border-transparent' 
                : 'bg-gray-50 border-transparent'"
            >
              <div class="flex-1">
                <div 
                  class="font-semibold text-sm"
                  :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
                >
                  {{ client.name || 'Unnamed Client' }}
                </div>
                <div 
                  class="text-xs mt-1"
                  :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
                >
                  {{ client.age || 'Age unknown' }} • {{ client.sex || 'Gender unknown' }}
                </div>
              </div>
              <div class="flex gap-2">
                <button
                  type="button"
                  @click="editClient(index)"
                  class="px-3 py-1.5 text-xs font-medium rounded transition-colors"
                  :class="isDarkMode 
                    ? 'bg-amber-600 text-white hover:bg-amber-700' 
                    : 'bg-amber-700 text-white hover:bg-amber-800'"
                >
                  Edit
                </button>
                <button
                  type="button"
                  @click="removeClient(index)"
                  class="px-3 py-1.5 text-xs font-medium bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                >
                  Remove
                </button>
              </div>
            </div>
          </div>
          
          <!-- Empty State -->
          <div 
            v-else
            class="text-center p-8 border border-dashed rounded-lg"
            :class="isDarkMode 
              ? 'bg-gray-800 border-transparent text-gray-500' 
              : 'bg-white border-transparent text-gray-500'"
          >
            No clients added yet
          </div>

          <!-- Add Client Button -->
          <button
            type="button"
            @click="openClientModal"
            class="w-full px-4 py-2 border-2 border-dashed rounded-lg transition-colors font-medium flex items-center justify-center gap-2"
            :class="isDarkMode 
              ? 'border-transparent text-gray-400 hover:border-amber-500 hover:text-amber-500 hover:bg-amber-900/20' 
              : 'border-transparent text-gray-600 hover:border-amber-600 hover:text-amber-700 hover:bg-amber-50'"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            Add Client
          </button>
        </div>
      </AccordionSection>

      <!-- 3. Perpetrators Section -->
      <AccordionSection
        title="Perpetrators"
        :isOpen="openSections.perpetrators"
        :badge="formData.perpetrators_case.length"
        @toggle="toggleSection('perpetrators')"
      >
        <div class="space-y-3">
          <!-- Perpetrator List -->
          <div v-if="formData.perpetrators_case.length > 0" class="space-y-2">
            <div
              v-for="(perp, index) in formData.perpetrators_case"
              :key="index"
              class="flex items-center justify-between p-3 border rounded-lg"
              :class="isDarkMode 
                ? 'bg-gray-800 border-transparent' 
                : 'bg-gray-50 border-transparent'"
            >
              <div class="flex-1">
                <div 
                  class="font-semibold text-sm"
                  :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
                >
                  {{ perp.name || 'Unnamed' }}
                </div>
                <div 
                  class="text-xs mt-1"
                  :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
                >
                  {{ perp.age || 'Age unknown' }} • {{ perp.sex || 'Gender unknown' }}
                </div>
              </div>
              <div class="flex gap-2">
                <button
                  type="button"
                  @click="editPerpetrator(index)"
                  class="px-3 py-1.5 text-xs font-medium rounded transition-colors"
                  :class="isDarkMode 
                    ? 'bg-amber-600 text-white hover:bg-amber-700' 
                    : 'bg-amber-700 text-white hover:bg-amber-800'"
                >
                  Edit
                </button>
                <button
                  type="button"
                  @click="removePerpetrator(index)"
                  class="px-3 py-1.5 text-xs font-medium bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
                >
                  Remove
                </button>
              </div>
            </div>
          </div>

          <!-- Empty State -->
          <div 
            v-else
            class="text-center p-8 border border-dashed rounded-lg"
            :class="isDarkMode 
              ? 'bg-gray-800 border-transparent text-gray-500' 
              : 'bg-white border-transparent text-gray-500'"
          >
            No perpetrators added yet
          </div>

          <!-- Add Perpetrator Button -->
          <button
            type="button"
            @click="openPerpetratorModal"
            class="w-full px-4 py-2 border-2 border-dashed rounded-lg transition-colors font-medium flex items-center justify-center gap-2"
            :class="isDarkMode 
              ? 'border-transparent text-gray-400 hover:border-amber-500 hover:text-amber-500 hover:bg-amber-900/20' 
              : 'border-transparent text-gray-600 hover:border-amber-600 hover:text-amber-700 hover:bg-amber-50'"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            Add Perpetrator
          </button>
        </div>
      </AccordionSection>

      <!-- 4. Services & Referrals Section -->
      <AccordionSection
        title="Services & Referrals"
        :isOpen="openSections.services"
        :badge="formData.services.length"
        @toggle="toggleSection('services')"
      >
        <div class="space-y-4">
          <BaseOptions
            id="services-offered"
            label="Services Offered"
            v-model="formData.services"
            placeholder="Select services..."
            :category-id="113"
            @selection-change="handleServicesChange"
          />
        </div>
      </AccordionSection>

      <!-- 5. Attachments Section -->
      <AccordionSection
        title="Attachments"
        :isOpen="openSections.attachments"
        :badge="formData.attachments_case.length"
        @toggle="toggleSection('attachments')"
      >
        <AttachmentUpload
          v-model="formData.attachments_case"
          label="Case Attachments"
          description="Upload or manage case documents"
          @upload-complete="handleAttachmentUpload"
        />
      </AccordionSection>
    </div>

    <!-- Bottom Save/Cancel buttons -->
    <div 
      class="flex justify-end gap-3 mt-6 pt-6 border-t sticky bottom-0 -mx-6 px-6 -mb-6 pb-6"
      :class="isDarkMode 
        ? 'bg-gray-900 border-transparent' 
        : 'bg-white border-transparent'"
    >
      <button
        @click="$emit('cancel')"
        type="button"
        class="px-4 py-2 border rounded-lg transition-colors font-medium"
        :class="isDarkMode 
          ? 'bg-gray-700 text-gray-300 border-transparent hover:bg-gray-600' 
          : 'bg-white text-gray-700 border-transparent hover:bg-gray-50'"
      >
        Cancel
      </button>
      <button
        @click="handleSave"
        :disabled="isSubmitting"
        type="button"
        class="px-4 py-2 text-white rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        :class="isDarkMode 
          ? 'bg-amber-600 hover:bg-amber-700' 
          : 'bg-amber-700 hover:bg-amber-800'"
      >
        <span v-if="isSubmitting" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
        {{ isSubmitting ? 'Saving...' : 'Save Changes' }}
      </button>
    </div>
  </div>

  <!-- Modals -->
  <ClientModal
    v-if="clientModalOpen"
    :clients="[]"
    :clientForm="clientForm"
    :currentClientStep="currentClientStep"
    @close-modal="closeClientModal"
    @update-client-form="updateClientForm"
    @prev-client-step="prevClientStep"
    @next-client-step="nextClientStep"
    @add-client="addClient"
  />

  <PerpetratorModal
    v-if="perpetratorModalOpen"
    :perpetrators="[]"
    :perpetratorForm="perpetratorForm"
    :currentPerpetratorStep="currentPerpetratorStep"
    :perpetratorModalOpen="perpetratorModalOpen"
    @close-modal="closePerpetratorModal"
    @update-perpetrator-form="updatePerpetratorForm"
    @prev-perpetrator-step="prevPerpetratorStep"
    @next-perpetrator-step="nextPerpetratorStep"
    @add-perpetrator="addPerpetrator"
  />
</template>

<script setup>
import { ref, reactive, inject, computed, onMounted } from 'vue'
import { toast } from 'vue-sonner'
import BaseSelect from '@/components/base/BaseSelect.vue'
import BaseOptions from '@/components/base/BaseOptions.vue'
import AttachmentUpload from '@/components/case-create/AttachmentUpload.vue'
import ClientModal from '@/components/case-create/ClientModal.vue'
import PerpetratorModal from '@/components/case-create/PerpetratorModal.vue'
import AccordionSection from '@/components/cases/AccordionSection.vue'

const props = defineProps({
  caseItem: { type: Array, required: true },
  cases_k: { type: Object, required: true },
  isSubmitting: { type: Boolean, default: false }
})

const emit = defineEmits(['submit', 'cancel'])

const isDarkMode = inject('isDarkMode')

// Accordion state
const openSections = reactive({
  caseInfo: true,
  clients: false,
  perpetrators: false,
  services: false,
  attachments: false
})

// Form data - will be populated from caseItem
const formData = reactive({
  narrative: '',
  plan: '',
  case_category_id: '',
  gbv_related: '',
  priority: '',
  status: '',
  justice_id: '',
  assessment_id: '',
  escalated_to_id: '',
  disposition_id: '',
  clients_case: [],
  perpetrators_case: [],
  services: [],
  attachments_case: []
})

// Modal states
const clientModalOpen = ref(false)
const perpetratorModalOpen = ref(false)
const currentClientStep = ref(0)
const currentPerpetratorStep = ref(0)
const editingClientIndex = ref(null)
const editingPerpetratorIndex = ref(null)

const clientForm = reactive({
  name: '',
  age: '',
  // ... all client fields
})

const perpetratorForm = reactive({
  name: '',
  age: '',
  // ... all perpetrator fields
})

// Helper to get case values
const getCaseValue = (key) => {
  if (!props.caseItem || !props.cases_k?.[key]) return null
  return props.caseItem[props.cases_k[key][0]]
}

// Initialize form data from case
onMounted(() => {
  formData.narrative = getCaseValue('narrative') || ''
  formData.plan = getCaseValue('plan') || ''
  formData.case_category_id = getCaseValue('case_category_id') || ''
  formData.gbv_related = getCaseValue('gbv_related') || ''
  formData.priority = getCaseValue('priority') || ''
  formData.status = getCaseValue('status') || ''
  formData.justice_id = getCaseValue('justice_id') || ''
  formData.assessment_id = getCaseValue('assessment_id') || ''
  formData.escalated_to_id = getCaseValue('escalated_to_id') || '0'
  formData.disposition_id = getCaseValue('disposition_id') || ''
  
  // TODO: Parse clients, perpetrators, services, attachments from case data
  // These might be JSON strings or nested arrays - need to check your backend structure
})

// Accordion toggle
const toggleSection = (section) => {
  openSections[section] = !openSections[section]
}

// Client handlers
const openClientModal = () => {
  editingClientIndex.value = null
  currentClientStep.value = 0
  Object.keys(clientForm).forEach(key => clientForm[key] = '')
  clientModalOpen.value = true
}

const editClient = (index) => {
  editingClientIndex.value = index
  const client = formData.clients_case[index]
  Object.assign(clientForm, client)
  currentClientStep.value = 0
  clientModalOpen.value = true
}

const removeClient = (index) => {
  formData.clients_case.splice(index, 1)
  toast.info('Client removed')
}

const closeClientModal = () => {
  clientModalOpen.value = false
  editingClientIndex.value = null
}

const addClient = () => {
  if (editingClientIndex.value !== null) {
    // Update existing
    formData.clients_case[editingClientIndex.value] = { ...clientForm }
    toast.success('Client updated')
  } else {
    // Add new
    formData.clients_case.push({ ...clientForm })
    toast.success('Client added')
  }
  closeClientModal()
}

// Perpetrator handlers (similar pattern)
const openPerpetratorModal = () => {
  editingPerpetratorIndex.value = null
  currentPerpetratorStep.value = 0
  Object.keys(perpetratorForm).forEach(key => perpetratorForm[key] = '')
  perpetratorModalOpen.value = true
}

const editPerpetrator = (index) => {
  editingPerpetratorIndex.value = index
  const perp = formData.perpetrators_case[index]
  Object.assign(perpetratorForm, perp)
  currentPerpetratorStep.value = 0
  perpetratorModalOpen.value = true
}

const removePerpetrator = (index) => {
  formData.perpetrators_case.splice(index, 1)
  toast.info('Perpetrator removed')
}

const closePerpetratorModal = () => {
  perpetratorModalOpen.value = false
  editingPerpetratorIndex.value = null
}

const addPerpetrator = () => {
  if (editingPerpetratorIndex.value !== null) {
    formData.perpetrators_case[editingPerpetratorIndex.value] = { ...perpetratorForm }
    toast.success('Perpetrator updated')
  } else {
    formData.perpetrators_case.push({ ...perpetratorForm })
    toast.success('Perpetrator added')
  }
  closePerpetratorModal()
}

// Change handlers
const handleCategoryChange = (value, text) => {
  formData.case_category_id = value
}

const handleGBVChange = (value, text) => {
  formData.gbv_related = value
}

const handleJusticeChange = (value, text) => {
  formData.justice_id = value
}

const handleAssessmentChange = (value, text) => {
  formData.assessment_id = value
}

const handleDispositionChange = (value, text) => {
  formData.disposition_id = value
}

const handleServicesChange = (selectionData) => {
  formData.services = selectionData.values || []
}

const handleAttachmentUpload = (data) => {
  // Attachments already updated via v-model
}

// Modal step navigation
const updateClientForm = (data) => Object.assign(clientForm, data)
const updatePerpetratorForm = (data) => Object.assign(perpetratorForm, data)
const prevClientStep = () => currentClientStep.value > 0 && currentClientStep.value--
const nextClientStep = () => currentClientStep.value < 4 && currentClientStep.value++
const prevPerpetratorStep = () => currentPerpetratorStep.value > 0 && currentPerpetratorStep.value--
const nextPerpetratorStep = () => currentPerpetratorStep.value < 3 && currentPerpetratorStep.value++

// Save handler
const handleSave = () => {
  // Validate required fields
  const errors = []
  if (!formData.narrative?.trim()) errors.push('Narrative')
  if (!formData.plan?.trim()) errors.push('Plan')
  if (!formData.case_category_id) errors.push('Case Category')
  if (!formData.gbv_related) errors.push('GBV Related')
  if (!formData.priority) errors.push('Priority')
  if (!formData.status) errors.push('Status')
  
  if (errors.length > 0) {
    toast.error('Required fields missing', {
      description: errors.join(', ')
    })
    return
  }
  
  emit('submit', formData)
}
</script>
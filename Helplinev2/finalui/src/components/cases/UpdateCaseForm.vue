<template>
  <div class="space-y-6">
    <div
      class="p-4 rounded-lg border-l-4"
      :class="isDarkMode
        ? 'bg-amber-900/20 border-amber-500 text-blue-300'
        : 'bg-blue-50 border-amber-500 text-blue-800'"
    >
      <p class="text-sm">Update case status, priority, and other critical information</p>
    </div>

    <form @submit.prevent="handleSubmit" class="space-y-6">
      <!-- Case Plan (Mandatory) -->
      <FormField
        v-model="localForm.plan"
        label="Case Plan Update"
        type="textarea"
        :rows="4"
        placeholder="Enter case plan update..."
        required
        :error="errors.plan"
      />

      <!-- Justice System Status -->
      <div>
        <BaseSelect
          id="justice-system-update"
          label="State of the Case in the Justice System"
          v-model="localForm.justice_id"
          placeholder="Select justice system status"
          :category-id="236687"
          @change="handleJusticeChange"
        />
      </div>

      <!-- General Case Assessment -->
      <div>
        <BaseSelect
          id="assessment-update"
          label="General Case Assessment"
          v-model="localForm.assessment_id"
          placeholder="Select assessment status"
          :category-id="236694"
          @change="handleAssessmentChange"
        />
      </div>

      <!-- Priority (Mandatory) -->
      <FormField
        v-model="localForm.priority"
        label="Priority"
        type="select"
        :options="priorityOptions"
        required
        :error="errors.priority"
      />

      <!-- Status (Mandatory) -->
      <FormField
        v-model="localForm.status"
        label="Status"
        type="select"
        :options="statusOptions"
        required
        :error="errors.status"
      />

      <!-- Escalated To -->
      <div>
        <label 
          class="block text-sm font-semibold mb-2"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          Escalated To
        </label>
        
        <!-- Loading State -->
        <div 
          v-if="userStore.loading" 
          class="flex items-center gap-2 p-3 border rounded-lg"
          :class="isDarkMode 
            ? 'bg-gray-800 border-transparent' 
            : 'bg-white border-transparent'"
        >
          <div 
            class="w-4 h-4 border-2 rounded-full animate-spin"
            :class="isDarkMode 
              ? 'border-transparent border-t-blue-500' 
              : 'border-transparent border-t-amber-700'"
          ></div>
          <span 
            class="text-sm"
            :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
          >
            Loading users...
          </span>
        </div>

        <!-- User Select -->
        <select 
          v-else
          v-model="localForm.escalated_to_id" 
          class="w-full px-4 py-3 rounded-lg border focus:ring-2 focus:ring-offset-0 transition-all"
          :class="isDarkMode
            ? 'bg-gray-800 border-transparent text-gray-300 focus:ring-amber-500'
            : 'bg-white border-transparent text-gray-900 focus:ring-amber-500'"
          @change="handleEscalationChange"
        >
          <option value="0">None</option>
          <option 
            v-for="user in filteredUsers" 
            :key="getUserId(user)" 
            :value="getUserId(user)"
          >
            {{ getUserName(user) }} - {{ getUserRole(user) }}
          </option>
        </select>
      </div>

      <!-- Disposition -->
      <div>
        <BaseSelect
          id="disposition-update"
          label="Disposition"
          v-model="localForm.disposition_id"
          placeholder="Select disposition"
          :category-id="363034"
          @change="handleDispositionChange"
        />
      </div>

      <!-- Action Buttons -->
      <div class="flex gap-3 pt-4">
        <button
          type="submit"
          :disabled="isSubmitting"
          class="flex-1 px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 shadow-lg active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
          :class="isDarkMode
            ? 'bg-amber-600 text-white hover:bg-amber-700'
            : 'bg-amber-700 text-white hover:bg-amber-800'"
        >
          <i-mdi-loading v-if="isSubmitting" class="w-5 h-5 animate-spin" />
          <i-mdi-check v-else class="w-5 h-5" />
          {{ isSubmitting ? 'Updating...' : 'Save Update' }}
        </button>
        <button
          type="button"
          @click="$emit('cancel')"
          :disabled="isSubmitting"
          class="px-6 py-3 rounded-lg font-medium transition-all duration-200 border disabled:opacity-50 disabled:cursor-not-allowed"
          :class="isDarkMode
            ? 'bg-gray-800 text-gray-300 border-transparent hover:bg-gray-700'
            : 'bg-white text-gray-700 border-transparent hover:bg-gray-50'"
        >
          Cancel
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, inject, computed, watch, onMounted } from 'vue'
import FormField from './FormField.vue'
import BaseSelect from '@/components/base/BaseSelect.vue'
import { useUserStore } from '@/stores/users'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  caseItem: {
    type: Object,
    required: true
  },
  cases_k: {
    type: Object,
    required: true
  },
  isSubmitting: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['submit', 'cancel'])

// Inject theme and stores
const isDarkMode = inject('isDarkMode')
const userStore = useUserStore()
const authStore = useAuthStore()

// Form errors
const errors = ref({
  plan: '',
  priority: '',
  status: ''
})

// Text values for submission
const textValues = ref({
  justice_text: '',
  assessment_text: '',
  disposition_text: '',
  escalated_to_text: ''
})

// Dropdown options
const priorityOptions = [
  { value: '1', label: 'Low' },
  { value: '2', label: 'Medium' },
  { value: '3', label: 'High' }
]

const statusOptions = [
  { value: '1', label: 'Open' },
  { value: '2', label: 'Closed' }
]

// Form state
const localForm = ref({
  plan: '',
  justice_id: '',
  assessment_id: '',
  priority: '',
  status: '',
  escalated_to_id: '',
  disposition_id: ''
})

// Load users on mount
onMounted(async () => {
  if (!userStore.users.length) {
    await userStore.listUsers()
  }
})

// Helper to get value using cases_k mapping
const getValue = (key) => {
  if (!props.caseItem || !props.cases_k?.[key]) return null
  return props.caseItem[props.cases_k[key][0]]
}

// Initialize form with case data
watch(() => props.caseItem, (newCase) => {
  if (newCase) {
    localForm.value = {
      plan: getValue('plan') || '',
      justice_id: getValue('justice_id') || '',
      assessment_id: getValue('assessment_id') || '',
      priority: getValue('priority')?.toString() || '',
      status: getValue('status')?.toString() || '',
      escalated_to_id: getValue('escalated_to_id') || '',
      disposition_id: getValue('disposition_id') || ''
    }
  }
}, { immediate: true })

// Helper functions for user data
const getFieldIndex = (fieldName) => {
  const mapping = userStore.users_k?.[fieldName]
  if (mapping && Array.isArray(mapping) && mapping.length > 0) {
    return parseInt(mapping[0])
  }
  return null
}

const getUserValue = (user, fieldName) => {
  if (!user || !Array.isArray(user)) return ""
  const idx = getFieldIndex(fieldName)
  if (idx !== null && idx >= 0 && idx < user.length) {
    return user[idx] || ""
  }
  return ""
}

const getUserId = (user) => getUserValue(user, 'id')

const getUserName = (user) => {
  const fullname = getUserValue(user, 'contact_fullname')
  const fname = getUserValue(user, 'contact_fname')
  const lname = getUserValue(user, 'contact_lname')
  const username = getUserValue(user, 'usn')
  
  if (fullname) return fullname
  if (fname && lname) return `${fname} ${lname}`
  if (fname) return fname
  if (username) return username
  return "Unnamed User"
}

const getUserRole = (user) => {
  const roleId = getUserValue(user, 'role')
  const roleMap = {
    '1': 'Counsellor',
    '2': 'Supervisor',
    '3': 'Case Manager',
    '4': 'Case Worker',
    '5': 'Partner',
    '6': 'Media Account',
    '99': 'Administrator'
  }
  return roleMap[roleId] || roleId || "No Role"
}

// Filter users with higher authority
const filteredUsers = computed(() => {
  const currentUserRole = parseInt(authStore.userRole)
  
  if (!currentUserRole) return []
  if (currentUserRole === 99) return userStore.users
  
  return userStore.users.filter(user => {
    const userRoleId = parseInt(getUserValue(user, 'role'))
    if (!userRoleId) return false
    if (userRoleId === 5 || userRoleId === 6) return false
    return userRoleId > currentUserRole
  })
})

// Change handlers
const handleJusticeChange = (value, text) => {
  localForm.value.justice_id = value
  textValues.value.justice_text = text
}

const handleAssessmentChange = (value, text) => {
  localForm.value.assessment_id = value
  textValues.value.assessment_text = text
}

const handleDispositionChange = (value, text) => {
  localForm.value.disposition_id = value
  textValues.value.disposition_text = text
}

const handleEscalationChange = (event) => {
  const value = event.target.value
  localForm.value.escalated_to_id = value
  
  if (value === '0') {
    textValues.value.escalated_to_text = 'None'
  } else {
    const user = filteredUsers.value.find(u => getUserId(u) === value)
    if (user) {
      textValues.value.escalated_to_text = `${getUserName(user)} - ${getUserRole(user)}`
    }
  }
}

// Validate form
const validateForm = () => {
  let isValid = true
  errors.value = { plan: '', priority: '', status: '' }

  if (!localForm.value.plan || localForm.value.plan.trim() === '') {
    errors.value.plan = 'Case plan is required'
    isValid = false
  }

  if (!localForm.value.priority) {
    errors.value.priority = 'Priority is required'
    isValid = false
  }

  if (!localForm.value.status) {
    errors.value.status = 'Status is required'
    isValid = false
  }

  return isValid
}

// Submit handler
const handleSubmit = () => {
  if (!validateForm()) {
    return
  }

  // Combine form data with text values
  const formDataWithText = {
    ...localForm.value,
    ...textValues.value
  }

  emit('submit', formDataWithText)
}
</script>
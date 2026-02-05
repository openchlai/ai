<template>
  <div class="min-h-96">
    <form class="flex flex-col gap-3.5" @submit.prevent="handleFormSubmit">
      <div>
        <div class="text-xl font-semibold mb-2" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">
          Case Details
        </div>
        <p class="text-sm mb-5" :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'">
          Enter case details including narrative, priority, and classification. Fields marked with * are required.
        </p>

        <!-- GBV Related (Required) -->
        <div class="mb-5">
          <label class="block font-semibold mb-2" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">
            Is this Case GBV Related? *
          </label>
          <TaxonomySelect v-model="localForm.isGBVRelated" placeholder="Select an option" root-key="GBV_RELATED"
            @change="handleGBVChange" />
        </div>

        <!-- Case Category (Required) -->
        <div class="mb-5">
          <TaxonomySelect id="case-category" label="Case Category *" v-model="localForm.categories"
            placeholder="Select case category" root-key="CASE_CATEGORY" searchable @change="handleCategoryChange"
            @trigger="handleWorkflowTrigger" />
        </div>

        <!-- Narrative (Required) -->
        <div class="mb-5">
          <BaseTextarea id="case-narrative" label="Case Narrative *" v-model="localForm.narrative"
            placeholder="Describe the case details, incident, and circumstances in detail..." :rows="6"
            @input="updateForm" />
        </div>

        <!-- Plan (Required) -->
        <div class="mb-5">
          <label for="case-plan" class="block font-semibold mb-2"
            :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">
            Case Plan *
          </label>
          <textarea v-model="localForm.plan" id="case-plan"
            class="w-full px-3 py-2 border rounded-lg text-sm transition-all focus:outline-none focus:ring-2 focus:border-transparent resize-vertical"
            :class="isDarkMode
              ? 'bg-gray-700 border-transparent text-gray-100 placeholder-gray-500 focus:ring-[#008080]'
              : 'bg-gray-50 border-transparent text-gray-900 placeholder-gray-400 focus:ring-[#003366]'"
            placeholder="Outline the planned interventions and support services..." rows="4"
            @input="updateForm"></textarea>
        </div>

        <!-- Priority and Status (Required) -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
          <!-- Priority -->
          <div>
            <label class="block font-semibold mb-2" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">
              Priority *
            </label>
            <select v-model="localForm.priority"
              class="w-full px-3 py-2 border rounded-lg text-sm transition-all focus:outline-none focus:ring-2 focus:border-transparent"
              :class="isDarkMode
                ? 'bg-gray-700 border-transparent text-gray-100 focus:ring-[#008080]'
                : 'bg-gray-50 border-transparent text-gray-900 focus:ring-[#003366]'" @change="handlePriorityChange">
              <option value="">Select priority</option>
              <option value="3">High</option>
              <option value="2">Medium</option>
              <option value="1">Low</option>
            </select>
          </div>

          <!-- Status -->
          <div>
            <label class="block font-semibold mb-2" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">
              Status *
            </label>
            <select v-model="localForm.status"
              class="w-full px-3 py-2 border rounded-lg text-sm transition-all focus:outline-none focus:ring-2 focus:border-transparent"
              :class="isDarkMode
                ? 'bg-gray-700 border-transparent text-gray-100 focus:ring-[#008080]'
                : 'bg-gray-50 border-transparent text-gray-900 focus:ring-[#003366]'" @change="handleStatusChange">
              <option value="">Select status</option>
              <option value="1">Open</option>
              <option value="2">Closed</option>
            </select>
          </div>
        </div>

        <!-- Department (Required) -->
        <div class="mb-5">
          <label class="block font-semibold mb-2" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">
            Department *
          </label>
          <div class="flex gap-4 mt-2">
            <label class="flex items-center gap-1.5 cursor-pointer">
              <input v-model="localForm.department" type="radio" value="116" @change="handleDepartmentChange"
                class="w-4 h-4" :class="isDarkMode ? 'text-[#008080]' : 'text-[#003366]'" />
              <span class="text-sm" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                116
              </span>
            </label>
            <label class="flex items-center gap-1.5 cursor-pointer">
              <input v-model="localForm.department" type="radio" value="labor" @change="handleDepartmentChange"
                class="w-4 h-4" :class="isDarkMode ? 'text-[#008080]' : 'text-[#003366]'" />
              <span class="text-sm" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                Labor
              </span>
            </label>
          </div>

          <!-- Client Passport Number (conditional) -->
          <div v-if="showPassportField" class="mt-4 p-4 border rounded-lg animate-fadeIn" :class="isDarkMode
            ? 'bg-black border-transparent'
            : 'bg-gray-50 border-transparent'">
            <label for="client-passport" class="block font-semibold mb-2"
              :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">
              Client's Passport Number
            </label>
            <input id="client-passport" v-model="localForm.clientPassportNumber" type="text"
              class="w-full px-3 py-2 border rounded-lg text-sm transition-all focus:outline-none focus:ring-2 focus:border-transparent"
              :class="isDarkMode
                ? 'bg-gray-700 border-transparent text-gray-100 placeholder-gray-500 focus:ring-amber-500'
                : 'bg-white border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'"
              placeholder="Enter client's passport number" @input="updateForm" />
          </div>
        </div>

        <!-- Incident Location (Required) -->
        <div class="mb-5">
          <TaxonomySelect id="incident-location" label="Incident Location *" v-model="localForm.incidentLocation"
            placeholder="Select incident location (District)" root-key="LOCATION"
            @change="handleIncidentLocationChange" />
        </div>

        <!-- Justice System State and General Assessment -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-5">
          <div>
            <TaxonomySelect id="justice-system-state" label="State of the Case in the Justice System *"
              v-model="localForm.justiceSystemState" placeholder="Select an option" root-key="JUSTICE_SYSTEM_STATE"
              @change="handleJusticeSystemChange" />
          </div>
          <div>
            <TaxonomySelect id="general-assessment" label="General Case Assessment *"
              v-model="localForm.generalAssessment" placeholder="Select an option" root-key="GENERAL_ASSESSMENT"
              @change="handleGeneralAssessmentChange" />
          </div>
        </div>

        <!-- Escalated To -->
        <div class="mb-5">
          <label class="block font-semibold mb-2" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">
            Escalated To
          </label>

          <!-- Loading State -->
          <div v-if="userStore.loading" class="flex items-center gap-2 p-3 border rounded-lg" :class="isDarkMode
            ? 'bg-gray-700 border-transparent'
            : 'bg-gray-50 border-transparent'">
            <div class="w-4 h-4 border-2 rounded-full animate-spin" :class="isDarkMode
              ? 'border-transparent border-t-[#008080]'
              : 'border-transparent border-t-[#003366]'"></div>
            <span class="text-sm" :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'">
              Loading users...
            </span>
          </div>

          <!-- User Select -->
          <select v-else v-model="localForm.escalatedTo"
            class="w-full px-3 py-2 border rounded-lg text-sm transition-all focus:outline-none focus:ring-2 focus:border-transparent"
            :class="isDarkMode
              ? 'bg-gray-700 border-transparent text-gray-100 focus:ring-[#008080]'
              : 'bg-gray-50 border-transparent text-gray-900 focus:ring-[#003366]'" @change="handleEscalationChange">
            <option value="0">None</option>
            <option v-for="user in filteredUsers" :key="getUserId(user)" :value="getUserId(user)">
              {{ getUserName(user) }} - {{ getUserRole(user) }}
            </option>
          </select>

          <!-- Error State -->
          <p v-if="userStore.error" class="text-xs mt-1" :class="isDarkMode ? 'text-red-400' : 'text-red-600'">
            Failed to load users: {{ userStore.error }}
          </p>
        </div>
      </div>

      <div class="flex gap-3 justify-between mt-6 pt-5 border-t"
        :class="isDarkMode ? 'border-transparent' : 'border-transparent'">
        <button type="button" class="px-4 py-2 border rounded-lg transition-colors" :class="isDarkMode
          ? 'bg-gray-700 text-gray-300 border-transparent hover:bg-gray-600'
          : 'bg-white text-gray-700 border-transparent hover:bg-gray-50'" @click="goToStep(1)">
          Back
        </button>
        <div class="flex gap-3">
          <button type="submit" class="px-4 py-2 text-white rounded-lg transition-colors" :class="isDarkMode
            ? 'bg-[#008080] hover:bg-[#006666]'
            : 'bg-[#003366] hover:bg-[#002244]'">
            Continue
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
  import { reactive, watch, computed, onMounted, inject } from "vue"
  import { useAuthStore } from "@/stores/auth"
  import { useUserStore } from "@/stores/users"
  import { useTaxonomyStore } from "@/stores/taxonomy"
  import TaxonomySelect from "@/components/base/TaxonomySelect.vue"
  import { toast } from 'vue-sonner'
  import BaseTextarea from "@/components/base/BaseTextarea.vue"

  const props = defineProps({
    currentStep: { type: Number, required: true },
    formData: { type: Object, required: true }
  })

  const emit = defineEmits([
    "form-update",
    "save-and-proceed",
    "step-change"
  ])

  // Inject theme
  const isDarkMode = inject('isDarkMode')

  const authStore = useAuthStore()
  const userStore = useUserStore()
  const taxonomyStore = useTaxonomyStore()

  const localForm = reactive({
    ...props.formData,
    clientPassportNumber: props.formData.clientPassportNumber || '',
    justiceSystemState: props.formData.justiceSystemState || '',
    generalAssessment: props.formData.generalAssessment || '',
    incidentLocation: props.formData.incidentLocation || '',
    // Text fields
    isGBVRelatedText: props.formData.isGBVRelatedText || '',
    categoriesText: props.formData.categoriesText || '',
    priorityText: props.formData.priorityText || '',
    statusText: props.formData.statusText || '',
    departmentText: props.formData.departmentText || '',
    escalatedToText: props.formData.escalatedToText || '',
    justiceSystemStateText: props.formData.justiceSystemStateText || '',
    generalAssessmentText: props.formData.generalAssessmentText || '',
    incidentLocationText: props.formData.incidentLocationText || ''
  })

  // Load users on mount
  onMounted(async () => {
    if (!userStore.users.length) {
      await userStore.listUsers()
    }
  })

  watch(() => props.formData, (newData) => {
    Object.assign(localForm, newData)
  }, { deep: true })

  // Computed properties
  const showPassportField = computed(() => {
    return localForm.department === 'labor'
  })

  const users = computed(() => userStore.users || [])

  // Helper functions to extract user data
  const getFieldIndex = (fieldName) => {
    const mapping = userStore.users_k?.[fieldName]
    if (mapping && Array.isArray(mapping) && mapping.length > 0) {
      return parseInt(mapping[0])
    }
    return null
  }

  const getValue = (user, fieldName) => {
    if (!user || !Array.isArray(user)) return ""
    const idx = getFieldIndex(fieldName)
    if (idx !== null && idx >= 0 && idx < user.length) {
      return user[idx] || ""
    }
    return ""
  }

  const getUserId = (user) => {
    return getValue(user, 'id')
  }

  const getUserName = (user) => {
    const fullname = getValue(user, 'contact_fullname')
    const fname = getValue(user, 'contact_fname')
    const lname = getValue(user, 'contact_lname')
    const username = getValue(user, 'usn')

    if (fullname) return fullname
    if (fname && lname) return `${fname} ${lname}`
    if (fname) return fname
    if (username) return username
    return "Unnamed User"
  }

  const getUserRole = (user) => {
    const roleId = getValue(user, 'role')

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

  // ROLE-BASED FILTERING: Show only users with higher authority
  const filteredUsers = computed(() => {
    const currentUserRole = parseInt(authStore.userRole)

    console.log('🔑 Current user role:', currentUserRole)

    if (!currentUserRole) {
      console.warn('⚠️ No current user role found')
      return []
    }

    // Administrator (99) can escalate to everyone
    if (currentUserRole === 99) {
      console.log('👑 Admin user - showing all users')
      return users.value
    }

    // Filter users with higher role numbers
    const filtered = users.value.filter(user => {
      const userRoleId = parseInt(getValue(user, 'role'))

      // Skip invalid roles
      if (!userRoleId) return false

      // Skip Partner (5) and Media Account (6) - they're not in the escalation hierarchy
      if (userRoleId === 5 || userRoleId === 6) return false

      // Show users with higher role numbers (higher authority)
      const hasHigherRole = userRoleId > currentUserRole

      if (hasHigherRole) {
        console.log(`✅ Including user ${getUserName(user)} (role ${userRoleId}) - higher than ${currentUserRole}`)
      }

      return hasHigherRole
    })

    console.log(`📋 Filtered ${filtered.length} users from ${users.value.length} total`)

    return filtered
  })

  // Workflow Trigger Handler
  const handleWorkflowTrigger = ({ triggerKey, id, text }) => {
    console.log(`[Step2] Workflow Trigger Fired: ${triggerKey} (${id})`)

    if (triggerKey === 'SEXUAL_ABUSE') {
      // Automatically set GBV to Yes (Legacy behavior requirement)
      // GBV Root 118, 'Yes' is typically 118002
      localForm.isGBVRelated = '118002'
      localForm.isGBVRelatedText = 'Yes'
      toast.info('Sexual Abuse selected: GBV fields activated.')
    }
  }

  // Helper to get category text
  const getCategoryText = async (categoryId, parentId) => {
    try {
      const data = await taxonomyStore.viewCategory(parentId)
      const k = data.keys
      const idIdx = Number(k?.id?.[0] ?? 0)
      const nameIdx = Number(k?.name?.[0] ?? 5)

      const option = data.items?.find(row => row[idIdx] === categoryId)
      return option ? option[nameIdx] : ''
    } catch (error) {
      console.error('Error fetching category text:', error)
      return ''
    }
  }

  // Change handlers to capture text
  const handleGBVChange = ({ id, text }) => {
    localForm.isGBVRelated = id
    localForm.isGBVRelatedText = text
    updateForm()
  }

  const handleCategoryChange = ({ id, text }) => {
    localForm.categories = id
    localForm.categoriesText = text
    updateForm()
  }

  const handlePriorityChange = (event) => {
    const value = event.target.value
    localForm.priority = value
    const priorityMap = { '3': 'High', '2': 'Medium', '1': 'Low' }
    localForm.priorityText = priorityMap[value] || ''
    updateForm()
  }

  const handleStatusChange = (event) => {
    const value = event.target.value
    localForm.status = value
    const statusMap = { '1': 'Open', '2': 'Closed' }
    localForm.statusText = statusMap[value] || ''
    updateForm()
  }

  const handleDepartmentChange = () => {
    const deptMap = { '116': '116', 'labor': 'Labor' }
    localForm.departmentText = deptMap[localForm.department] || ''

    if (localForm.department !== 'labor') {
      localForm.clientPassportNumber = ''
    }
    updateForm()
  }

  const handleJusticeSystemChange = ({ id, text }) => {
    localForm.justiceSystemState = id
    localForm.justiceSystemStateText = text
    updateForm()
  }

  const handleGeneralAssessmentChange = ({ id, text }) => {
    localForm.generalAssessment = id
    localForm.generalAssessmentText = text
    updateForm()
  }

  const handleIncidentLocationChange = ({ id, text }) => {
    localForm.incidentLocation = id
    localForm.incidentLocationText = text
    updateForm()
  }

  const handleEscalationChange = (event) => {
    const value = event.target.value
    localForm.escalatedTo = value

    if (value === '0') {
      localForm.escalatedToText = 'None'
    } else {
      const user = filteredUsers.value.find(u => getUserId(u) === value)
      if (user) {
        localForm.escalatedToText = `${getUserName(user)} - ${getUserRole(user)}`
      } else {
        localForm.escalatedToText = ''
      }
    }
    updateForm()
  }

  function updateForm() {
    emit("form-update", localForm)
  }

  function goToStep(step) {
    emit("form-update", localForm)
    emit("step-change", step)
  }

  function handleFormSubmit() {
    emit("save-and-proceed", { step: 2, data: localForm })
  }
</script>

<style scoped>
  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }

    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  .animate-fadeIn {
    animation: fadeIn 0.3s ease-in-out;
  }
</style>
<template>
  <div 
    class="max-w-3xl w-full rounded-lg shadow-2xl border max-h-[90vh] flex flex-col"
    :class="isDarkMode 
      ? 'bg-gray-800 border-transparent' 
      : 'bg-white border-transparent'"
  >
    <!-- Header -->
    <div 
      class="px-8 py-5 border-b"
      :class="isDarkMode 
        ? 'border-transparent' 
        : 'border-transparent'"
    >
      <h2 
        class="text-xl font-bold"
        :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
      >
        Edit User
      </h2>
    </div>

    <!-- Scrollable Form Content -->
    <div class="overflow-y-auto px-8 py-6 flex-1">
      <form @submit.prevent="submitForm" class="space-y-5">

        <!-- Username -->
        <div>
          <label 
            class="block mb-2 text-sm font-medium"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            Username *
          </label>
          <input 
            v-model="form.usn" 
            type="text" 
            required 
            class="w-full rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:border-transparent"
            :class="isDarkMode 
              ? 'bg-gray-700 border border-transparent text-gray-100 placeholder-gray-500 focus:ring-blue-500' 
              : 'bg-gray-50 border border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'"
          />
        </div>

        <!-- First Name -->
        <div>
          <label 
            class="block mb-2 text-sm font-medium"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            First Name *
          </label>
          <input 
            v-model="form.fname" 
            type="text" 
            required 
            class="w-full rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:border-transparent"
            :class="isDarkMode 
              ? 'bg-gray-700 border border-transparent text-gray-100 placeholder-gray-500 focus:ring-blue-500' 
              : 'bg-gray-50 border border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'"
          />
        </div>

        <!-- Last Name -->
        <div>
          <label 
            class="block mb-2 text-sm font-medium"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            Last Name *
          </label>
          <input 
            v-model="form.lname" 
            type="text" 
            required 
            class="w-full rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:border-transparent"
            :class="isDarkMode 
              ? 'bg-gray-700 border border-transparent text-gray-100 placeholder-gray-500 focus:ring-blue-500' 
              : 'bg-gray-50 border border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'"
          />
        </div>

        <!-- Role (Dropdown) -->
        <div>
          <label 
            class="block mb-2 text-sm font-medium"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            Role *
          </label>
          <select 
            v-model="form.role" 
            required 
            class="w-full rounded-lg px-4 py-3 focus:outline-none focus:ring-2"
            :class="isDarkMode 
              ? 'bg-gray-700 border border-transparent text-gray-100 focus:ring-blue-500' 
              : 'bg-gray-50 border border-transparent text-gray-900 focus:ring-amber-600'"
          >
            <option disabled value="">Select Role</option>
            <option v-for="r in roles" :key="r.id" :value="r.id">
              {{ r.name }}
            </option>
          </select>
        </div>

        <!-- Phone -->
        <div>
          <label 
            class="block mb-2 text-sm font-medium"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            Phone
          </label>
          <input 
            v-model="form.phone" 
            type="text" 
            class="w-full rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:border-transparent"
            :class="isDarkMode 
              ? 'bg-gray-700 border border-transparent text-gray-100 placeholder-gray-500 focus:ring-blue-500' 
              : 'bg-gray-50 border border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'"
          />
        </div>

        <!-- Email -->
        <div>
          <label 
            class="block mb-2 text-sm font-medium"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            Email
          </label>
          <input 
            v-model="form.email" 
            type="email" 
            class="w-full rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:border-transparent"
            :class="isDarkMode 
              ? 'bg-gray-700 border border-transparent text-gray-100 placeholder-gray-500 focus:ring-blue-500' 
              : 'bg-gray-50 border border-transparent text-gray-900 placeholder-gray-400 focus:ring-amber-600'"
          />
        </div>

        <!-- Is Active -->
        <div class="flex items-center gap-2 pt-2">
          <input 
            type="checkbox" 
            v-model="isActive" 
            class="h-4 w-4 rounded text-blue-600 focus:ring-blue-500"
            :class="isDarkMode 
              ? 'border-transparent bg-gray-700' 
              : 'border-transparent bg-white'"
          />
          <label 
            class="text-sm"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            Active User
          </label>
        </div>
      </form>
    </div>

    <!-- Footer Buttons -->
    <div 
      class="px-8 py-5 border-t flex gap-3"
      :class="isDarkMode 
        ? 'border-transparent' 
        : 'border-transparent'"
    >
      <button
        @click="submitForm"
        class="flex-1 text-white py-3 rounded-lg transition-all duration-200 font-medium flex items-center justify-center gap-2"
        :class="isDarkMode 
          ? 'bg-amber-600 hover:bg-amber-700' 
          : 'bg-amber-700 hover:bg-amber-800'"
      >
        <i-mdi-content-save class="w-5 h-5" />
        Update User
      </button>

      <button
        type="button"
        @click="emit('cancel')"
        class="px-8 py-3 rounded-lg transition-all duration-200 font-medium border"
        :class="isDarkMode 
          ? 'bg-gray-700 hover:bg-gray-600 text-gray-300 border-transparent' 
          : 'bg-gray-200 hover:bg-gray-300 text-gray-700 border-transparent'"
      >
        Cancel
      </button>
    </div>

  </div>
</template>

<script setup>
import { reactive, ref, inject, onMounted } from 'vue'
import { useUserStore } from '@/stores/users'

const props = defineProps({
  user: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(["saved", "cancel"])
const store = useUserStore()

// Inject theme
const isDarkMode = inject('isDarkMode')

const roles = [
  { id: "1", name: "Counsellor" },
  { id: "2", name: "Supervisor" },
  { id: "3", name: "Case Manager" },
  { id: "4", name: "Case Worker" },
  { id: "5", name: "Partner" },
  { id: "6", name: "Media Account" },
  { id: "99", name: "Administrator" },
]

const form = reactive({
  usn: "",
  fname: "",
  lname: "",
  role: "",
  phone: "",
  email: ""
})

const isActive = ref(true)
const userId = ref(null)

const getValue = (key) => {
  if (!store.users_k?.[key]) return null
  return props.user[store.users_k[key][0]]
}

onMounted(() => {
  // Populate form with existing user data
  userId.value = getValue('id')
  form.usn = getValue('usn') || ''
  form.fname = getValue('contact_fname') || ''
  form.lname = getValue('contact_lname') || ''
  form.role = String(getValue('role')) || ''
  form.phone = getValue('contact_phone') || ''
  form.email = getValue('contact_email') || ''
  isActive.value = getValue('is_active') === 1
})

const submitForm = async () => {
  const payload = {
    usn: form.usn,
    fname: form.fname,
    lname: form.lname,
    role: form.role,
    phone: form.phone,
    email: form.email,
    is_active: isActive.value ? 1 : 0,
  }

  await store.editUser(userId.value, payload)
  emit("saved")
}
</script>
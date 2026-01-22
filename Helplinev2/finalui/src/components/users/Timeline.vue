<template>
  <div 
    class="relative border-l-2 pl-6 space-y-6"
    :class="isDarkMode ? 'border-transparent' : 'border-transparent'"
  >

    <div
      v-for="user in store.users"
      :key="getValue(user, 'id')"
      class="relative shadow-xl rounded-lg p-6 border cursor-pointer transition-all duration-200"
      :class="isDarkMode 
        ? 'bg-neutral-900 border-transparent hover:border-amber-600' 
        : 'bg-white border-transparent hover:border-amber-600'"
      @click="selectUser(user)"
    >
      <!-- Timeline Dot -->
      <div 
        class="absolute -left-[1.875rem] top-6 w-6 h-6 rounded-full border-4"
        :class="isDarkMode 
          ? 'bg-amber-600 border-transparent' 
          : 'bg-amber-600 border-transparent'"
      ></div>

      <!-- User Info -->
      <h3 
        class="text-lg font-semibold"
        :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
      >
        {{ getValue(user, 'contact_fname') }} {{ getValue(user, 'contact_lname') }}
      </h3>

      <p 
        class="text-sm mt-1"
        :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
      >
        Username: <span 
          class="font-medium"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          {{ getValue(user, 'usn') }}
        </span>
      </p>

      <p 
        class="text-sm mt-1"
        :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
      >
        Created By: {{ getValue(user, 'created_by') || 'N/A' }}
      </p>

      <p 
        class="text-sm mt-1"
        :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
      >
        Created On: {{ formatDate(getValue(user, 'created_on')) }}
      </p>

      <!-- Role Badge -->
      <span
        class="inline-block mt-3 px-3 py-1 rounded-full text-xs font-medium uppercase border"
        :class="isDarkMode 
          ? 'bg-amber-600/20 text-amber-500 border-amber-600/30' 
          : 'bg-amber-100 text-amber-700 border-amber-300'"
      >
        {{ getRoleName(getValue(user, 'role')) }}
      </span>
    </div>

    <!-- User Details Modal -->
    <Transition name="modal">
      <div 
        v-if="selectedUser"
        class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        @click.self="closeModal"
      >
        <UserDetailsModal
          :user="selectedUser"
          :loading="loadingUser"
          @close="handleClose"
          @edit="handleEdit"
        />
      </div>
    </Transition>

    <!-- Loading overlay for modal -->
    <Transition name="modal">
      <div 
        v-if="loadingUser"
        class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4"
      >
        <div 
          class="rounded-lg shadow-2xl p-8 border"
          :class="isDarkMode 
            ? 'bg-neutral-900 border-transparent' 
            : 'bg-white border-transparent'"
        >
          <div class="flex flex-col items-center gap-4">
            <div 
              class="w-12 h-12 border-4 rounded-full animate-spin"
              :class="isDarkMode 
                ? 'border-transparent border-t-amber-500' 
                : 'border-transparent border-t-amber-700'"
            ></div>
            <p 
              class="text-sm font-medium"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
            >
              Loading user details...
            </p>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import { toast } from 'vue-sonner'
import { useUserStore } from "@/stores/users"
import UserDetailsModal from './UserDetailsModal.vue'

const emit = defineEmits(['refresh', 'edit'])

const store = useUserStore()
const isDarkMode = inject('isDarkMode')
const selectedUser = ref(null)
const loadingUser = ref(false)

const roleMap = {
  "1": "Counsellor",
  "2": "Supervisor",
  "3": "Case Manager",
  "4": "Case Worker",
  "5": "Partner",
  "6": "Media Account",
  "99": "Administrator"
}

const getValue = (userItem, key) => {
  if (!store.users_k?.[key]) return null
  return userItem[store.users_k[key][0]]
}

const getRoleName = (roleId) => {
  return roleMap[String(roleId)] || roleId || 'N/A'
}

const formatDate = (timestamp) => {
  if (!timestamp) return 'N/A'
  const date = new Date(parseInt(timestamp) * 1000)
  return date.toLocaleString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: true
  })
}

const selectUser = async (user) => {
  const userId = getValue(user, 'id')
  
  if (!userId) {
    toast.error('User ID not found')
    return
  }

  loadingUser.value = true
  selectedUser.value = null

  try {
    const userData = await store.viewUser(userId)
    console.log('Fetched user data:', userData)
    
    // The API returns the user in the same array format
    if (userData.users && userData.users.length > 0) {
      selectedUser.value = userData.users[0]
    } else {
      toast.error('User data not found')
    }
  } catch (error) {
    console.error('Error fetching user:', error)
    toast.error('Failed to load user details')
  } finally {
    loadingUser.value = false
  }
}

const closeModal = () => {
  selectedUser.value = null
  loadingUser.value = false
}

const handleEdit = (user) => {
  selectedUser.value = null
  emit('edit', user)
}

const handleClose = (shouldRefresh = false) => {
  selectedUser.value = null
  if (shouldRefresh) {
    emit('refresh')
  }
}
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style>
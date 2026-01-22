<template>
  <div 
    class="max-w-2xl w-full rounded-xl shadow-2xl border overflow-hidden"
    :class="isDarkMode 
      ? 'bg-gray-800 border-transparent' 
      : 'bg-white border-transparent'"
  >
    <!-- Header -->
    <div 
      class="px-8 py-5 border-b flex items-center justify-between"
      :class="isDarkMode 
        ? 'border-transparent bg-gray-900/50' 
        : 'border-transparent bg-gray-50'"
    >
      <div class="flex items-center gap-3">
        <div 
          class="w-12 h-12 rounded-full flex items-center justify-center text-lg font-bold"
          :class="isDarkMode 
            ? 'bg-amber-600 text-white' 
            : 'bg-amber-600 text-white'"
        >
          {{ getUserInitials() }}
        </div>
        <div>
          <h2 
            class="text-xl font-bold"
            :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
          >
            {{ getValue('contact_fname') }} {{ getValue('contact_lname') }}
          </h2>
          <p 
            class="text-sm"
            :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
          >
            @{{ getValue('usn') }}
          </p>
        </div>
      </div>
      
      <button
        type="button"
       @click="$emit('close', false)" 
        class="p-2 rounded-xl transition-colors duration-200"
        :class="isDarkMode 
          ? 'hover:bg-gray-700 text-gray-400 hover:text-gray-200' 
          : 'hover:bg-gray-200 text-gray-600 hover:text-gray-900'"
      >
        <i-mdi-close class="w-6 h-6" />
      </button>
    </div>

    <!-- Password Reset Success Message -->
    <Transition name="slide-down">
      <div 
        v-if="resetSuccess && newPassword"
        class="px-8 py-4 border-b"
        :class="isDarkMode 
          ? 'bg-green-900/30 border-transparent' 
          : 'bg-green-50 border-green-200'"
      >
        <div class="flex items-start gap-3">
          <div 
            class="mt-0.5 p-2 rounded-full"
            :class="isDarkMode 
              ? 'bg-green-600/20' 
              : 'bg-green-100'"
          >
            <i-mdi-check-circle 
              class="w-6 h-6"
              :class="isDarkMode ? 'text-green-400' : 'text-green-600'"
            />
          </div>
          <div class="flex-1">
            <h3 
              class="font-semibold mb-1"
              :class="isDarkMode ? 'text-green-400' : 'text-green-700'"
            >
              Password Reset Successful!
            </h3>
            <p 
              class="text-sm mb-3"
              :class="isDarkMode ? 'text-green-300' : 'text-green-600'"
            >
              {{ resetMessage }}
            </p>
            
            <!-- New Password Display -->
            <div 
              class="rounded-xl p-4 border"
              :class="isDarkMode 
                ? 'bg-gray-800 border-transparent' 
                : 'bg-white border-green-300'"
            >
              <label 
                class="block text-xs font-semibold uppercase tracking-wider mb-2"
                :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
              >
                New Temporary Password
              </label>
              <div class="flex items-center justify-between gap-3">
                <code 
                  class="text-2xl font-mono font-bold tracking-wider"
                  :class="isDarkMode ? 'text-green-400' : 'text-green-700'"
                >
                  {{ newPassword }}
                </code>
                <button
                  type="button"
                  @click="copyPassword"
                  class="px-4 py-2 rounded-xl transition-all duration-200 flex items-center gap-2 text-sm font-medium"
                  :class="passwordCopied
                    ? (isDarkMode 
                      ? 'bg-green-600 text-white' 
                      : 'bg-green-600 text-white')
                    : (isDarkMode 
                      ? 'bg-gray-700 text-gray-300 hover:bg-gray-600' 
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300')"
                >
                  <i-mdi-check v-if="passwordCopied" class="w-4 h-4" />
                  <i-mdi-content-copy v-else class="w-4 h-4" />
                  {{ passwordCopied ? 'Copied!' : 'Copy' }}
                </button>
              </div>
            </div>

            <p 
              class="text-xs mt-3"
              :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
            >
              ⚠️ Make sure to save this password. The user will need to change it on first login.
            </p>
          </div>
        </div>
      </div>
    </Transition>

    <!-- User Details -->
    <div 
      class="px-8 py-6 space-y-4"
      :class="isDarkMode ? 'bg-gray-800' : 'bg-white'"
    >
      <!-- Role Badge -->
      <div>
        <label 
          class="text-xs font-semibold uppercase tracking-wider mb-2 block"
          :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
        >
          Role
        </label>
        <span
          class="inline-block px-4 py-2 rounded-full text-sm font-medium uppercase border"
          :class="isDarkMode 
            ? 'bg-amber-600/20 text-amber-500 border-amber-600/30' 
            : 'bg-amber-100 text-amber-700 border-amber-300'"
        >
          {{ getRoleName(getValue('role')) }}
        </span>
      </div>

      <!-- Contact Information -->
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label 
            class="text-xs font-semibold uppercase tracking-wider mb-1 block"
            :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
          >
            Phone
          </label>
          <p 
            class="text-sm"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            {{ getValue('contact_phone') || 'N/A' }}
          </p>
        </div>

        <div>
          <label 
            class="text-xs font-semibold uppercase tracking-wider mb-1 block"
            :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
          >
            Email
          </label>
          <p 
            class="text-sm"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            {{ getValue('contact_email') || 'N/A' }}
          </p>
        </div>
      </div>

      <!-- User ID -->
      <div>
        <label 
          class="text-xs font-semibold uppercase tracking-wider mb-1 block"
          :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
        >
          User ID
        </label>
        <p 
          class="text-sm font-mono"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          {{ getValue('id') }}
        </p>
      </div>

      <!-- Created Information -->
      <div class="grid grid-cols-2 gap-4 pt-4 border-t"
        :class="isDarkMode ? 'border-transparent' : 'border-transparent'"
      >
        <div>
          <label 
            class="text-xs font-semibold uppercase tracking-wider mb-1 block"
            :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
          >
            Created On
          </label>
          <p 
            class="text-sm"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            {{ formatDate(getValue('created_on')) }}
          </p>
        </div>

        <div>
          <label 
            class="text-xs font-semibold uppercase tracking-wider mb-1 block"
            :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
          >
            Created By
          </label>
          <p 
            class="text-sm"
            :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
          >
            {{ getValue('created_by') || 'N/A' }}
          </p>
        </div>
      </div>

      <!-- Status -->
<div class="pt-2">
  <label 
    class="text-xs font-semibold uppercase tracking-wider mb-1 block"
    :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
  >
    Status
  </label>
  <div class="flex items-center gap-2">
    <div 
      class="w-2 h-2 rounded-full"
      :class="getValue('is_active') === '1' 
        ? 'bg-green-500' 
        : 'bg-red-500'"
    ></div>
    <span 
      class="text-sm font-medium"
      :class="getValue('is_active') === '1' 
        ? (isDarkMode ? 'text-green-400' : 'text-green-600')
        : (isDarkMode ? 'text-red-400' : 'text-red-600')"
    >
      {{ getValue('is_active') === '1' ? 'Active' : 'Inactive' }}
    </span>
  </div>
</div>
    </div>

    <!-- Action Buttons -->
    <div 
      class="px-8 py-5 border-t flex gap-3"
      :class="isDarkMode 
        ? 'border-transparent bg-gray-900/30' 
        : 'border-transparent bg-gray-50'"
    >
      <!-- Show different buttons based on reset state -->
      <template v-if="resetSuccess && newPassword">
        <!-- After successful reset, show Done button -->
        <button
          type="button"
          @click="handleDone"
          class="flex-1 py-3 rounded-xl transition-all duration-200 font-medium flex items-center justify-center gap-2 border"
          :class="isDarkMode 
            ? 'bg-green-600 hover:bg-green-700 text-white border-green-600' 
            : 'bg-green-600 hover:bg-green-700 text-white border-green-600'"
        >
          <i-mdi-check class="w-5 h-5" />
          Done
        </button>
      </template>
      
      <template v-else>
        <!-- Normal state buttons -->
        <button
          type="button"
          @click="handleEdit"
          class="flex-1 py-3 rounded-xl transition-all duration-200 font-medium flex items-center justify-center gap-2 border"
          :class="isDarkMode 
            ? 'bg-amber-600 hover:bg-amber-700 text-white border-amber-600' 
            : 'bg-amber-700 hover:bg-amber-800 text-white border-amber-700'"
        >
          <i-mdi-pencil class="w-5 h-5" />
          Edit User
        </button>

        <button
  type="button"
  @click.prevent.stop="handleResetPassword"
  :disabled="resetting"
  class="flex-1 py-3 rounded-xl transition-all duration-200 font-medium flex items-center justify-center gap-2 border disabled:opacity-50 disabled:cursor-not-allowed"
  :class="isDarkMode 
    ? 'bg-orange-600 hover:bg-orange-700 text-white border-orange-600' 
    : 'bg-orange-500 hover:bg-orange-600 text-white border-orange-500'"
>
  <i-mdi-lock-reset v-if="!resetting" class="w-5 h-5" />
  <svg v-else class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
  </svg>
  {{ resetting ? 'Resetting...' : 'Reset Password' }}
</button>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import { toast } from 'vue-sonner'
import { useUserStore } from '@/stores/users'

const props = defineProps({
  user: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['close', 'edit', 'refresh'])

const store = useUserStore()
const isDarkMode = inject('isDarkMode')
const resetting = ref(false)
const resetSuccess = ref(false)
const newPassword = ref('')
const resetMessage = ref('')
const passwordCopied = ref(false)

const roleMap = {
  "1": "Counsellor",
  "2": "Supervisor",
  "3": "Case Manager",
  "4": "Case Worker",
  "5": "Partner",
  "6": "Media Account",
  "99": "Administrator"
}

const getValue = (key) => {
  if (!store.users_k?.[key]) return null
  return props.user[store.users_k[key][0]]
}

const getRoleName = (roleId) => {
  return roleMap[String(roleId)] || roleId || 'N/A'
}

const formatDate = (timestamp) => {
  if (!timestamp) return 'N/A'
  const ms = timestamp < 10000000000 ? timestamp * 1000 : timestamp * 3600 * 1000
  return new Date(ms).toLocaleString()
}

const getUserInitials = () => {
  const fname = getValue('contact_fname') || ''
  const lname = getValue('contact_lname') || ''
  return `${fname.charAt(0)}${lname.charAt(0)}`.toUpperCase() || 'U'
}

const handleEdit = () => {
  emit('edit', props.user)
}

const copyPassword = async () => {
  try {
    await navigator.clipboard.writeText(newPassword.value)
    passwordCopied.value = true
    toast.success('Password copied to clipboard!')
    
    setTimeout(() => {
      passwordCopied.value = false
    }, 3000)
  } catch (err) {
    console.error('Failed to copy password:', err)
    toast.error('Failed to copy password')
  }
}

const handleResetPassword = async () => {
  const userId = getValue('id')
  const username = getValue('usn')
  
  if (!userId) {
    toast.error('User ID not found')
    return
  }

  // Confirm before resetting
  if (!confirm(`Are you sure you want to reset the password for user "${username}"?`)) {
    return
  }

  console.log('🔄 Starting password reset...')
  resetting.value = true
  resetSuccess.value = false
  newPassword.value = ''
  resetMessage.value = ''

  try {
    const result = await store.resetPassword(userId)
    console.log('✅ Password reset result:', result)
    
    // Extract the password from the response
    if (result.data?.auth_nb && Array.isArray(result.data.auth_nb)) {
      const messageArray = result.data.auth_nb[0]
      if (Array.isArray(messageArray) && messageArray.length >= 2) {
        const fullMessage = messageArray[1]
        resetMessage.value = fullMessage
        
        const passwordMatch = fullMessage.match(/password is (\d+)/)
        if (passwordMatch && passwordMatch[1]) {
          newPassword.value = passwordMatch[1]
          resetSuccess.value = true
          console.log('✅ Password extracted:', newPassword.value)
          
          // Show the password in a long-duration toast
          toast.success(fullMessage, {
            duration: 15000, // Show for 15 seconds
            description: `Username: ${username}`,
            closeButton: true,
          })
        } else {
          toast.warning('Password reset completed but password not found in response')
        }
      }
    } else if (result.status === 202 || result.status === 200) {
      resetSuccess.value = true
      resetMessage.value = 'Password has been reset successfully'
      toast.success(`Password reset successful for ${username}!`, {
        duration: 10000,
        closeButton: true,
      })
    } else {
      toast.warning('Password reset completed with unexpected response')
    }
  } catch (error) {
    console.error('❌ Password reset error:', error)
    toast.error(`Failed to reset password: ${error.message}`)
  } finally {
    resetting.value = false
    console.log('✅ Password reset complete')
  }
}

const handleDone = () => {
  // Reset the success state
  resetSuccess.value = false
  newPassword.value = ''
  resetMessage.value = ''
  
  // Close modal and trigger refresh
  emit('close', true) // ← Pass true to indicate refresh is needed
}
</script>

<style scoped>
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  opacity: 0;
  transform: translateY(-20px);
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>
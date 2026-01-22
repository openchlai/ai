<template>
  <!-- Backdrop -->
  <div 
    class="fixed inset-0 bg-black/50 z-40 transition-opacity duration-300"
    @click="$emit('close')"
  ></div>

  <!-- Chat Panel Slide-out -->
  <div 
    class="fixed right-0 top-0 h-full w-full md:w-[500px] shadow-2xl z-50 flex flex-col border-l animate-slide-in"
    :class="isDarkMode 
      ? 'bg-black border-transparent' 
      : 'bg-white border-transparent'"
  >
    <!-- Header -->
    <div 
      class="flex items-center justify-between p-4 border-b"
      :class="isDarkMode 
        ? 'bg-neutral-900 border-transparent' 
        : 'bg-gray-50 border-transparent'"
    >
      <div class="flex items-center gap-3">
        <div
          class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold text-sm"
          :style="{ background: getAvatarColor(getContactName()) }"
        >
          {{ getContactName().charAt(0).toUpperCase() }}
        </div>
        <div>
          <h3 
            class="font-semibold"
            :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
          >
            {{ getContactName() }}
          </h3>
          <p 
            class="text-xs"
            :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
          >
            {{ getPlatform() }}
          </p>
        </div>
      </div>
      <button 
        @click="$emit('close')"
        class="p-2 rounded-lg transition-all"
        :class="isDarkMode 
          ? 'hover:bg-neutral-800 text-gray-400' 
          : 'hover:bg-gray-200'"
      >
        <i-mdi-close 
          class="w-6 h-6"
          :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
        />
      </button>
    </div>

    <!-- Message History -->
    <div 
      class="flex-1 overflow-y-auto p-4 space-y-4"
      :class="isDarkMode ? 'bg-black' : 'bg-gray-50'"
    >
      <!-- Received Message -->
      <div class="flex gap-3">
        <div
          class="w-8 h-8 rounded-full flex items-center justify-center text-white font-semibold text-xs flex-shrink-0"
          :style="{ background: getAvatarColor(getContactName()) }"
        >
          {{ getContactName().charAt(0).toUpperCase() }}
        </div>
        <div class="flex-1">
          <div 
            class="rounded-lg rounded-tl-none p-3 border"
            :class="isDarkMode 
              ? 'bg-neutral-900 border-transparent' 
              : 'bg-white border-transparent'"
          >
            <p 
              class="text-sm"
              :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'"
            >
              {{ getMessageContent() }}
            </p>
          </div>
          <p 
            class="text-xs mt-1"
            :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
          >
            {{ getMessageTime() }}
          </p>
        </div>
      </div>

      <!-- Add more messages here as needed -->
    </div>

    <!-- Message Input -->
    <MessageInput 
      v-model="newMessage"
      @send-message="handleSendMessage"
    />
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import { useMessagesStore } from '@/stores/messages'
import MessageInput from './MessageInput.vue'

const props = defineProps({
  selectedMessage: {
    type: [Object, Array],
    default: null
  },
  newMessage: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['close', 'sendMessage'])

const messagesStore = useMessagesStore()
const newMessage = ref(props.newMessage)

// Inject theme
const isDarkMode = inject('isDarkMode')

const getValue = (key) => {
  if (!props.selectedMessage || !messagesStore.pmessages_k?.[key]) return null
  const index = messagesStore.pmessages_k[key][0]
  return props.selectedMessage[index]
}

const getContactName = () => {
  return getValue('created_by') || 'Unknown Contact'
}

const getPlatform = () => {
  return getValue('src') || 'Unknown Platform'
}

const getMessageContent = () => {
  return getValue('src_msg') || 'No message content'
}

const getMessageTime = () => {
  const timestamp = getValue('dth')
  if (!timestamp) return 'N/A'
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('en-US', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getAvatarColor = (name) => {
  const colors = isDarkMode.value 
    ? ['#F59E0B', '#10B981', '#EF4444', '#8B5CF6', '#EC4899']
    : ['#B45309', '#059669', '#DC2626', '#7C3AED', '#DB2777']
  const index = name?.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) || 0
  return colors[index % colors.length]
}

const handleSendMessage = (message) => {
  emit('sendMessage', message)
  newMessage.value = ''
}
</script>

<style scoped>
@keyframes slideIn {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

.animate-slide-in {
  animation: slideIn 0.3s ease-out;
}
</style>
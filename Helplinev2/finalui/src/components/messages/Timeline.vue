<template>
  <div class="space-y-6">
    <div 
      v-if="Object.keys(groupedMessagesByDate).length === 0" 
      class="text-center py-12 rounded-lg shadow-xl border"
      :class="isDarkMode 
        ? 'bg-neutral-900 border-transparent' 
        : 'bg-white border-transparent'"
    >
      <p 
        :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
      >
        No chats to display
      </p>
    </div>

    <div
      v-for="(group, label) in groupedMessagesByDate"
      :key="label"
      class="space-y-3"
    >
      <h2 
        class="text-base font-semibold uppercase tracking-wide"
        :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
      >
        {{ label }}
      </h2>

      <div class="space-y-2">
        <div
          v-for="message in group"
          :key="getValue(message, 'id')"
          :class="[
            'rounded-lg p-4 shadow-xl border transition-all duration-200 cursor-pointer',
            selectedMessageId === getValue(message, 'id') 
              ? isDarkMode
                ? 'ring-2 ring-amber-600 border-amber-600 bg-amber-600/10' 
                : 'ring-2 ring-amber-600 border-amber-600 bg-amber-100'
              : isDarkMode
                ? 'bg-neutral-900 border-transparent hover:border-amber-600/50 hover:shadow-2xl'
                : 'bg-white border-transparent hover:border-amber-600/50 hover:shadow-2xl'
          ]"
          @click="openChatPanel(message)"
        >
          <div class="flex items-start gap-3">
            <!-- Avatar -->
            <div
              class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0 text-sm"
              :style="{ background: getAvatarColor(getValue(message, 'created_by') || '') }"
            >
              {{ (getValue(message, 'created_by') || '?').charAt(0).toUpperCase() }}
            </div>

            <!-- Content -->
            <div class="flex-1 min-w-0">
              <div class="flex justify-between items-baseline mb-1">
                <span 
                  class="text-sm font-medium"
                  :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'"
                >
                  {{ getValue(message, 'created_by') || 'Unknown' }}
                </span>
                <span 
                  class="text-xs ml-2"
                  :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'"
                >
                  {{ formatTime(getValue(message, 'dth')) }}
                </span>
              </div>

              <div class="flex gap-2 mb-2">
                <span 
                  class="px-2 py-0.5 rounded-full text-xs font-medium uppercase border"
                  :class="isDarkMode 
                    ? 'bg-amber-600/20 text-amber-500 border-amber-600/30' 
                    : 'bg-amber-100 text-amber-700 border-amber-300'"
                >
                  {{ getValue(message, 'src') || 'Chat' }}
                </span>
                <span 
                  class="px-2 py-0.5 rounded-full text-xs font-medium uppercase border"
                  :class="isDarkMode 
                    ? 'bg-green-600/20 text-green-400 border-green-600/30' 
                    : 'bg-green-100 text-green-700 border-green-300'"
                >
                  {{ getValue(message, 'src_status') || 'Active' }}
                </span>
              </div>

              <p 
                class="text-sm truncate"
                :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
              >
                {{ getValue(message, 'src_msg') || '' }}
              </p>
            </div>

            <!-- Chat Action Button -->
            <button 
              @click.stop="openChatPanel(message)" 
              class="p-2 rounded transition-all duration-200 flex-shrink-0 text-white active:scale-95"
              :class="isDarkMode 
                ? 'bg-amber-600 hover:bg-amber-700' 
                : 'bg-amber-700 hover:bg-amber-800'"
              title="Open Chat"
            >
              <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z" />
                <path d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { inject } from 'vue'
import { useMessagesStore } from '@/stores/messages'

const props = defineProps({
  groupedMessagesByDate: {
    type: Object,
    default: () => ({})
  },
  selectedMessageId: [String, Number]
})

const emit = defineEmits(['openChat'])

const messagesStore = useMessagesStore()

// Inject theme
const isDarkMode = inject('isDarkMode')

const getValue = (message, key) => {
  if (!messagesStore.pmessages_k?.[key]) return null
  const index = messagesStore.pmessages_k[key][0]
  return message[index]
}

const formatTime = (timestamp) => {
  if (!timestamp) return 'N/A'
  const date = new Date(timestamp * 1000)
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

const openChatPanel = (message) => {
  emit('openChat', message)
}

const getAvatarColor = (name) => {
  const colors = isDarkMode.value 
    ? ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']
    : ['#B45309', '#059669', '#DC2626', '#7C3AED', '#DB2777']
  const index = name?.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) || 0
  return colors[index % colors.length]
}
</script>
<template>
  <div 
    class="p-6 min-h-screen"
    :class="isDarkMode ? 'bg-black' : 'bg-gray-50'"
  >
    <!-- Page Header -->
    <div class="mb-6">
      <h1 
        class="text-3xl font-bold flex items-center gap-3"
        :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'"
      >
        <i-mdi-message-text-outline 
          class="w-8 h-8"
          :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
        />
        Chats
      </h1>
      <p 
        class="mt-2"
        :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
      >
        Manage conversations and communications across all channels
      </p>
    </div>

    <!-- Channel Filter Pills -->
    <Filter 
      :channelFilters="channelFilters" 
      :activePlatform="activePlatform" 
      @update:activePlatform="handlePlatformChange"
    />


    <!-- Loading State -->
    <div 
      v-if="messagesStore.loading" 
      class="text-center py-12 rounded-lg shadow-xl border"
      :class="isDarkMode 
        ? 'bg-gray-800 border-transparent' 
        : 'bg-white border-transparent'"
    >
      <div 
        :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
      >
        Loading messages...
      </div>
    </div>

    <!-- Content -->
    <template v-else>
      <!-- View Buttons and Total Count -->
      <div class="flex justify-between items-center mb-6">
        <!-- Total Count -->
        <div 
          class="flex items-center gap-2"
          :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'"
        >
          <i-mdi-message-text-outline 
            class="w-5 h-5"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
          />
          <span class="text-sm">Total Messages:</span>
          <span 
            class="text-lg font-bold"
            :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'"
          >
            {{ messagesStore.messageCount }}
          </span>
        </div>

        <!-- View Toggle Buttons -->
        <div class="flex gap-3">
          <button 
            :class="getViewButtonClass(activeView === 'timeline')" 
            @click="activeView='timeline'"
          >
            <i-mdi-timeline-text-outline class="w-5 h-5" />
            Timeline
          </button>
          <button 
            :class="getViewButtonClass(activeView === 'table')" 
            @click="activeView='table'"
          >
            <i-mdi-table class="w-5 h-5" />
            Table
          </button>
          <button 
            @click="refreshMessages"
            :disabled="messagesStore.loading"
            class="px-5 py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 text-sm border disabled:opacity-50 disabled:cursor-not-allowed"
            :class="isDarkMode 
              ? 'bg-gray-800 text-gray-300 border-transparent hover:border-green-500 hover:text-green-400' 
              : 'bg-white text-gray-700 border-transparent hover:border-green-600 hover:text-green-700'"
          >
            <i-mdi-refresh class="w-5 h-5" />
            Refresh
          </button>
        </div>
      </div>

      <!-- Views -->
      <Timeline
        v-if="activeView==='timeline'" 
        :groupedMessagesByDate="groupedMessagesByDate" 
        :selectedMessageId="selectedMessageId"
        @openChat="openChatPanel"
      />
      <Table
        v-else
        :messages="messagesStore.pmessages"
        :selectedMessageId="selectedMessageId"
        @openChat="openChatPanel"
      />
    </template>

    <!-- Chat Panel -->
    <ChatPanel
      v-if="showChatPanel"
      :selectedMessage="selectedMessage"
      :newMessage="newMessage"
      @close="closeChatPanel"
      @sendMessage="sendMessage"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import { toast } from 'vue-sonner'
import Filter from '@/components/messages/Filter.vue'
import Timeline from '@/components/messages/Timeline.vue'
import Table from '@/components/messages/Table.vue'
import ChatPanel from '@/components/messages/ChatPanel.vue'

import { useMessagesStore } from '@/stores/messages'

const messagesStore = useMessagesStore()

// Inject theme
const isDarkMode = inject('isDarkMode')

// Dynamic button class for view toggle
const getViewButtonClass = (isActive) => {
  const baseClasses = 'px-5 py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 text-sm'
  
  if (isActive) {
    return isDarkMode.value
      ? `${baseClasses} bg-amber-600 text-white shadow-lg shadow-amber-900/50`
      : `${baseClasses} bg-amber-700 text-white shadow-lg shadow-amber-900/30`
  } else {
    return isDarkMode.value
      ? `${baseClasses} bg-gray-800 text-gray-300 border border-transparent hover:border-amber-500 hover:text-amber-500`
      : `${baseClasses} bg-white text-gray-700 border border-transparent hover:border-amber-600 hover:text-amber-700`
  }
}

const channelFilters = ref([
  { id: "all", name: "All", icon: "i-mdi-apps" },
  { id: "whatsapp", name: "WhatsApp", icon: "i-mdi-whatsapp" },
  { id: "safepal", name: "SafePal", icon: "i-mdi-shield-check" },
  { id: "email", name: "Email", icon: "i-mdi-email-outline" },
  { id: "walkin", name: "Walk-In", icon: "i-mdi-walk" },
  { id: "ai", name: "AI", icon: "i-mdi-robot-outline" },
  { id: "call", name: "Call", icon: "i-mdi-phone-outline" }
])

const activePlatform = ref("all")
const activeView = ref("timeline")
const showChatPanel = ref(false)
const selectedMessage = ref(null)
const selectedMessageId = ref(null)
const newMessage = ref("")

// Group messages by date for timeline view
const groupedMessagesByDate = computed(() => {
  const groups = {}
  const today = new Date()
  const yesterday = new Date(today)
  yesterday.setDate(today.getDate() - 1)

  const messages = messagesStore.pmessages || []
  const dthIndex = messagesStore.pmessages_k?.dth?.[0]
  
  if (dthIndex === undefined) return groups

  for (const msg of messages) {
    const timestamp = msg[dthIndex]
    if (!timestamp) continue
    
    const date = new Date(timestamp * 1000)
    let label = date.toDateString() === today.toDateString() 
      ? 'Today' 
      : date.toDateString() === yesterday.toDateString() 
        ? 'Yesterday' 
        : date.toLocaleDateString()
    
    if (!groups[label]) groups[label] = []
    groups[label].push(msg)
  }
  return groups
})

// Handle platform change from pills
function handlePlatformChange(platformId) {
  activePlatform.value = platformId
  
  console.log('Platform changed to:', platformId)
  
  try {
    if (platformId === 'all') {
      messagesStore.fetchAllMessages()
    } else {
      messagesStore.fetchMessagesBySource(platformId)
    }
    
    setTimeout(() => {
      console.log('Messages after filter:', messagesStore.pmessages?.length || 0)
      console.log('Messages_k:', messagesStore.pmessages_k)
    }, 500)
  } catch (err) {
    console.error('Error filtering messages:', err)
    toast.error('Failed to filter messages. Please try again.')
  }
}

// Refresh messages
async function refreshMessages() {
  try {
    if (activePlatform.value === 'all') {
      await messagesStore.fetchAllMessages()
    } else {
      await messagesStore.fetchMessagesBySource(activePlatform.value)
    }
    toast.success('Messages refreshed successfully!')
  } catch (err) {
    console.error('Error refreshing messages:', err)
    toast.error('Failed to refresh messages. Please try again.')
  }
}

const openChatPanel = (msg) => {
  selectedMessage.value = msg
  const idIndex = messagesStore.pmessages_k?.id?.[0]
  selectedMessageId.value = idIndex !== undefined ? msg[idIndex] : null
  showChatPanel.value = true
}

const closeChatPanel = () => {
  showChatPanel.value = false
  selectedMessage.value = null
  selectedMessageId.value = null
  newMessage.value = ''
}

const sendMessage = (msg) => {
  console.log("Send message:", msg)
  newMessage.value = ''
}

onMounted(async () => {
  try {
    await messagesStore.fetchAllMessages()
  } catch (err) {
    console.log('Failed to fetch messages:', err)
    toast.error('Failed to load messages. Please try again.')
  }
})
</script>
<template>
<<<<<<< HEAD
  <div class="space-y-6">
=======
  <div 
    class="space-y-6"
  >
>>>>>>> main

    <!-- Channel Filter Pills -->
    <Filter :channelFilters="channelFilters" :activePlatform="activePlatform"
      @update:activePlatform="handlePlatformChange" />


    <!-- Loading State -->
<<<<<<< HEAD
    <div v-if="messagesStore.loading" class="text-center py-12 rounded-lg shadow-xl border" :class="isDarkMode
      ? 'bg-black border-transparent'
      : 'bg-white border-transparent'">
      <div :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'">
=======
    <div 
      v-if="messagesStore.loading" 
      class="text-center py-12 rounded-lg shadow-xl border"
      :class="isDarkMode 
        ? 'bg-black border-transparent' 
        : 'bg-white border-transparent'"
    >
      <div 
        :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
      >
>>>>>>> main
        Loading messages...
      </div>
    </div>

    <!-- Content -->
    <template v-else>
      <!-- View Buttons and Total Count -->
      <div class="flex flex-col md:flex-row justify-between items-center mb-6 gap-4">
        <!-- Total Count with Pagination Info -->
        <div class="flex items-center gap-2" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
          <i-mdi-message-text-outline class="w-5 h-5" :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'" />
          <span class="text-sm">
            Showing {{ messagesStore.paginationInfo.rangeStart }} - {{ messagesStore.paginationInfo.rangeEnd }} of
          </span>
          <span class="text-lg font-bold" :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'">
            {{ messagesStore.paginationInfo.total }}
          </span>
          <span class="text-sm">messages</span>
        </div>

<<<<<<< HEAD
        <!-- Search and Actions Toolbar -->
        <div class="flex flex-col md:flex-row gap-3 w-full md:w-auto items-stretch md:items-center">
          <!-- Search Input -->
          <div class="relative group w-full md:w-auto z-10">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <i-mdi-magnify class="w-5 h-5 text-gray-400 group-focus-within:text-amber-500 transition-colors" />
            </div>
            <input type="text" v-model="searchQuery" placeholder="Search messages..." 
              class="block w-full md:w-64 pl-10 pr-10 py-2.5 rounded-lg text-sm border focus:ring-2 focus:ring-amber-500/20 focus:border-amber-500 transition-all outline-none shadow-sm"
              :class="isDarkMode 
                ? 'bg-black border-gray-800 text-gray-200 placeholder-gray-600' 
                : 'bg-white border-gray-200 text-gray-900 placeholder-gray-400'" />
            <!-- Clear Search -->
            <button v-if="searchQuery" @click="searchQuery = ''" 
              class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 cursor-pointer">
               <i-mdi-close-circle class="w-4 h-4" />
            </button>
          </div>

          <!-- View Toggle Buttons -->
          <div class="flex gap-2 w-full md:w-auto">
            <button :class="getViewButtonClass(activeView === 'timeline')" @click="activeView = 'timeline'" title="Timeline View" class="flex-1 md:flex-none justify-center">
              <i-mdi-timeline-text-outline class="w-5 h-5" />
              <span class="hidden sm:inline">Timeline</span>
            </button>
            <button :class="getViewButtonClass(activeView === 'table')" @click="activeView = 'table'" title="Table View" class="flex-1 md:flex-none justify-center">
              <i-mdi-table class="w-5 h-5" />
              <span class="hidden sm:inline">Table</span>
            </button>
            <button @click="refreshMessages" :disabled="messagesStore.loading"
              class="px-5 py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center justify-center gap-2 text-sm border disabled:opacity-50 disabled:cursor-not-allowed w-full md:w-auto"
              :class="isDarkMode
                ? 'bg-black text-gray-300 border-transparent hover:border-green-500 hover:text-green-400'
                : 'bg-white text-gray-700 border-transparent hover:border-green-600 hover:text-green-700'"
               title="Refresh Messages">
              <i-mdi-refresh class="w-5 h-5" />
            </button>
          </div>
=======
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
              ? 'bg-black text-gray-300 border-transparent hover:border-green-500 hover:text-green-400' 
              : 'bg-white text-gray-700 border-transparent hover:border-green-600 hover:text-green-700'"
          >
            <i-mdi-refresh class="w-5 h-5" />
            Refresh
          </button>
>>>>>>> main
        </div>
      </div>

      <!-- Views -->
      <MessagesTimeline v-if="activeView === 'timeline'" :groupedMessagesByDate="groupedMessagesByDate"
        :selectedMessageId="selectedMessageId" @openChat="openChatPanel" />
      <MessagesTable v-else :messages="filteredTableMessages" :selectedMessageId="selectedMessageId"
        @openChat="openChatPanel" />

      <!-- Pagination Controls -->
      <Pagination :paginationInfo="messagesStore.paginationInfo" :hasNextPage="messagesStore.hasNextPage"
        :hasPrevPage="messagesStore.hasPrevPage" :loading="messagesStore.loading" :pageSize="selectedPageSize"
        @prev="goToPrevPage" @next="goToNextPage" @goToPage="goToPage" @changePageSize="changePageSize" />
    </template>

    <!-- Chat & AI Panels -->
    <template v-if="showChatPanel">
      <AIPredictionPanel v-if="selectedMessage?.platform === 'gateway' || getValue(selectedMessage, 'src') === 'gateway'" :msg="selectedMessage"
        :pmessages_k="messagesStore.pmessages_k" @close="closeChatPanel" />
      <ChatPanel v-else :selectedMessage="selectedMessage" :newMessage="newMessage" @close="closeChatPanel"
        @sendMessage="sendMessage" />
    </template>
  </div>
</template>

<script setup>
  import { ref, computed, onMounted, inject } from 'vue'
  import { toast } from 'vue-sonner'
  import Filter from '@/components/messages/Filter.vue'
  import MessagesTimeline from '@/components/messages/MessagesTimeline.vue'
  import MessagesTable from '@/components/messages/MessagesTable.vue'
  import ChatPanel from '@/components/messages/ChatPanel.vue'
  import AIPredictionPanel from '@/components/messages/AIPredictionPanel.vue'
  import Pagination from '@/components/base/Pagination.vue'

  import { useMessagesStore } from '@/stores/messages'

  const messagesStore = useMessagesStore()

  // Inject theme
  const isDarkMode = inject('isDarkMode')

<<<<<<< HEAD
  // Dynamic button class for view toggle
  const getViewButtonClass = (isActive) => {
    const baseClasses = 'px-5 py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 text-sm'

    if (isActive) {
      return isDarkMode.value
        ? `${baseClasses} bg-amber-600 text-white shadow-lg shadow-amber-900/50`
        : `${baseClasses} bg-amber-700 text-white shadow-lg shadow-amber-900/30`
    } else {
      return isDarkMode.value
        ? `${baseClasses} bg-black text-gray-300 border border-transparent hover:border-amber-500 hover:text-amber-500`
        : `${baseClasses} bg-white text-gray-700 border border-transparent hover:border-amber-600 hover:text-amber-700`
    }
=======
// Dynamic button class for view toggle
const getViewButtonClass = (isActive) => {
  const baseClasses = 'px-5 py-2.5 rounded-lg font-medium transition-all duration-200 flex items-center gap-2 text-sm'
  
  if (isActive) {
    return isDarkMode.value
      ? `${baseClasses} bg-amber-600 text-white shadow-lg shadow-amber-900/50`
      : `${baseClasses} bg-amber-700 text-white shadow-lg shadow-amber-900/30`
  } else {
    return isDarkMode.value
      ? `${baseClasses} bg-black text-gray-300 border border-transparent hover:border-amber-500 hover:text-amber-500`
      : `${baseClasses} bg-white text-gray-700 border border-transparent hover:border-amber-600 hover:text-amber-700`
>>>>>>> main
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
  const selectedPageSize = ref(20)
  const searchQuery = ref("")

  // Helper to check if message matches search query
  const messageMatchesSearch = (msg) => {
    if (!searchQuery.value) return true
    const query = searchQuery.value.toLowerCase()
    
    const sender = (msg.sender || '').toLowerCase()
    const text = (msg.text || '').toLowerCase()
    const address = (msg.address || '').toLowerCase()
    const platform = (msg.platform || '').toLowerCase()
    
    return sender.includes(query) || 
           text.includes(query) || 
           address.includes(query) || 
           platform.includes(query)
  }

  // Filtered Table Messages
  const filteredTableMessages = computed(() => {
     return messagesStore.normalizedMessages.filter(messageMatchesSearch)
  })

  // Group messages by date for timeline view (Conversations view)
  const groupedMessagesByDate = computed(() => {
    const groups = {}
    const today = new Date()
    const yesterday = new Date(today)
    yesterday.setDate(today.getDate() - 1)

    // Use pre-computed active conversations from store
    const activeConversations = messagesStore.activeConversations

    for (const msg of activeConversations) {
      if (!messageMatchesSearch(msg)) continue

      const timestamp = msg.timestamp
      if (!timestamp) continue

      // Timestamp is typically unix seconds or ISO string? 
      // Normalizer keeps original value. Let's assume Unix seconds if number, or ISO string.
      const ts = typeof timestamp === 'number' && String(timestamp).length === 10 ? timestamp * 1000 : timestamp
      const date = new Date(ts)
      
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

  // Handle platform change from pills (resets pagination)
  async function handlePlatformChange(platformId) {
    activePlatform.value = platformId

    console.log('Platform changed to:', platformId)

    try {
      messagesStore.resetPagination()
      if (platformId === 'all') {
        await messagesStore.fetchAllMessages({ _o: 0, _c: selectedPageSize.value })
      } else {
        await messagesStore.fetchMessagesBySource(platformId, { _o: 0, _c: selectedPageSize.value })
      }

      console.log('Messages after filter:', messagesStore.pmessages?.length || 0)
      console.log('Pagination info:', messagesStore.paginationInfo)
    } catch (err) {
      console.error('Error filtering messages:', err)
      toast.error('Failed to filter messages. Please try again.')
    }
  }

  // Refresh messages (maintains current page)
  async function refreshMessages() {
    try {
      const params = {
        _o: messagesStore.pagination.offset,
        _c: messagesStore.pagination.limit
      }
      if (activePlatform.value === 'all') {
        await messagesStore.fetchAllMessages(params)
      } else {
        await messagesStore.fetchMessagesBySource(activePlatform.value, params)
      }
      toast.success('Messages refreshed successfully!')
    } catch (err) {
      console.error('Error refreshing messages:', err)
      toast.error('Failed to refresh messages. Please try again.')
    }
  }

  // Pagination handlers
  async function goToNextPage() {
    try {
      await messagesStore.nextPage({ src: activePlatform.value })
    } catch (err) {
      console.error('Error going to next page:', err)
      toast.error('Failed to load next page.')
    }
  }

  async function goToPrevPage() {
    try {
      await messagesStore.prevPage({ src: activePlatform.value })
    } catch (err) {
      console.error('Error going to previous page:', err)
      toast.error('Failed to load previous page.')
    }
  }

  async function goToPage(page) {
    if (page === '...') return
    try {
      await messagesStore.goToPage(page, { src: activePlatform.value })
    } catch (err) {
      console.error('Error going to page:', err)
      toast.error('Failed to load page.')
    }
  }

  async function changePageSize(size) {
    selectedPageSize.value = size
    try {
      await messagesStore.setPageSize(size, { src: activePlatform.value })
    } catch (err) {
      console.error('Error changing page size:', err)
      toast.error('Failed to change page size.')
    }
  }

  const openChatPanel = (msg) => {
    selectedMessage.value = msg
    // msg is normalized, so it has .id property
    selectedMessageId.value = msg.id
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

  const getValue = (msg, key) => {
    // legacy support for raw msg if still used anywhere (e.g. AIPrediction which expects raw?)
    if (msg && typeof msg === 'object' && !Array.isArray(msg) && msg[key] !== undefined) {
         return msg[key] // if normalized object matches key (unlikely for src_msg etc)
    }
    // Fallback to normalized map if needed, but we mostly use .text, .platform etc now.
    // If AIPredictionPanel receives a raw array, this still works. 
    // If it receives a normalized object, it might need updating. 
    // Assuming AIPredictionPanel handles raw arrays primarily if passed raw. 
    // But normalizedMessages returns objects. 
    
    if (!msg || !messagesStore.pmessages_k?.[key]) return null
    const index = messagesStore.pmessages_k[key][0]
    return msg[index]
  }

  onMounted(async () => {
    try {
      await messagesStore.fetchAllMessages({ _o: 0, _c: selectedPageSize.value })
      console.log('Messages fetched:', messagesStore.pmessages?.length)
      console.log('Pagination info:', messagesStore.paginationInfo)
    } catch (err) {
      console.log('Failed to fetch messages:', err)
      toast.error('Failed to load messages. Please try again.')
    }
  })
</script>
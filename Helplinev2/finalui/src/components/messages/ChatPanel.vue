<template>
  <!-- Backdrop -->
  <div class="fixed inset-0 bg-black/50 z-40 transition-opacity duration-300" @click="$emit('close')"></div>

  <!-- Chat Panel Slide-out -->
  <div class="fixed right-0 top-0 h-full w-full md:w-[500px] shadow-2xl z-50 flex flex-col border-l animate-slide-in"
    :class="isDarkMode
      ? 'bg-black border-transparent'
      : 'bg-white border-transparent'">
    <!-- Header -->
    <div class="flex items-center justify-between p-4 border-b" :class="isDarkMode
      ? 'bg-black border-transparent'
      : 'bg-gray-50 border-transparent'">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold text-sm"
          :style="{ background: getAvatarColor(getContactName()) }">
          {{ getContactName().charAt(0).toUpperCase() }}
        </div>
        <div>
          <h3 class="font-semibold" :class="isDarkMode ? 'text-gray-100' : 'text-gray-900'">
            {{ getContactName() }}
          </h3>
          <p class="text-xs flex gap-2" :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'">
            <span>{{ getPlatform() }}</span>
            <span v-if="props.selectedMessage?.address" class="opacity-75">• {{ props.selectedMessage.address }}</span>
          </p>
        </div>
      </div>
      <div class="flex items-center gap-2">
        <button 
          @click="handleEndConversation" 
          :disabled="isEndConversationLoading"
          class="px-3 py-1.5 text-xs font-medium rounded-md flex items-center gap-1 transition-colors"
          :class="isDarkMode 
            ? 'bg-red-900/30 text-red-400 hover:bg-red-900/50 border border-red-900/50' 
            : 'bg-red-100 text-red-700 hover:bg-red-200 border border-red-200'"
        >
          <i-mdi-check-circle-outline class="w-4 h-4" />
          {{ isEndConversationLoading ? 'Ending...' : 'End Conversation' }}
        </button>
        <button @click="$emit('close')" class="p-2 rounded-lg transition-all" :class="isDarkMode
          ? 'hover:bg-neutral-800 text-gray-400'
          : 'hover:bg-gray-200'">
          <i-mdi-close class="w-6 h-6" :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'" />
        </button>
      </div>
    </div>

    <!-- Message History -->
    <div ref="messageContainer" class="flex-1 overflow-y-auto p-4 space-y-6" :class="isDarkMode ? 'bg-black' : 'bg-gray-50'">
      <div v-if="isLoadingHistory" class="flex justify-center p-4">
          <span class="text-sm text-gray-400">Loading history...</span>
      </div>
      
      <!-- Loop through conversation history -->
      <div v-for="(msg, index) in conversationHistory" :key="msg.id || index" class="flex flex-col w-full">
        
        <!-- Check alignment based on direction. Assuming '2' is outbound/agent -->
        <div class="flex w-full" :class="isOutbound(msg) ? 'justify-end' : 'justify-start'">
          
          <div class="flex max-w-[85%] md:max-w-[75%] gap-2" :class="isOutbound(msg) ? 'flex-row-reverse' : 'flex-row'">
            
            <!-- Avatar (Only for Inbound/Customer usually, but keeping for both if desired) -->
            <!-- Showing avatar for inbound makes sense. For outbound (Agent), maybe show agent avatar or simplify. -->
            <div v-if="!isOutbound(msg)"
              class="w-8 h-8 rounded-full flex items-center justify-center text-white font-semibold text-xs flex-shrink-0 mt-auto shadow-sm"
              :style="{ background: getAvatarColor(msg.sender || 'Unknown') }">
              {{ (msg.sender || 'U').charAt(0).toUpperCase() }}
            </div>

            <!-- Bubble -->
            <div class="relative px-4 py-2 shadow-sm rounded-2xl text-sm break-words" 
                 :class="[
                   isOutbound(msg) 
                     ? (isDarkMode ? 'bg-indigo-600 text-white rounded-br-none' : 'bg-indigo-600 text-white rounded-br-none') 
                     : (isDarkMode ? 'bg-neutral-800 text-gray-100 rounded-bl-none' : 'bg-white text-gray-800 rounded-bl-none')
                 ]">
                 
                 <!-- Sender Name (Only for Inbound in Group Context, or if needed. In 1:1 usually hidden if obvious) -->
                 <!-- Keeping it small if explicitly different from main contact or if inbound -->
                 <div v-if="!isOutbound(msg) && msg.sender" class="text-[10px] font-bold mb-1 opacity-70 uppercase tracking-wider">
                    {{ msg.sender }}
                 </div>

                 <p class="whitespace-pre-wrap leading-relaxed">{{ msg.text }}</p>
                 
                 <!-- Metadata Footer in Bubble -->
                 <div class="flex items-center justify-end gap-1 mt-1 select-none">
                    <span class="text-[10px] opacity-70">
                      {{ formatMessageDate(msg.timestamp) }}
                    </span>
                    <!-- Checkmarks for outbound if available -->
                    <i-mdi-check-all v-if="isOutbound(msg)" class="w-3 h-3 opacity-70" />
                 </div>
            </div>
          </div>
        </div>
      </div>
      
      <div v-if="!isLoadingHistory && conversationHistory.length === 0" class="text-center text-gray-500 text-sm mt-4">
          No history found.
      </div>
    </div>

    <!-- Message Input -->
    <MessageInput v-model="newMessage" @send-message="handleSendMessage" />
  </div>
</template>

<script setup>
  import { ref, inject, onMounted, watch, computed } from 'vue'
  import { toast } from 'vue-sonner'
  import { useMessagesStore } from '@/stores/messages'
  import { useAuthStore } from '@/stores/auth' // Need auth for agent ID
  import { decodeMessage } from '@/utils/formatters' // Still used for decoding potentially? Normalizer handles it though.
  import MessageInput from './MessageInput.vue'

  const props = defineProps({
    selectedMessage: {
      type: Object,
      default: null
    },
    newMessage: {
      type: String,
      default: ''
    }
  })

  const emit = defineEmits(['close', 'sendMessage'])

  const messagesStore = useMessagesStore()
  const authStore = useAuthStore()
  
  const newMessage = ref(props.newMessage)
  const conversationHistory = ref([])
  const isLoadingHistory = ref(false)

  // Inject theme
  const isDarkMode = inject('isDarkMode')

  const getContactName = () => {
    return props.selectedMessage?.sender || props.selectedMessage?.address || 'Unknown Contact'
  }

  const getPlatform = () => {
    return props.selectedMessage?.platform || 'Unknown Platform'
  }

  // Robust date formatter using timestamp (seconds or ms)
  const formatMessageDate = (timestamp) => {
    if (!timestamp) return ''
    const ts = typeof timestamp === 'string' && timestamp.length === 10 ? parseInt(timestamp) * 1000 : 
               typeof timestamp === 'number' && String(timestamp).length === 10 ? timestamp * 1000 : timestamp
    const date = new Date(ts)
    if (isNaN(date.getTime())) return String(timestamp)
    
    return date.toLocaleString('en-US', {
      day: 'numeric', 
      month: 'short', 
      hour: '2-digit', 
      minute: '2-digit'
    })
  }

  const fetchHistory = async () => {
    const src = props.selectedMessage?.platform
    const srcCallId = props.selectedMessage?.threadId || props.selectedMessage?.address
    
    if (!src || !srcCallId) return

    isLoadingHistory.value = true
    try {
      // Fetch latest 10 messages
      // _s='id' (sequential ID), _sd='desc' (newest first), _c=10 (limit 10)
      const params = { _c: 10, _o: 0, _s: 'id', _sd: 'desc' } 
      const data = await messagesStore.fetchConversationHistory(src, srcCallId, params)
      
      // Store already returns normalized array if using the updated action
      let rows = []
      if (Array.isArray(data)) {
        rows = data
      } else if (data.messages || data.pmessages) {
         // Fallback if store didn't normalize (state it did, but just in case)
         // Logic inside store handles normalization now.
         rows = data.messages || data.pmessages
      }
      
      // Filter out messages that show 'closed' or have isClosed flag
      const activeMessages = rows.filter(msg => !msg.isClosed && !msg.text?.includes('*closed*'))

      // Sort oldest to newest for chat timeline (render top to bottom)
      conversationHistory.value = activeMessages.sort((a, b) => {
        // Fallback to ID if timestamps are missing/equal
        const tA = a.timestamp || 0
        const tB = b.timestamp || 0
        if (tA !== tB) return tA - tB
        return (a.id || 0) - (b.id || 0)
      })
      
      // Scroll to bottom after render
      setTimeout(scrollToBottom, 100)
      
    } catch (e) {
      console.error("Failed to load history", e)
    } finally {
      isLoadingHistory.value = false
    }
  }

  const messageContainer = ref(null)

  const scrollToBottom = () => {
    if (messageContainer.value) {
      messageContainer.value.scrollTop = messageContainer.value.scrollHeight
    }
  }

  // Load history when panel opens or message changes
  onMounted(fetchHistory)
  watch(() => props.selectedMessage, fetchHistory)

  const getAvatarColor = (name) => {
    const colors = isDarkMode.value
      ? ['#F59E0B', '#10B981', '#EF4444', '#8B5CF6', '#EC4899']
      : ['#B45309', '#059669', '#DC2626', '#7C3AED', '#DB2777']
    const index = name?.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) || 0
    return colors[index % colors.length]
  }

  // Determine if message is outbound (from agent/system)
  const isOutbound = (msg) => {
      // 2 = Outbound, 1 = Inbound
      return String(msg.direction) === '2'
  }

  const isEndConversationLoading = ref(false)

  const handleEndConversation = async () => {
    if (!confirm('Are you sure you want to end this conversation?')) return

    const m = props.selectedMessage
    const payload = {
      close: "close",
      src_msg: "*closed*",
      src: m.platform || 'whatsApp', 
      src_uid: m.id || '',
      src_address: m.address || '',
      src_uid2: "",
      src_usr: "",
      src_vector: "",
      src_callid: m.threadId || m.address || '', 
      src_ts: "",
      activity_id: "-1",
      contact_uuid_id: "-1",
      activity_ca_id: ""
    }

    isEndConversationLoading.value = true
    try {
      await messagesStore.closeConversation(payload)
      toast.success('Conversation ended successfully')
      emit('close')
    } catch (err) {
      console.error('Failed to end conversation:', err)
      toast.error('Failed to end conversation. Please try again.')
    } finally {
      isEndConversationLoading.value = false
    }
  }

  const isSending = ref(false)

  const handleSendMessage = async (msgText) => {
    if (!msgText.trim()) return

    const timestamp = Math.floor(Date.now() / 1000) // Seconds
    const extension = authStore.profile?.exten || '100'
    const m = props.selectedMessage
    const src = m.platform || 'whatsApp'
    
    // Construct payload per user request
    const payload = {
        src: src,
        src_uid: `${src}-${extension}-${timestamp}`,
        src_address: "",
        src_uid2: `${src}-${extension}-${timestamp}-1`,
        src_usr: extension,
        src_vector: "2", // Direction?
        src_callid: m.threadId || m.address || '', // Customer Phone
        src_ts: "",
        activity_id: "-1", // Context
        contact_uuid_id: "-1",
        activity_ca_id: "",
        src_msg: msgText
    }

    isSending.value = true
    try {
        await messagesStore.sendMessage(payload)
        toast.success("Message sent")
        newMessage.value = ''
        
        // Refresh history safely - don't let it crash the send success flow
        try {
            await fetchHistory()
        } catch (hErr) {
            console.warn("History refresh failed, but send was success", hErr)
        }
    } catch (e) {
        console.error("Failed to send", e)
        toast.error("Failed to send message")
    } finally {
        isSending.value = false
    }
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
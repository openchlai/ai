<template>
  <div class="space-y-6">
    <div v-if="Object.keys(groupedMessagesByDate).length === 0" class="text-center py-12 rounded-lg shadow-xl border"
      :class="isDarkMode
        ? 'bg-black border-transparent'
        : 'bg-white border-transparent'">
      <p :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'">
        No chats to display
      </p>
    </div>

    <div v-for="(group, label) in groupedMessagesByDate" :key="label" class="space-y-3">
      <h2 class="text-base font-semibold uppercase tracking-wide"
        :class="isDarkMode ? 'text-amber-500' : 'text-amber-700'">
        {{ label }}
      </h2>

      <div class="space-y-2">
        <div v-for="message in group" :key="message.id" :class="[
          'rounded-lg p-4 shadow-xl border transition-all duration-200 cursor-pointer',
          selectedMessageId === message.id
            ? isDarkMode
              ? 'ring-2 ring-amber-600 border-amber-600 bg-amber-600/10'
              : 'ring-2 ring-amber-600 border-amber-600 bg-amber-100'
            : isDarkMode
              ? 'bg-black border-transparent hover:border-amber-600/50 hover:shadow-2xl'
              : 'bg-white border-transparent hover:border-amber-600/50 hover:shadow-2xl'
        ]" @click="openChatPanel(message)">
          <div class="flex items-start gap-3">
            <!-- Avatar -->
            <div v-if="message.platform === 'gateway'"
              class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0 text-sm shadow-md"
              :class="isDarkMode ? 'bg-indigo-600' : 'bg-indigo-700'">
              <i-mdi-robot-outline class="w-6 h-6" />
            </div>
            <div v-else
              class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0 text-sm"
              :style="{ background: getAvatarColor(message.sender || '') }">
              {{ (message.sender || '?').charAt(0).toUpperCase() }}
            </div>

            <!-- Content -->
            <div class="flex-1 min-w-0">
              <div class="flex justify-between items-baseline mb-1">
                <span class="text-sm font-bold" :class="isDarkMode ? 'text-indigo-400' : 'text-indigo-700'"
                  v-if="message.platform === 'gateway'">
                  Post-Call Insight
                </span>
                <span class="text-sm font-medium" :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'" v-else>
                  {{ message.sender || 'Unknown' }}
                  <span v-if="message.address && message.address !== message.sender" 
                        class="block text-xs font-normal opacity-75">
                    {{ message.address }}
                  </span>
                  <span v-else-if="message.address" class="block text-xs font-normal opacity-75">
                    {{ message.address }}
                  </span>
                </span>
                <span class="text-xs ml-2" :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'">
                  {{ formatTime(message.timestamp) }}
                </span>
              </div>

              <div class="flex gap-2 mb-2">
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase border tracking-wider"
                  :class="message.platform === 'gateway'
                    ? (isDarkMode ? 'bg-indigo-600/20 text-indigo-400 border-indigo-600/30' : 'bg-indigo-100 text-indigo-700 border-indigo-300')
                    : (isDarkMode ? 'bg-amber-600/20 text-amber-500 border-amber-600/30' : 'bg-amber-100 text-amber-700 border-amber-300')">
                  {{ message.platform === 'gateway' ? 'AI Prediction' : (message.platform || 'Chat') }}
                </span>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase border tracking-wider"
                  v-if="message.platform === 'gateway'"
                  :class="isDarkMode ? 'bg-emerald-600/20 text-emerald-400 border-emerald-600/30' : 'bg-emerald-100 text-emerald-700 border-emerald-300'">
                  High Confidence
                </span>
                <span class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase border tracking-wider" v-else
                  :class="isDarkMode ? 'bg-green-600/20 text-green-400 border-green-600/30' : 'bg-green-100 text-green-700 border-green-300'">
                  {{ message.status || 'Active' }}
                </span>
              </div>

              <p class="text-sm" :class="isDarkMode ? 'text-gray-300' : 'text-gray-600'"
                v-if="message.platform === 'gateway'">
                AI has analyzed call <strong>#{{ getPredictionCallId(message) }}</strong> and classified it as
                <span class="italic">{{ getPredictionCategory(message) }}</span>.
              </p>
              <p class="text-sm truncate" :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'" v-else>
                {{ message.text || '' }}
              </p>
            </div>

            <!-- Chat Action Button -->
            <button @click.stop="openChatPanel(message)"
              class="p-2.5 rounded-xl transition-all duration-200 flex-shrink-0 text-white shadow-lg transform active:scale-95"
              :class="message.platform === 'gateway'
                ? (isDarkMode ? 'bg-indigo-600 hover:bg-indigo-700' : 'bg-indigo-700 hover:bg-indigo-800')
                : (isDarkMode ? 'bg-amber-600 hover:bg-amber-700' : 'bg-amber-700 hover:bg-amber-800')"
              :title="message.platform === 'gateway' ? 'View AI Insights' : 'Open Chat'">
              <i-mdi-robot-outline v-if="message.platform === 'gateway'" class="w-5 h-5" />
              <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z" />
                <path
                  d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z" />
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
  // import { decodeMessage } from '@/utils/formatters' // No longer needed if normalized

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

  // Helper removed, using normalized object properties directly.
  
  const formatTime = (timestamp) => {
    if (!timestamp) return 'N/A'
    // Normalized timestamp is usually string or number.
    const ts = typeof timestamp === 'string' && timestamp.length === 10 ? parseInt(timestamp) * 1000 : 
               typeof timestamp === 'number' && String(timestamp).length === 10 ? timestamp * 1000 : timestamp
               
    const date = new Date(ts)
    if (isNaN(date.getTime())) return 'N/A'
    
    // Check if it's today
    const now = new Date()
    const isToday = date.toDateString() === now.toDateString()
    
    return date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    }) + (isToday ? '' : ` ${date.getDate()}/${date.getMonth() + 1}`)
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

  const getPredictionCallId = (message) => {
    // message.text is the decoded content. For AI messages, it might be JSON.
    const rawMsg = message.text
    if (!rawMsg) return 'N/A'
    try {
      // If normalizer decoded base64, rawMsg is the JSON string.
      // Or if it was double encoded? 
      // Usually src_msg is Base64 -> JSON string.
      // Normalizer does: decodeURIComponent(escape(atob(raw)))
      const data = typeof rawMsg === 'string' ? JSON.parse(rawMsg) : rawMsg
      return data.call_metadata?.call_id || 'N/A'
    } catch (e) {
      return 'N/A'
    }
  }

  const getPredictionCategory = (message) => {
    const rawMsg = message.text
    if (!rawMsg) return 'N/A'
    try {
      const data = typeof rawMsg === 'string' ? JSON.parse(rawMsg) : rawMsg
      const c = data.payload?.classification
      return c?.sub_category || c?.main_category || 'Unclassified'
    } catch (e) {
      return 'Unclassified'
    }
  }
</script>
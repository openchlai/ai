<template>
  <div class="rounded-lg shadow-xl border overflow-hidden" :class="isDarkMode
    ? 'bg-black border-transparent'
    : 'bg-white border-transparent'">
    <div class="overflow-x-auto">
      <table class="w-full">
        <thead>
          <tr class="border-b" :class="isDarkMode
            ? 'bg-black/60 border-transparent'
            : 'bg-gray-50 border-transparent'">
            <th class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider whitespace-nowrap"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
              Contact
            </th>
            <th class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider whitespace-nowrap"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
              Platform
            </th>
            <th class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider whitespace-nowrap"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
              Message
            </th>
            <th class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider whitespace-nowrap"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
              Time
            </th>
            <th class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider whitespace-nowrap"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
              Status
            </th>
            <th class="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wider whitespace-nowrap"
              :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
              Actions
            </th>
          </tr>
        </thead>
        <tbody class="divide-y" :class="isDarkMode ? 'divide-gray-700' : 'divide-gray-200'">
          <tr v-for="message in messages" :key="message.id" :class="[
            'cursor-pointer transition-all duration-200',
            selectedMessageId === message.id
              ? isDarkMode
                ? 'bg-amber-600/10 border-l-4 border-l-amber-600'
                : 'bg-amber-100 border-l-4 border-l-amber-600'
              : isDarkMode
                ? 'hover:bg-neutral-800'
                : 'hover:bg-gray-50'
          ]" @click="openChatPanel(message)">
            <!-- Contact -->
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center gap-3">
                <div v-if="message.platform === 'gateway'"
                  class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0 text-sm shadow-md"
                  :class="isDarkMode ? 'bg-indigo-600' : 'bg-indigo-700'">
                  <i-mdi-robot-outline class="w-6 h-6" />
                </div>
                <div v-else
                  class="w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold text-sm flex-shrink-0"
                  :style="{ background: getAvatarColor(message.sender || '') }">
                  {{ (message.sender || '?').charAt(0).toUpperCase() }}
                </div>
                <div class="flex flex-col">
                  <span class="text-sm font-medium" :class="isDarkMode ? 'text-gray-200' : 'text-gray-900'">
                    {{ message.platform === 'gateway' ? 'AI Assistant' : (message.sender || 'Unknown') }}
                  </span>
                  <span v-if="message.platform !== 'gateway' && message.address" 
                        class="text-xs" :class="isDarkMode ? 'text-gray-400' : 'text-gray-500'">
                    {{ message.address }}
                  </span>
                </div>
              </div>
            </td>

            <!-- Platform -->
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="px-3 py-1 rounded-full text-xs font-bold uppercase border tracking-wider"
                :class="message.platform === 'gateway'
                  ? (isDarkMode ? 'bg-indigo-600/20 text-indigo-400 border-indigo-600/30' : 'bg-indigo-100 text-indigo-700 border-indigo-300')
                  : (isDarkMode ? 'bg-amber-600/20 text-amber-500 border-amber-600/30' : 'bg-amber-100 text-amber-700 border-amber-300')">
                {{ message.platform === 'gateway' ? 'AI Insight' : (message.platform || 'Chat') }}
              </span>
            </td>

            <!-- Message -->
            <td class="px-6 py-4">
              <div class="text-sm max-w-md truncate" :class="isDarkMode ? 'text-gray-300' : 'text-gray-700'">
                <template v-if="message.platform === 'gateway'">
                  Classification: {{ getPredictionCategory(message) }}
                </template>
                <template v-else>
                  {{ message.text || '' }}
                </template>
              </div>
            </td>

            <!-- Time -->
            <td class="px-6 py-4 whitespace-nowrap text-sm" :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'">
              {{ formatDateTime(message.timestamp) }}
            </td>

            <!-- Status -->
            <td class="px-6 py-4 whitespace-nowrap">
              <span class="px-3 py-1 rounded-full text-xs font-semibold uppercase border tracking-wider"
                :class="message.platform === 'gateway'
                  ? (isDarkMode ? 'bg-emerald-600/20 text-emerald-400 border-emerald-600/30' : 'bg-emerald-100 text-emerald-700 border-emerald-300')
                  : (isDarkMode ? 'bg-green-600/20 text-green-400 border-green-600/30' : 'bg-green-100 text-green-700 border-green-300')">
                {{ message.platform === 'gateway' ? 'High Conf.' : (message.status || 'Active')
                }}
              </span>
            </td>

            <!-- Actions -->
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <button class="p-2 rounded-lg text-white transition-all duration-200 shadow-md" :class="message.platform === 'gateway'
                ? (isDarkMode ? 'bg-indigo-600 hover:bg-indigo-700' : 'bg-indigo-700 hover:bg-indigo-800')
                : (isDarkMode ? 'bg-amber-600 hover:bg-amber-700' : 'bg-amber-700 hover:bg-amber-800')"
                @click.stop="openChatPanel(message)"
                :title="message.platform === 'gateway' ? 'View AI Insights' : 'Open Chat'">
                <i-mdi-robot-outline v-if="message.platform === 'gateway'" class="w-4 h-4" />
                <svg v-else class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z" />
                  <path
                    d="M15 7v2a4 4 0 01-4 4H9.828l-1.766 1.767c.28.149.599.233.938.233h2l3 3v-3h2a2 2 0 002-2V9a2 2 0 00-2-2h-1z" />
                </svg>
              </button>
            </td>
          </tr>

          <tr v-if="!messages || messages.length === 0">
            <td colspan="6" class="text-center py-12" :class="isDarkMode ? 'text-gray-500' : 'text-gray-500'">
              No messages to display
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
  import { inject } from 'vue'
  import { useMessagesStore } from '@/stores/messages'
  // import { decodeMessage } from '@/utils/formatters' // No longer needed

  const props = defineProps({
    messages: {
      type: Array,
      default: () => []
    },
    selectedMessageId: [String, Number]
  })

  const emit = defineEmits(['openChat'])

  const messagesStore = useMessagesStore()

  // Inject theme
  const isDarkMode = inject('isDarkMode')

  const formatDateTime = (timestamp) => {
    if (!timestamp) return 'N/A'
    // Normalized timestamp
    const ts = typeof timestamp === 'string' && timestamp.length === 10 ? parseInt(timestamp) * 1000 : 
               typeof timestamp === 'number' && String(timestamp).length === 10 ? timestamp * 1000 : timestamp
    
    const date = new Date(ts)
    return date.toLocaleString('en-US', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
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
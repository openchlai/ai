<template>
  <div class="overflow-x-auto bg-white rounded shadow p-4">
    <table class="min-w-full divide-y divide-gray-200">
      <thead class="bg-gray-50">
        <tr>
          <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">Contact</th>
          <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">Platform</th>
          <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">Message</th>
          <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">Time</th>
          <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">Status</th>
          <th class="px-4 py-2 text-left text-sm font-medium text-gray-700">Actions</th>
        </tr>
      </thead>
      <tbody class="divide-y divide-gray-200">
        <tr
          v-for="message in messages"
          :key="message[messagesStore.pmessages_k.id?.[0] || 'id']"
          :class="{
            'bg-blue-50': selectedMessageId === message[messagesStore.pmessages_k.id?.[0] || 'id']
          }"
          @click="openChatPanel(message)"
        >
          <!-- Contact -->
          <td class="px-4 py-2 flex items-center space-x-2">
            <div
              class="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold"
              :style="{ background: getAvatarColor(message[messagesStore.pmessages_k.created_by?.[0] || 'created_by'] || '') }"
            >
              {{
                (message[messagesStore.pmessages_k.created_by?.[0] || 'created_by'] || '?').charAt(0)
              }}
            </div>
            <span>
              {{ message[messagesStore.pmessages_k.created_by?.[0] || 'created_by'] || "Unknown" }}
            </span>
          </td>

          <!-- Platform -->
          <td class="px-4 py-2">
            <span class="px-2 py-1 rounded bg-gray-200 text-gray-700 text-xs">
              {{ message[messagesStore.pmessages_k.src?.[0] || 'src'] || "N/A" }}
            </span>
          </td>

          <!-- Message -->
          <td class="px-4 py-2">
            {{ message[messagesStore.pmessages_k.src_msg?.[0] || 'src_msg'] || "" }}
          </td>

          <!-- Time -->
          <td class="px-4 py-2 text-sm text-gray-500">
            {{
              message[messagesStore.pmessages_k.dth?.[0] || 'dth']
                ? new Date(
                    message[messagesStore.pmessages_k.dth?.[0] || 'dth'] * 1000
                  ).toLocaleString()
                : "N/A"
            }}
          </td>

          <!-- Status -->
          <td class="px-4 py-2">
            <span
              class="px-2 py-1 rounded text-white text-xs"
              :class="statusClass(message[messagesStore.pmessages_k.src_status?.[0] || 'src_status'], true)"
            >
              {{ message[messagesStore.pmessages_k.src_status?.[0] || 'src_status'] || "Active" }}
            </span>
          </td>

          <!-- Actions -->
          <td class="px-4 py-2">
            <button
              class="p-2 rounded bg-blue-500 text-white hover:bg-blue-600"
              @click.stop="openChatPanel(message)"
              title="Open Chat"
            >
              Open
            </button>
          </td>
        </tr>

        <tr v-if="!messages || messages.length === 0">
          <td colspan="6" class="text-center py-4 text-gray-500">
            No messages to display
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useMessagesStore } from '@/stores/messages';

const props = defineProps({
  messages: {
    type: Array,
    default: () => [],
  },
  selectedMessageId: [String, Number],
});

const emit = defineEmits(['open-chat']);

const messagesStore = useMessagesStore();

const openChatPanel = (message) => {
  emit('open-chat', message);
};

const getAvatarColor = (name) => {
  return 'var(--color-primary)'; // you can customize colors
};

// Status mapping for Tailwind
const statusClass = (statusRaw, isTable = false) => {
  const status = String(statusRaw || 'active').toLowerCase();
  const map = {
    active: 'bg-green-500',
    pending: 'bg-yellow-500',
    inactive: 'bg-gray-500',
    busy: 'bg-red-500',
    away: 'bg-orange-500'
  };
  return map[status] || map.active;
};
</script>

<template>
  <div class="space-y-6">
    <div v-if="Object.keys(groupedMessagesByDate).length === 0" class="text-center py-10 text-gray-500">
      <p>No chats to display</p>
    </div>

    <div
      v-for="(group, label) in groupedMessagesByDate"
      :key="label"
      class="space-y-4"
    >
      <h2 class="text-gray-700 font-semibold text-lg">{{ label }}</h2>

      <div class="space-y-2">
        <div
          v-for="message in group"
          :key="message[messagesStore.pmessages_k.id?.[0] || 'id']"
          :class="[
            'flex items-start space-x-3 p-2 rounded cursor-pointer hover:bg-gray-100',
            selectedMessageId === message[messagesStore.pmessages_k.id?.[0] || 'id'] ? 'bg-blue-50' : ''
          ]"
          @click="openChatPanel(message)"
        >
          <!-- Avatar -->
          <div
            class="w-10 h-10 rounded-full flex items-center justify-center text-white font-bold"
            :style="{ background: getAvatarColor(message[messagesStore.pmessages_k.created_by?.[0] || 'created_by'] || '') }"
          >
            {{ (message[messagesStore.pmessages_k.created_by?.[0] || 'created_by'] || '?').charAt(0) }}
          </div>

          <!-- Chat Content -->
          <div class="flex-1">
            <div class="flex justify-between items-center">
              <span class="font-medium text-gray-800">
                {{ message[messagesStore.pmessages_k.created_by?.[0] || 'created_by'] || 'Unknown' }}
              </span>
              <span class="text-xs text-gray-400">
                {{
                  message[messagesStore.pmessages_k.dth?.[0] || 'dth']
                    ? new Date(message[messagesStore.pmessages_k.dth?.[0] || 'dth'] * 1000).toLocaleTimeString()
                    : "N/A"
                }}
              </span>
            </div>

            <div class="flex space-x-2 mt-1 items-center">
              <span class="px-2 py-1 bg-gray-200 text-gray-700 rounded text-xs">
                {{ message[messagesStore.pmessages_k.src?.[0] || 'src'] || 'N/A' }}
              </span>
              <span
                class="px-2 py-1 rounded text-white text-xs"
                :class="statusClass(message[messagesStore.pmessages_k.src_status?.[0] || 'src_status'])"
              >
                {{ message[messagesStore.pmessages_k.src_status?.[0] || 'src_status'] || 'Active' }}
              </span>
            </div>

            <p class="text-gray-700 mt-1 text-sm">
              {{ message[messagesStore.pmessages_k.src_msg?.[0] || 'src_msg'] || '' }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useMessagesStore } from '@/stores/messages';

const props = defineProps({
  groupedMessagesByDate: {
    type: Object,
    default: () => ({}),
  },
  selectedMessageId: [String, Number],
});

const emit = defineEmits(['open-chat']);

const messagesStore = useMessagesStore();

const openChatPanel = (message) => {
  emit('open-chat', message);
};

const getAvatarColor = (name) => {
  return 'var(--color-primary)';
};

const statusClass = (statusRaw) => {
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

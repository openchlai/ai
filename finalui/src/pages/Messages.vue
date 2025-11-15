<template>
  <div class="p-6">
    <h1 class="text-2xl font-bold mb-2">Chats</h1>
    <p class="text-gray-500 mb-4">Manage conversations and communications across all channels</p>

    <!-- Filter -->
    <Filter 
      :channelFilters="channelFilters" 
      :activePlatform="activePlatform" 
      @update:activePlatform="activePlatform = $event" 
    />

    <!-- View Buttons -->
    <div class="flex space-x-2 mb-4">
      <button class="px-4 py-2 border rounded" :class="activeView==='timeline'?'bg-blue-500 text-white':''" @click="activeView='timeline'">Timeline</button>
      <button class="px-4 py-2 border rounded" :class="activeView==='table'?'bg-blue-500 text-white':''" @click="activeView='table'">Table</button>
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
      :messages="filteredMessages"
      :selectedMessageId="selectedMessageId"
      @openChat="openChatPanel"
    />

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
import { ref, computed, onMounted } from 'vue';
import Filter from '@/components/messages/Filter.vue'
import Timeline from '@/components/messages/Timeline.vue'
import Table from '@/components/messages/Table.vue'
import ChatPanel from '@/components/messages/ChatPanel.vue'

import { useMessagesStore } from '@/stores/messages';

const messagesStore = useMessagesStore();

const channelFilters = ref([
  { id: "all", name: "All Channels" },
  { id: "whatsapp", name: "WhatsApp" },
  { id: "sms", name: "SMS" },
  { id: "messenger", name: "Messenger" },
  { id: "telegram", name: "Telegram" },
]);

const activePlatform = ref("all");
const activeView = ref("table");
const showChatPanel = ref(false);
const selectedMessage = ref(null);
const selectedMessageId = ref(null);
const newMessage = ref("");

const filteredMessages = computed(() => {
  let messages = messagesStore.pmessages || [];
  if (activePlatform.value!=='all') messages = messages.filter(m=>m.src===activePlatform.value);
  return messages;
});

const groupedMessagesByDate = computed(() => {
  const groups = {};
  const today = new Date();
  const yesterday = new Date(today); yesterday.setDate(today.getDate()-1);
  for (const msg of filteredMessages.value){
    const date = new Date(msg.dth*1000);
    let label = date.toDateString()===today.toDateString() ? 'Today' : date.toDateString()===yesterday.toDateString() ? 'Yesterday' : date.toLocaleDateString();
    if (!groups[label]) groups[label]=[];
    groups[label].push(msg);
  }
  return groups;
});

const openChatPanel = (msg)=>{
  selectedMessage.value = msg;
  selectedMessageId.value = msg.id;
  showChatPanel.value = true;
};
const closeChatPanel = ()=>{
  showChatPanel.value=false;
  selectedMessage.value=null;
  selectedMessageId.value=null;
  newMessage.value='';
};
const sendMessage=(msg)=>{
  console.log("Send message:",msg);
  newMessage.value='';
};

onMounted(async ()=>{
  await messagesStore.fetchAllMessages().catch(()=>console.log('Failed to fetch'));
});
</script>

<!-- src/views/MessagesView.vue -->
<script setup>
import { onMounted } from 'vue';
import { useMessagesStore } from '@/stores/messages';

const messagesStore = useMessagesStore();

// Load all messages on mount
onMounted(async () => {
  await messagesStore.fetchAllMessages({ _c: 20 });
  await messagesStore.fetchWhatsappMessages({ _c: 20 });
  await messagesStore.fetchSmsMessages({ _c: 20 });
});

// Manual refresh for all
const refreshAll = async () => {
  await Promise.all([
    messagesStore.fetchAllMessages({ _c: 20 }),
    messagesStore.fetchWhatsappMessages({ _c: 20 }),
    messagesStore.fetchSmsMessages({ _c: 20 })
  ]);
};
</script>

<template>
  <section class="messages-view">
    <h2>Messages Overview</h2>
    <button @click="refreshAll">Refresh All</button>
    <p v-if="messagesStore.loading">Loading…</p>
    <p v-else-if="messagesStore.error" class="error">{{ messagesStore.error }}</p>

    <div v-else class="tables-wrapper">
      <!-- All Messages -->
      <div class="table-section">
        <h3>All Messages ({{ messagesStore.allMessages.length }})</h3>
        <table v-if="messagesStore.allMessages.length">
          <thead>
            <tr>
              <th v-for="(value, key) in messagesStore.allMessages[0]" :key="key">{{ key }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(msg, index) in messagesStore.allMessages" :key="index">
              <td v-for="(value, key) in msg" :key="key">{{ value }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else>No messages found.</p>
      </div>

      <!-- WhatsApp Messages -->
      <div class="table-section">
        <h3>WhatsApp Messages ({{ messagesStore.whatsappMessages.length }})</h3>
        <table v-if="messagesStore.whatsappMessages.length">
          <thead>
            <tr>
              <th v-for="(value, key) in messagesStore.whatsappMessages[0]" :key="key">{{ key }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(msg, index) in messagesStore.whatsappMessages" :key="index">
              <td v-for="(value, key) in msg" :key="key">{{ value }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else>No WhatsApp messages found.</p>
      </div>

      <!-- SMS Messages -->
      <div class="table-section">
        <h3>SMS Messages ({{ messagesStore.smsMessages.length }})</h3>
        <table v-if="messagesStore.smsMessages.length">
          <thead>
            <tr>
              <th v-for="(value, key) in messagesStore.smsMessages[0]" :key="key">{{ key }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(msg, index) in messagesStore.smsMessages" :key="index">
              <td v-for="(value, key) in msg" :key="key">{{ value }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else>No SMS messages found.</p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.messages-view {
  padding: 1rem;
}
.tables-wrapper {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
  margin-top: 1rem;
}
.table-section table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 0.5rem;
}
.table-section th, .table-section td {
  border: 1px solid #ddd;
  padding: 8px;
}
.error {
  color: red;
}
button {
  margin-bottom: 1rem;
  padding: 6px 12px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button:hover {
  background: #45a049;
}
</style>

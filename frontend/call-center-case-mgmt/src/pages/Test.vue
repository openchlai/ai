<template>
  <div class="tables-wrapper">
    <!-- Filter Buttons -->
    <div class="filter-buttons">
      <button @click="showAllMessages">All</button>
      <button @click="filterBySource('whatsapp')">WhatsApp</button>
      <button @click="filterBySource('email')">Email</button>
      <button @click="filterBySource('safepal')">Safepal</button>
      <button @click="filterBySource('walkin')">Walk-In</button>
      <button @click="filterBySource('ai')">AI</button>
      <button @click="filterBySource('call')">Call</button>
    </div>

    <!-- Messages Table -->
    <div class="table-section">
      <h3>Messages ({{ messagesStore.pmessages.length }})</h3>

      <table v-if="messagesStore.pmessages.length">
        <thead>
          <tr>
            <th v-for="(meta, key) in messagesStore.pmessages_k" :key="key">
              {{ meta[3] || key }}
            </th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="message in messagesStore.pmessages" :key="message[0]">
            <td v-for="(meta, key) in messagesStore.pmessages_k" :key="key">
              {{ message[meta[0]] }}
            </td>
            <td>
              <button @click="handleView(message[0])">View</button>
            </td>
          </tr>
        </tbody>
      </table>

      <p v-else>No messages found.</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useMessagesStore } from '@/stores/messages'

const messagesStore = useMessagesStore()

onMounted(() => {
  messagesStore.fetchAllMessages()
})

const showAllMessages = () => {
  messagesStore.fetchAllMessages()
}

const filterBySource = (src) => {
  messagesStore.fetchMessagesBySource(src)
}

const handleView = (id) => {
  console.log('View message with ID:', id)
}
</script>

<style scoped>
.tables-wrapper {
  padding: 1rem;
}
.filter-buttons {
  margin-bottom: 1rem;
}
.filter-buttons button {
  margin-right: 0.5rem;
  padding: 0.4rem 0.8rem;
  cursor: pointer;
}
.table-section table {
  width: 100%;
  border-collapse: collapse;
}
.table-section th,
.table-section td {
  border: 1px solid #ccc;
  padding: 0.5rem;
  text-align: left;
}
</style>

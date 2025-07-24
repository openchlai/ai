<!-- src/views/QueueStatusView.vue -->
<script setup>
import { onMounted, onUnmounted } from 'vue';
import { useQueueStore } from '@/stores/queue';

const queueStore = useQueueStore();

// Polling interval
let pollInterval = null;

// Join Queue
const handleJoin = async () => {
  try {
    const res = await queueStore.joinQueue();
    console.log('Joined queue:', res);
  } catch (err) {
    console.error('Join failed:', err.message);
  }
};

// Leave Queue
const handleLeave = async () => {
  try {
    const res = await queueStore.leaveQueue();
    console.log('Left queue:', res);
  } catch (err) {
    console.error('Leave failed:', err.message);
  }
};

// Poll Queue Status every 10 seconds
const startPolling = () => {
  pollInterval = setInterval(async () => {
    try {
      await queueStore.pollQueueStatus();
    } catch (err) {
      console.error('Polling failed:', err.message);
    }
  }, 10000);
};

onMounted(() => {
  queueStore.pollQueueStatus(); // Initial poll
  startPolling();
});

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval);
});
</script>

<template>
  <section class="queue-status">
    <h2>Queue Status</h2>

    <p v-if="queueStore.loading">Loading...</p>
    <p v-else-if="queueStore.error" class="error">{{ queueStore.error }}</p>

    <div v-else>
      <p><strong>Status:</strong> {{ queueStore.status || 'Unknown' }}</p>
      <p><strong>Message:</strong> {{ queueStore.message || 'No message' }}</p>
      <p><small>Last checked: {{ queueStore.lastPoll?.toLocaleTimeString() || 'Never' }}</small></p>
    </div>

    <div class="actions">
      <button @click="handleJoin">Join Queue</button>
      <button @click="handleLeave">Leave Queue</button>
    </div>
  </section>
</template>

<style scoped>
.queue-status {
  padding: 1rem;
  max-width: 400px;
}

.actions button {
  margin-right: 10px;
  padding: 6px 12px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.actions button:hover {
  background: #45a049;
}

.error {
  color: red;
}
</style>

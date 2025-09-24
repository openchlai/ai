<template>
  <template>
    <div class="p-10">
      <h1 class="text-4xl font-bold text-blue-600 underline">
        Tailwind is Working 🚀
      </h1>
    </div>
  </template>

  <div class="bg-gray-100 dark:bg-gray-900 min-h-screen p-4 sm:p-6 lg:p-8">
    <div class="max-w-7xl mx-auto">
      <!-- Header -->
      <header class="flex justify-between items-center mb-6">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Helpline Wallboard</h1>
        <div class="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
          <span class="w-3 h-3 bg-green-500 rounded-full"></span>
          <span>Connected · Last Update: {{ lastUpdate }}</span>
        </div>
      </header>

      <!-- Key Metrics -->
      <section class="mb-8">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Key Metrics</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <MetricCard title="Today's Calls" :value="keyMetrics.today" />
          <MetricCard title="Month's Calls" :value="keyMetrics.month" />
          <MetricCard title="Total Calls" :value="keyMetrics.total" />
        </div>
      </section>

      <!-- Call Status -->
      <section class="mb-8">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Call Status</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
          <MetricCard title="Answered" :value="callStatus.answered" colorClass="text-green-500" />
          <MetricCard title="In Queue" :value="callStatus.inQueue" colorClass="text-yellow-500" />
          <MetricCard title="On Hold" :value="callStatus.onHold" colorClass="text-orange-500" />
          <MetricCard title="Hangup" :value="callStatus.hangup" colorClass="text-red-500" />
        </div>
      </section>

      <!-- Counsellors Online -->
      <section class="mb-8">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Counsellors Online</h2>
        <DataTable :headers="counsellorHeaders" :data="counsellors" />
      </section>

      <!-- Callers Online -->
      <section>
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Callers Online</h2>
        <DataTable :headers="callerHeaders" :data="callers" />
      </section>
    </div>
  </div>
</template>

<script setup>
  import { ref } from 'vue';
  import MetricCard from './MetricCard.vue';
  import DataTable from './DataTable.vue';

  const lastUpdate = ref(new Date().toLocaleTimeString());

  // Dummy Data
  const keyMetrics = ref({
    today: 125,
    month: 2450,
    total: 15230,
  });

  const callStatus = ref({
    answered: 98,
    inQueue: 12,
    onHold: 5,
    hangup: 10,
  });

  const counsellorHeaders = ['Name', 'Status', 'Calls', 'Talk Time'];
  const counsellors = ref([
    ['Alice', 'Available', 25, '02:30:15'],
    ['Bob', 'On Call', 30, '03:10:45'],
    ['Charlie', 'Wrap-up', 22, '01:55:20'],
  ]);

  const callerHeaders = ['Phone Number', 'Status', 'Wait Time', 'Queue'];
  const callers = ref([
    ['Anonymous', 'In Queue', '00:02:15', 'General'],
    ['Anonymous', 'In Queue', '00:01:30', 'Support'],
    ['Anonymous', 'On Hold', '00:05:00', 'General'],
  ]);

  // Update last update time every second for demonstration
  setInterval(() => {
    lastUpdate.value = new Date().toLocaleTimeString();
  }, 1000);
</script>

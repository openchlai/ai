<template>
  <div class="p-6 bg-gray-50 min-h-screen">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-bold text-gray-800">Cases</h1>
      <div class="flex gap-2">
        <button
          :class="[
            'px-4 py-2 rounded-md font-medium',
            currentView === 'table'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-100'
          ]"
          @click="currentView = 'table'"
        >
          Table View
        </button>
        <button
          :class="[
            'px-4 py-2 rounded-md font-medium',
            currentView === 'timeline'
              ? 'bg-blue-600 text-white'
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-100'
          ]"
          @click="currentView = 'timeline'"
        >
          Timeline View
        </button>
      </div>
    </div>

    <!-- Loader -->
    <div v-if="casesStore.loading" class="text-center py-20 text-gray-600">
      Loading cases...
    </div>

    <!-- Error -->
    <div v-else-if="casesStore.error" class="text-center py-20 text-red-600">
      {{ casesStore.error }}
    </div>

    <!-- Data -->
    <div v-else>
      <Table
        v-if="currentView === 'table'"
        :cases="casesStore.cases"
        :cases_k="casesStore.cases_k"
      />
      <Timeline
        v-else
        :cases="casesStore.cases"
        :cases_k="casesStore.cases_k"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useCaseStore } from '@/stores/cases';
import Table from '@/components/cases/Table.vue';
import Timeline from '@/components/cases/Timeline.vue';

const casesStore = useCaseStore();
const currentView = ref('table');

onMounted(async () => {
  try {
    await casesStore.listCases({ limit: 50 });
  } catch (err) {
    console.error('Failed to fetch cases:', err);
  }
});
</script>

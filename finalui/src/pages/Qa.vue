<template>
  <div class="p-6 space-y-4">
    <div class="flex justify-between items-center">
      <h1 class="text-xl font-semibold text-gray-700">QA Results</h1>
      <button
        @click="fetchQA"
        class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
      >
        Refresh
      </button>
    </div>

    <div v-if="qaStore.loading" class="text-gray-500 italic">Loading...</div>
    <div v-else-if="qaStore.error" class="text-red-500">{{ qaStore.error }}</div>

    <Table
      v-if="qaStore.qas && qaStore.qas.length"
      :qas="qaStore.qas"
      :qas_k="qaStore.qas_k"
    />

    <p v-else class="text-gray-400 italic">No QA results found.</p>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useQAStore } from '@/stores/qas'
import Table from '@/components/qas/Table.vue'

const qaStore = useQAStore()

const fetchQA = async () => {
  await qaStore.listQA()
}

onMounted(fetchQA)
</script>

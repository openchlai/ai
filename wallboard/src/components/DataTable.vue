<template>
  <div
    class="bg-white dark:bg-gray-900 rounded-2xl shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
    <!-- Table Container -->
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <!-- Header -->
        <thead class="bg-gradient-to-r from-indigo-500 to-purple-600 text-white">
          <tr>
            <th v-for="header in headers" :key="header" scope="col"
              class="px-6 py-3 text-left text-sm font-semibold uppercase tracking-wider">
              {{ header }}
            </th>
          </tr>
        </thead>

        <!-- Body -->
        <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-for="(row, rowIndex) in paginatedData" :key="rowIndex"
            class="cursor-pointer odd:bg-gray-50 even:bg-white dark:odd:bg-gray-800 dark:even:bg-gray-900 hover:bg-indigo-50 dark:hover:bg-indigo-900 transition"
            @click="$emit('rowClick', row)">
            <td v-for="(cell, cellIndex) in row" :key="cellIndex"
              class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-gray-100">
              <!-- Status Badge -->
              <span v-if="headers[cellIndex] === 'Status'" :class="[
                'inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded',
                cell === 'Active'
                  ? 'bg-green-100 text-green-800'
                  : cell === 'Offline'
                    ? 'bg-red-100 text-red-800'
                    : cell === 'Busy'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-200',
              ]">
                <svg v-if="cell === 'Active'" class="w-3 h-3 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414L8.414 15l-4.121-4.121a1 1 0 111.414-1.414L8.414 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clip-rule="evenodd" />
                </svg>
                <svg v-else-if="cell === 'Offline'" class="w-3 h-3 text-red-600" fill="currentColor"
                  viewBox="0 0 20 20">
                  <path fill-rule="evenodd"
                    d="M10 9V5a1 1 0 112 0v4h4a1 1 0 110 2h-4v4a1 1 0 11-2 0v-4H6a1 1 0 110-2h4z" clip-rule="evenodd" />
                </svg>
                <svg v-else-if="cell === 'Busy'" class="w-3 h-3 text-yellow-600" fill="currentColor"
                  viewBox="0 0 20 20">
                  <path fill-rule="evenodd"
                    d="M18 10c0 4.418-3.582 8-8 8S2 14.418 2 10 5.582 2 10 2s8 3.582 8 8zm-7 0V6a1 1 0 10-2 0v5a1 1 0 00.293.707l3 3a1 1 0 101.414-1.414L11 10z"
                    clip-rule="evenodd" />
                </svg>
                {{ cell }}
              </span>
              <!-- Default Cell -->
              <span v-else>{{ cell }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Footer -->
    <div
      class="px-6 py-3 bg-gray-100 dark:bg-gray-800 flex justify-between items-center text-xs text-gray-600 dark:text-gray-400">
      <span>Showing {{ paginatedData.length }} of {{ data.length }} records</span>
      <div class="space-x-2">
        <button @click="prevPage" :disabled="page === 1"
          class="px-3 py-1 rounded bg-gray-200 dark:bg-gray-700 disabled:opacity-50">
          Prev
        </button>
        <button @click="nextPage" :disabled="page === totalPages"
          class="px-3 py-1 rounded bg-gray-200 dark:bg-gray-700 disabled:opacity-50">
          Next
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { computed, ref } from 'vue'

  const props = defineProps({
    headers: {
      type: Array,
      required: true,
    },
    data: {
      type: Array,
      required: true,
    },
    perPage: {
      type: Number,
      default: 5,
    },
  })

  /* Pagination logic */
  const page = ref(1)
  const totalPages = computed(() => Math.ceil(props.data.length / props.perPage))

  const paginatedData = computed(() => {
    const start = (page.value - 1) * props.perPage
    return props.data.slice(start, start + props.perPage)
  })

  const nextPage = () => {
    if (page.value < totalPages.value) page.value++
  }

  const prevPage = () => {
    if (page.value > 1) page.value--
  }
</script>

<style scoped>

  /* Mobile responsive: turn table into cards */
  @media (max-width: 640px) {
    table thead {
      display: none;
    }

    table tbody tr {
      display: block;
      margin-bottom: 1rem;
      border: 1px solid #e5e7eb;
      border-radius: 0.75rem;
      padding: 0.75rem;
    }

    table tbody td {
      display: flex;
      justify-content: space-between;
      padding: 0.5rem 0;
    }
  }
</style>
 
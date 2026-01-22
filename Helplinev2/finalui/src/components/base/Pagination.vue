<template>
  <div
    v-if="paginationInfo.total > 0"
    class="flex justify-between items-center mt-6 p-4 rounded-xl"
    :class="isDarkMode ? 'bg-gray-800' : 'bg-white shadow'"
  >
    <!-- Page Info -->
    <div
      class="text-sm"
      :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
    >
      Page {{ paginationInfo.currentPage }} of {{ paginationInfo.totalPages }}
    </div>

    <!-- Pagination Buttons -->
    <div class="flex items-center gap-2">
      <!-- Previous Button -->
      <button
        @click="$emit('prev')"
        :disabled="!hasPrevPage || loading"
        :class="[
          'px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-1 text-sm',
          hasPrevPage && !loading
            ? isDarkMode
              ? 'bg-gray-700 text-gray-200 hover:bg-gray-600'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            : 'opacity-50 cursor-not-allowed ' + (isDarkMode ? 'bg-gray-800 text-gray-500' : 'bg-gray-100 text-gray-400')
        ]"
      >
        <i-mdi-chevron-left class="w-5 h-5" />
        Previous
      </button>

      <!-- Page Numbers -->
      <div class="flex items-center gap-1">
        <template v-for="page in visiblePages" :key="page">
          <button
            v-if="page !== '...'"
            @click="$emit('goToPage', page)"
            :disabled="loading"
            :class="[
              'w-10 h-10 rounded-lg font-medium transition-all duration-200 text-sm',
              page === paginationInfo.currentPage
                ? isDarkMode
                  ? 'bg-amber-600 text-white'
                  : 'bg-amber-700 text-white'
                : isDarkMode
                  ? 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            ]"
          >
            {{ page }}
          </button>
          <span
            v-else
            class="px-2"
            :class="isDarkMode ? 'text-gray-500' : 'text-gray-400'"
          >
            ...
          </span>
        </template>
      </div>

      <!-- Next Button -->
      <button
        @click="$emit('next')"
        :disabled="!hasNextPage || loading"
        :class="[
          'px-4 py-2 rounded-lg font-medium transition-all duration-200 flex items-center gap-1 text-sm',
          hasNextPage && !loading
            ? isDarkMode
              ? 'bg-gray-700 text-gray-200 hover:bg-gray-600'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            : 'opacity-50 cursor-not-allowed ' + (isDarkMode ? 'bg-gray-800 text-gray-500' : 'bg-gray-100 text-gray-400')
        ]"
      >
        Next
        <i-mdi-chevron-right class="w-5 h-5" />
      </button>
    </div>

    <!-- Page Size Selector -->
    <div class="flex items-center gap-2">
      <span
        class="text-sm"
        :class="isDarkMode ? 'text-gray-400' : 'text-gray-600'"
      >
        Per page:
      </span>
      <select
        :value="pageSize"
        @change="$emit('changePageSize', Number($event.target.value))"
        :class="[
          'px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 cursor-pointer',
          isDarkMode
            ? 'bg-gray-700 text-gray-200 border-gray-600'
            : 'bg-gray-100 text-gray-700 border-gray-200'
        ]"
      >
        <option :value="10">10</option>
        <option :value="20">20</option>
        <option :value="50">50</option>
        <option :value="100">100</option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { computed, inject } from 'vue'

const props = defineProps({
  paginationInfo: {
    type: Object,
    required: true
  },
  hasNextPage: {
    type: Boolean,
    default: false
  },
  hasPrevPage: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  pageSize: {
    type: Number,
    default: 20
  }
})

defineEmits(['prev', 'next', 'goToPage', 'changePageSize'])

const isDarkMode = inject('isDarkMode')

// Compute visible page numbers for pagination
const visiblePages = computed(() => {
  const { currentPage, totalPages } = props.paginationInfo
  const pages = []
  const maxVisible = 5

  if (totalPages <= maxVisible) {
    for (let i = 1; i <= totalPages; i++) {
      pages.push(i)
    }
  } else {
    // Always show first page
    pages.push(1)

    if (currentPage > 3) {
      pages.push('...')
    }

    // Show pages around current
    const start = Math.max(2, currentPage - 1)
    const end = Math.min(totalPages - 1, currentPage + 1)

    for (let i = start; i <= end; i++) {
      if (!pages.includes(i)) {
        pages.push(i)
      }
    }

    if (currentPage < totalPages - 2) {
      pages.push('...')
    }

    // Always show last page
    if (!pages.includes(totalPages)) {
      pages.push(totalPages)
    }
  }

  return pages
})
</script>

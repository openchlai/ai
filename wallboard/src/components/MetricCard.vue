<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4 text-center">
    <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ title }}</h3>
    <p class="mt-1 text-3xl font-semibold text-gray-900 dark:text-white" :class="colorClass">
      {{ value }}
    </p>
  </div>
</template>

<script setup>
  defineProps({
    title: {
      type: String,
      required: true,
    },
    value: {
      type: [String, Number],
      required: true,
    },
    colorClass: {
      type: String,
      default: '',
    },
  })
</script>

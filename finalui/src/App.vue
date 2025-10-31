<template>
  <div id="app" class="min-h-screen font-sans text-gray-900 bg-gray-50">
    <component :is="layout" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DefaultLayout from '@/layout/DefaultLayout.vue'
import { RouterView } from 'vue-router'

const route = useRoute()

// Dynamically choose layout
const layout = computed(() => {
  if (route.meta.layout === 'none') return RouterView // for Login
  return DefaultLayout // for all protected pages
})
</script>

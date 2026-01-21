<template>
  <div class="flex min-h-screen">
    <Sidebar />
    <main class="flex-1 bg-gray-50 p-6 overflow-auto">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import Sidebar from '@/components/layout/Sidebar.vue'
</script>

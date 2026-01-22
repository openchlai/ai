<template>
  <div class="flex min-h-screen" :class="isDarkMode ? 'bg-gray-900' : 'bg-gray-50'">
    <!-- Fixed Sidebar - Only show when NOT on login page -->
    <Sidebar v-if="showSidebar" :isDarkMode="isDarkMode" @toggle-theme="toggleTheme" />
    
    <!-- Main Content Area with conditional left margin -->
    <main 
      class="flex-1 overflow-auto" 
      :class="[
        showSidebar ? 'ml-64' : '',
        isDarkMode ? 'bg-gray-900' : 'bg-gray-50'
      ]"
    >
      <div>
        <RouterView />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, provide } from 'vue'
import { useRoute } from 'vue-router'
import { useTheme } from '@/composables/useTheme'
import Sidebar from '@/components/layout/Sidebar.vue'

const route = useRoute()
const { isDarkMode, toggleTheme } = useTheme()

// Provide theme to all child components
provide('isDarkMode', isDarkMode)
provide('toggleTheme', toggleTheme)

// Hide sidebar on login page
const showSidebar = computed(() => {
  return route.path !== '/login'
})
</script>
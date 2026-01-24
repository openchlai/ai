<template>
  <div class="flex min-h-screen" :class="isDarkMode ? 'bg-black' : 'bg-gray-50'">
    <!-- Fixed Sidebar - Only show when NOT on login page -->
    <Sidebar v-if="showSidebar" :isDarkMode="isDarkMode" @toggle-theme="toggleTheme" />
    
    <!-- Main Content Area with conditional left margin -->
    <div 
      class="flex-1 flex flex-col min-h-screen relative" 
      :class="[
        showSidebar ? 'ml-64' : '',
        isDarkMode ? 'bg-black' : 'bg-gray-50'
      ]"
    >
      <!-- Static Navbar -->
      <Navbar v-if="showSidebar" :isDarkMode="isDarkMode" />

      <!-- Main Content Container -->
      <main class="flex-1 overflow-auto p-6">
        <RouterView />
      </main>
    </div>
<<<<<<< HEAD

    <!-- Global Active Call Toolbar -->
    <ActiveCallToolbar />
=======
>>>>>>> main
  </div>
</template>

<script setup>
import { computed, provide } from 'vue'
import { useRoute } from 'vue-router'
import { useTheme } from '@/composables/useTheme'
import Sidebar from '@/components/layout/Sidebar.vue'
import Navbar from '@/components/layout/Navbar.vue'

import Navbar from '@/components/layout/Navbar.vue'
import ActiveCallToolbar from '@/components/softphone/ActiveCallToolbar.vue'

const route = useRoute()
const { isDarkMode, toggleTheme } = useTheme()

// Provide theme to all child components
provide('isDarkMode', isDarkMode)
provide('toggleTheme', toggleTheme)

<<<<<<< HEAD

=======
>>>>>>> main
// Hide sidebar and navbar on login page
const showSidebar = computed(() => {
  return route.path !== '/login'
})
</script>
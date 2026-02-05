<template>
  <div 
    class="flex flex-col lg:flex-row gap-6 p-2 lg:p-6 min-h-screen transition-colors duration-300"
    :class="isDarkMode ? 'bg-gray-950' : 'bg-gray-50'"
  >
    <!-- Left Sidebar -->
    <aside class="w-full lg:w-80 xl:w-96 space-y-6 shrink-0">
      <slot name="sidebar"></slot>
    </aside>

    <!-- Main Content -->
    <main class="flex-1 flex flex-col gap-6 min-w-0">
      <!-- Primary Case Details -->
      <div 
        class="p-6 rounded-xl shadow-sm border transition-all duration-300"
        :class="isDarkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-100'"
      >
        <slot name="main"></slot>
      </div>

      <!-- Lower Section -->
      <div 
        class="p-6 rounded-xl shadow-sm border transition-all duration-300"
        :class="isDarkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-gray-100'"
      >
        <slot name="lower"></slot>
      </div>

      <!-- Footer & Actions -->
      <div 
        class="p-6 rounded-xl shadow-sm border transition-all duration-300 sticky bottom-4 z-10"
        :class="isDarkMode ? 'bg-gray-900 border-gray-800 shadow-xl' : 'bg-white border-gray-100 shadow-lg'"
      >
        <slot name="footer"></slot>
      </div>
    </main>

    <!-- Right Sidebar (AI Assistant) -->
    <aside v-if="$slots['right-sidebar']" class="w-full lg:w-80 xl:w-96 space-y-6 shrink-0">
      <slot name="right-sidebar"></slot>
    </aside>
  </div>
</template>

<script setup>
import { inject } from 'vue';

const isDarkMode = inject('isDarkMode');
</script>

<template>
  <div class="flex flex-col lg:flex-row gap-6 p-2 lg:p-6 min-h-screen bg-gray-50 dark:bg-black transition-colors duration-300">
    <!-- Left Sidebar -->
    <aside class="w-full lg:w-1/3 xl:w-1/4 space-y-6">
      <slot name="sidebar"></slot>
    </aside>

    <!-- Main Content -->
    <main class="w-full lg:w-2/3 xl:w-3/4 flex flex-col gap-6">
      <!-- Primary Case Details -->
      <div 
        class="p-6 rounded-xl shadow-sm border transition-all duration-300"
        :class="isDarkMode ? 'bg-neutral-900 border-neutral-800' : 'bg-white border-gray-100'"
      >
        <slot name="main"></slot>
      </div>

      <!-- Lower Section -->
      <div 
        class="p-6 rounded-xl shadow-sm border transition-all duration-300"
        :class="isDarkMode ? 'bg-neutral-900 border-neutral-800' : 'bg-white border-gray-100'"
      >
        <slot name="lower"></slot>
      </div>

      <!-- Footer & Actions -->
      <div 
        class="p-6 rounded-xl shadow-sm border transition-all duration-300 sticky bottom-4 z-10"
        :class="isDarkMode ? 'bg-neutral-900 border-neutral-800 shadow-xl' : 'bg-white border-gray-100 shadow-lg'"
      >
        <slot name="footer"></slot>
      </div>
    </main>
  </div>
</template>

<script setup>
import { inject } from 'vue';

const isDarkMode = inject('isDarkMode');
</script>

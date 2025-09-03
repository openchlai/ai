<template>
  <router-view />
  
  
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { applyTheme, getCurrentTheme } from '@/utils/theme.js'

const isReading = ref(false)
const currentTheme = ref('dark')

function readAloud() {}

function toggleTheme() {
  currentTheme.value = currentTheme.value === 'dark' ? 'light' : 'dark'
  localStorage.setItem('theme', currentTheme.value)
  applyTheme(currentTheme.value)
}

onMounted(() => {
  const saved = localStorage.getItem('theme') || getCurrentTheme() || 'dark'
  currentTheme.value = saved
  applyTheme(currentTheme.value)
})
</script>

<style>
html, body, #app {
  height: auto;
  min-height: 100vh;
  overflow: auto;
}
body, #app {
  background: var(--background-color, #fff);
  color: var(--text-color, #222);
  margin: 0;
  padding: 0;
}
 
</style>

import { ref, watch } from 'vue'

// Initialize from localStorage or default to light mode
const isDarkMode = ref(localStorage.getItem('theme') === 'dark')

export function useTheme() {
  const toggleTheme = () => {
    isDarkMode.value = !isDarkMode.value
  }

  // Watch and persist theme changes
  watch(isDarkMode, (newValue) => {
    localStorage.setItem('theme', newValue ? 'dark' : 'light')
    
    // Update document class for global styling if needed
    if (newValue) {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }, { immediate: true })

  return {
    isDarkMode,
    toggleTheme
  }
}
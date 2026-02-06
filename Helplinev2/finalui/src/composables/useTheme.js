import { ref, watch } from 'vue'

const getSystemPreference = () => window.matchMedia('(prefers-color-scheme: dark)').matches

// Determine initial state: Storage > System
const storedTheme = localStorage.getItem('theme')
const initialValue = storedTheme ? storedTheme === 'dark' : getSystemPreference()

const isDarkMode = ref(initialValue)

// Listen for system changes (PC/Mac settings)
const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
const handler = (e) => {
  // Only update automatically if user hasn't manually set a preference in this session/browser
  if (!localStorage.getItem('theme')) {
    isDarkMode.value = e.matches
  }
}

// support modern and safe fallback
if (mediaQuery && mediaQuery.addEventListener) {
  mediaQuery.addEventListener('change', handler)
}

export function useTheme() {
  const toggleTheme = () => {
    isDarkMode.value = !isDarkMode.value
    // Persist user choice implies manual override
    localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light')
  }

  // Watch and apply
  watch(isDarkMode, (newValue) => {
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
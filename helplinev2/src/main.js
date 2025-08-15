import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import { router } from './router'
import { applyTheme } from './utils/theme.js'

const app = createApp(App)
const pinia = createPinia()

// Add error handling
app.config.errorHandler = (err, vm, info) => {
  console.error('Vue Error:', err)
  console.error('Error Info:', info)
}

// Add global error handler
window.addEventListener('error', (event) => {
  console.error('Global Error:', event.error)
})

app.use(pinia)
app.use(router)

// On app startup, set the theme globally
const savedTheme = localStorage.getItem('theme') || 'dark';
applyTheme(savedTheme);

// Add debugging
console.log('Mounting app...')
app.mount('#app')
console.log('App mounted')

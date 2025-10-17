import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'


// this is the latest i have made it possible 

export default defineConfig({
  plugins: [vue()],
  base: '/wallboard-new/',
  server: {
    port: 3000,
    open: true
  }
})

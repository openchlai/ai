import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    open: true,
    hmr: true
  },
  build: {
    sourcemap: true
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
<<<<<<< HEAD
=======
  },
  // Testing configuration
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./src/test-setup.js'],
    include: [
      'src/**/*.{test,spec}.{js,ts}',
      'src/**/__tests__/**/*.{js,ts}'
    ],
    exclude: [
      'node_modules',
      'dist',
      'coverage',
      'public'
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      reportsDirectory: './coverage',
      exclude: [
        'node_modules/',
        'dist/',
        'coverage/',
        'public/',
        '**/*.config.js',
        '**/*.config.ts',
        'src/test-setup.js',
        'src/main.js'
      ],
      thresholds: {
        lines: 90,
        functions: 90,
        branches: 90,
        statements: 90
      },
      all: true,
      src: ['src']
    }
>>>>>>> f2457c087bd9919b681a4048be71e6ebd3b765e1
  }
})
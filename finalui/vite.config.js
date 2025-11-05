import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';
import Icons from 'unplugin-icons/vite'
import IconsResolver from 'unplugin-icons/resolver'
import Components from 'unplugin-vue-components/vite'

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(),
    Icons(),
    Components({
      resolvers: [IconsResolver()],
    }),
  ],

  server: {
    port: 5173,
    host: '0.0.0.0', // allow access from all interfaces
    open: true,
    hmr: true,
    cors: true, // important for dev CORS
    proxy: {
      '/api-proxy': {
        target: 'https://demo-openchs.bitz-itc.com',
        changeOrigin: true, // rewrite Host header
        secure: false,      // allow self-signed SSL
        rewrite: (path) => path.replace(/^\/api-proxy/, '/helpline'),
        configure: (proxy) => {
          proxy.on('proxyReq', (_proxyReq, req) => {
            console.log(`[proxy] ${req.method} ${req.url} -> ${proxy.target}${req.url}`);
          });
        },
      },
    },
  },

  build: {
    sourcemap: true, // enable source maps
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});

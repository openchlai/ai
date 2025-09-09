import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';


export default defineConfig({
  plugins: [vue()],

  server: {
    port: 3000,
    host: '0.0.0.0', // This allows access from any network interface
    open: true,
    hmr: true,
    proxy: {
      // Any request that starts with /api-proxy will be proxied
      // e.g. GET /api-proxy/auth/login --> https://demo-openchs.bitz-itc.com/helpline/auth/login
      '/api-proxy': {
        target: 'https://demo-openchs.bitz-itc.com',
        // target: 'https://system.childlinekenya.co.ke/helpline',
        changeOrigin: true,     // rewrite Host header to target
        secure: false,          // allow self‑signed SSL certs
        rewrite: (path) => path.replace(/^\/api-proxy/, '/helpline'),
        // Vite uses 'rewrite', not 'pathRewrite'
        // Same effect: strip "/api-proxy" and prepend "/helpline"
        configure: (proxy/*, options */) => {
          // Optional: verbose logging similar to logLevel:'debug'
          proxy.on('proxyReq', (_proxyReq, req) => {
            console.log(`[proxy] ${req.method} ${req.url} -> ${proxy.target}${req.url}`);
          });
        },
      },
    },
  },
  build: {
    sourcemap: true,
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});

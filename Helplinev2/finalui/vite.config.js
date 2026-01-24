import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';
import Icons from 'unplugin-icons/vite'
import IconsResolver from 'unplugin-icons/resolver'
import Components from 'unplugin-vue-components/vite'

export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, process.cwd(), '');

  return {
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
          target: env.VITE_BACKEND_URL || 'https://demo-openchs.bitz-itc.com',
          changeOrigin: true, // rewrite Host header
          secure: false,      // allow self-signed SSL
          rewrite: (path) => path.replace(/^\/api-proxy/, env.VITE_BACKEND_PATH || '/helpline'),
          configure: (proxy) => {
            proxy.on('proxyReq', (_proxyReq, req) => {
              console.log(`[proxy] ${req.method} ${req.url} -> ${proxy.target}${req.url}`);
            });
          },
        },
        '/ws': {
          target: env.VITE_BACKEND_URL || 'https://demo-openchs.bitz-itc.com',
          ws: true,
          changeOrigin: true,
          secure: false,
          configure: (proxy) => {
            proxy.on('proxyReqWs', (proxyReq, req, socket, options, head) => {
              console.log(`[proxy-ws] WS connection ${req.url} -> ${options.target}`);
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
        'vue': 'vue/dist/vue.esm-bundler.js',
      },
    },
  };
});
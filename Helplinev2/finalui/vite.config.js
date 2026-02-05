import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';
import Icons from 'unplugin-icons/vite'
import IconsResolver from 'unplugin-icons/resolver'
import Components from 'unplugin-vue-components/vite'
import { ENVIRONMENT_REGISTRY } from './src/config/taxonomyContract'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const country = (env.VITE_DEFAULT_COUNTRY || 'TZ').toUpperCase();
  const config = ENVIRONMENT_REGISTRY[country] || ENVIRONMENT_REGISTRY['DEMO'];
  const endpoints = config.ENDPOINTS;

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
      host: '0.0.0.0',
      open: true,
      hmr: true,
      cors: true,
      proxy: {
        '/api-proxy': {
          target: endpoints.DEV_TARGET_API,
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api-proxy/, endpoints.BACKEND_PATH || '/helpline'),
          configure: (proxy, options) => {
            proxy.on('proxyReq', (_proxyReq, req) => {
              console.log(`[proxy] ${req.method} ${req.url} -> ${options.target}${req.url}`);
            });
          },
        },
        [endpoints.ATI_WS_PATH || '/ati/sync']: {
          target: endpoints.DEV_TARGET_ATI,
          changeOrigin: true,
          secure: false,
          configure: (proxy, options) => {
            proxy.on('proxyReq', (proxyReq, req) => {
              console.log(`[proxy-ati] ${req.method} ${req.url} -> ${options.target}${req.url}`);
            });
          },
        },
        [endpoints.AMI_WS_PATH || '/ami/sync']: {
          target: endpoints.DEV_TARGET_AMI,
          ws: true,
          changeOrigin: true,
          secure: false,
          configure: (proxy, options) => {
            proxy.on('proxyReqWs', (proxyReq, req, socket, options, head) => {
              console.log(`[proxy-ami] WS connection ${req.url} -> ${options.target}`);
            });
          },
        },
        [endpoints.SIP_WS_PATH || '/ws/']: {
          target: endpoints.DEV_TARGET_SIP,
          ws: true,
          changeOrigin: true,
          secure: false,
          configure: (proxy, options) => {
            proxy.on('proxyReqWs', (proxyReq, req, socket, options, head) => {
              console.log(`[proxy-ws] WS connection ${req.url} -> ${options.target}`);
            });
          },
        },
        '/audio-api': {
          target: 'http://192.168.8.18:8125',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/audio-api/, ''),
        },
      },
    },

    build: {
      sourcemap: true,
    },

    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        'vue': 'vue/dist/vue.esm-bundler.js',
      },
    },
  };
});
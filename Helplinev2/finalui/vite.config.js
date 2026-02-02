import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import tailwindcss from '@tailwindcss/vite';
import path from 'path';
import Icons from 'unplugin-icons/vite'
import IconsResolver from 'unplugin-icons/resolver'
import Components from 'unplugin-vue-components/vite'
import https from 'https';
import dns from 'dns';

// Force IPv4 first to avoid IPv6 timeout issues
dns.setDefaultResultOrder('ipv4first');

export default defineConfig(({ mode }) => {
  // Load env file based on `mode` in the current working directory.
  const env = loadEnv(mode, path.resolve(__dirname), '');

  // Create HTTPS agent that forces IPv4
  const httpsAgent = new https.Agent({
    family: 4, // Force IPv4
    rejectUnauthorized: false
  });

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
          agent: httpsAgent,  // Use IPv4 agent
          rewrite: (path) => path.replace(/^\/api-proxy/, env.VITE_BACKEND_PATH || '/helpline'),
          configure: (proxy, options) => {
            proxy.on('proxyReq', (_proxyReq, req) => {
              console.log(`[proxy] ${req.method} ${req.url} -> ${options.target}${req.url}`);
            });
          },
        },
        '/ati': {
          target: (() => {
            if (env.VITE_ATI_URL) return env.VITE_ATI_URL;
            try {
              const backend = new URL(env.VITE_BACKEND_URL || 'https://demo-openchs.bitz-itc.com');
              return `${backend.protocol}//${backend.hostname}:8384`;
            } catch (e) {
              return 'https://demo-openchs.bitz-itc.com:8384';
            }
          })(),
          changeOrigin: true,
          secure: false, // allow self-signed SSL
          agent: httpsAgent, // Use IPv4 agent
          configure: (proxy, options) => {
            proxy.on('proxyReq', (proxyReq, req) => {
              console.log(`[proxy-ati] ${req.method} ${req.url} -> ${options.target}${req.url}`);

              // Add Basic Auth if credentials are present
              const username = env.VITE_ASTERISK_USERNAME;
              const password = env.VITE_ASTERISK_PASSWORD || env.VITE_VA_SIP_PASS_PREFIX;

              if (username && password) {
                const auth = Buffer.from(`${username}:${password}`).toString('base64');
                proxyReq.setHeader('Authorization', `Basic ${auth}`);
              }
            });
          },
        },
        '/ws': {
          target: (() => {
            if (env.VITE_SIP_WS_URL) {
              try {
                const url = new URL(env.VITE_SIP_WS_URL);
                return `${url.protocol === 'wss:' ? 'https:' : 'http:'}//${url.host}`;
              } catch (e) {
                // Fallback if parsing fails
              }
            }
            return env.VITE_BACKEND_URL || 'https://demo-openchs.bitz-itc.com';
          })(),
          ws: true,
          changeOrigin: true,
          secure: false,
          agent: httpsAgent, // Use IPv4 agent
          configure: (proxy, options) => {
            proxy.on('proxyReqWs', (_proxyReq, req, _socket, _head) => {
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

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'


// this is the latest i have made it possible 

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, process.cwd(), '')
    const apiTarget = env.VITE_API_TARGET || 'http://192.168.10.3'
    const wsTarget = env.VITE_WS_TARGET || 'wss://192.168.10.3:8384'
    const prodWsUrl = env.VITE_PROD_WS_URL || 'wss://helpline.sematanzania.org/ami/sync?c=-2'
    const agentStatusTarget = env.VITE_AGENT_STATUS_TARGET || 'http://192.168.10.3:8383'
    const appBaseUrl = mode === 'development' ? '/api-proxy' : '/wallboard'
    const agentStatusUrl = mode === 'development' ? '/agent-proxy' : '/ami'

    // Determine WS URL based on environment
    const appWsUrl = mode === 'development'
        ? `${env.VITE_DEV_WS_PROTOCOL || 'ws'}://${env.VITE_DEV_HOST || 'localhost'}:${env.VITE_DEV_PORT || '3000'}/ws-proxy/sync?c=-2`
        : prodWsUrl

    return {
        base: './',
        define: {
            __APP_API_BASE_URL__: JSON.stringify(appBaseUrl),
            __APP_WS_URL__: JSON.stringify(appWsUrl),
            __APP_AGENT_STATUS_URL__: JSON.stringify(agentStatusUrl)
        },
        plugins: [vue()],
        server: {
            port: 3000,
            host: '0.0.0.0',
            open: true,
            hmr: true,
            proxy: {
                '/api-proxy': {
                    target: apiTarget,
                    changeOrigin: true,
                    secure: false,
                    rewrite: (path) => path.replace(/^\/api-proxy/, '/helpline/api/wallonly'),
                    configure: (proxy, options) => {
                        proxy.on('proxyReq', (_proxyReq, req) => {
                            console.log(`[proxy] ${req.method} ${req.url} -> ${proxy.target}${req.url}`);
                        });
                    },
                },
                '/ws-proxy': {
                    target: wsTarget.replace('https://', 'wss://').replace('http://', 'ws://'),
                    changeOrigin: true,
                    secure: false,
                    ws: true,
                    rewrite: (path) => path.replace(/^\/ws-proxy/, '/ami'),
                    headers: {
                        'Connection': 'Upgrade'
                    },
                    configure: (proxy, _options) => {
                        proxy.on('error', (err, _req, _res) => {
                            console.log('proxy websocket error', err);
                        });
                        proxy.on('proxyReqWs', (_proxyReq, _req, _socket, _options, _head) => {
                            console.log('[proxy-ws] Connecting to target WebSocket:', wsTarget);
                        });
                    },
                },
                '/agent-proxy': {
                    target: agentStatusTarget,
                    changeOrigin: true,
                    secure: false,
                    rewrite: (path) => path.replace(/^\/agent-proxy/, '/ami'),
                    configure: (proxy, options) => {
                        proxy.on('proxyReq', (_proxyReq, req) => {
                            console.log(`[agent-proxy] ${req.method} ${req.url} -> ${proxy.target}${req.url}`);
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
    }
});
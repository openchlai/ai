import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
    plugins: [vue()],
    server: {
        port: 3000,
        host: '0.0.0.0',
        open: true,
        hmr: true,
        proxy: {
            '/api-proxy': {
                target: 'https://demo-openchs.bitz-itc.com/helpline',
                changeOrigin: true,
                secure: false,
                rewrite: (path) => path.replace(/^\/api-proxy/, '/helpline'),
                configure: (proxy, options) => {
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


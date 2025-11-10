// vite.config.js
import { defineConfig } from "file:///C:/Users/LENOVO/Desktop/job/open%20ai/main%20ai/main/ai/wallboard/node_modules/vite/dist/node/index.js";
import vue from "file:///C:/Users/LENOVO/Desktop/job/open%20ai/main%20ai/main/ai/wallboard/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import path from "path";
var __vite_injected_original_dirname = "C:\\Users\\LENOVO\\Desktop\\job\\open ai\\main ai\\main\\ai\\wallboard";
var vite_config_default = defineConfig({
  plugins: [vue()],
  server: {
    port: 3e3,
    host: "0.0.0.0",
    open: true,
    hmr: true,
    proxy: {
      "/api-proxy": {
        // target: 'https://demo-openchs.bitz-itc.com',
        target: "https://helpline.sematanzania.org",
        changeOrigin: true,
        secure: false,
        rewrite: (path2) => path2.replace(/^\/api-proxy/, "/helpline"),
        configure: (proxy, options) => {
          proxy.on("proxyReq", (_proxyReq, req) => {
            console.log(`[proxy] ${req.method} ${req.url} -> ${proxy.target}${req.url}`);
          });
        }
      }
    }
  },
  build: {
    sourcemap: true
  },
  resolve: {
    alias: {
      "@": path.resolve(__vite_injected_original_dirname, "./src")
    }
  }
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcuanMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJDOlxcXFxVc2Vyc1xcXFxMRU5PVk9cXFxcRGVza3RvcFxcXFxqb2JcXFxcb3BlbiBhaVxcXFxtYWluIGFpXFxcXG1haW5cXFxcYWlcXFxcd2FsbGJvYXJkXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCJDOlxcXFxVc2Vyc1xcXFxMRU5PVk9cXFxcRGVza3RvcFxcXFxqb2JcXFxcb3BlbiBhaVxcXFxtYWluIGFpXFxcXG1haW5cXFxcYWlcXFxcd2FsbGJvYXJkXFxcXHZpdGUuY29uZmlnLmpzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9DOi9Vc2Vycy9MRU5PVk8vRGVza3RvcC9qb2Ivb3BlbiUyMGFpL21haW4lMjBhaS9tYWluL2FpL3dhbGxib2FyZC92aXRlLmNvbmZpZy5qc1wiO2ltcG9ydCB7IGRlZmluZUNvbmZpZyB9IGZyb20gJ3ZpdGUnXHJcbmltcG9ydCB2dWUgZnJvbSAnQHZpdGVqcy9wbHVnaW4tdnVlJ1xyXG5pbXBvcnQgcGF0aCBmcm9tICdwYXRoJ1xyXG5cclxuZXhwb3J0IGRlZmF1bHQgZGVmaW5lQ29uZmlnKHtcclxuICAgIHBsdWdpbnM6IFt2dWUoKV0sXHJcbiAgICBzZXJ2ZXI6IHtcclxuICAgICAgICBwb3J0OiAzMDAwLFxyXG4gICAgICAgIGhvc3Q6ICcwLjAuMC4wJyxcclxuICAgICAgICBvcGVuOiB0cnVlLFxyXG4gICAgICAgIGhtcjogdHJ1ZSxcclxuICAgICAgICBwcm94eToge1xyXG4gICAgICAgICAgICAnL2FwaS1wcm94eSc6IHtcclxuICAgICAgICAgICAgICAgIC8vIHRhcmdldDogJ2h0dHBzOi8vZGVtby1vcGVuY2hzLmJpdHotaXRjLmNvbScsXHJcbiAgICAgICAgICAgICAgICB0YXJnZXQ6ICdodHRwczovL2hlbHBsaW5lLnNlbWF0YW56YW5pYS5vcmcnLFxyXG4gICAgICAgICAgICAgICAgY2hhbmdlT3JpZ2luOiB0cnVlLFxyXG4gICAgICAgICAgICAgICAgc2VjdXJlOiBmYWxzZSxcclxuICAgICAgICAgICAgICAgIHJld3JpdGU6IChwYXRoKSA9PiBwYXRoLnJlcGxhY2UoL15cXC9hcGktcHJveHkvLCAnL2hlbHBsaW5lJyksXHJcbiAgICAgICAgICAgICAgICBjb25maWd1cmU6IChwcm94eSwgb3B0aW9ucykgPT4ge1xyXG4gICAgICAgICAgICAgICAgICAgIHByb3h5Lm9uKCdwcm94eVJlcScsIChfcHJveHlSZXEsIHJlcSkgPT4ge1xyXG4gICAgICAgICAgICAgICAgICAgICAgICBjb25zb2xlLmxvZyhgW3Byb3h5XSAke3JlcS5tZXRob2R9ICR7cmVxLnVybH0gLT4gJHtwcm94eS50YXJnZXR9JHtyZXEudXJsfWApO1xyXG4gICAgICAgICAgICAgICAgICAgIH0pO1xyXG4gICAgICAgICAgICAgICAgfSxcclxuICAgICAgICAgICAgfSxcclxuICAgICAgICB9LFxyXG4gICAgfSxcclxuICAgIGJ1aWxkOiB7XHJcbiAgICAgICAgc291cmNlbWFwOiB0cnVlLFxyXG4gICAgfSxcclxuICAgIHJlc29sdmU6IHtcclxuICAgICAgICBhbGlhczoge1xyXG4gICAgICAgICAgICAnQCc6IHBhdGgucmVzb2x2ZShfX2Rpcm5hbWUsICcuL3NyYycpLFxyXG4gICAgICAgIH0sXHJcbiAgICB9LFxyXG59KTtcclxuXHJcbiJdLAogICJtYXBwaW5ncyI6ICI7QUFBaVksU0FBUyxvQkFBb0I7QUFDOVosT0FBTyxTQUFTO0FBQ2hCLE9BQU8sVUFBVTtBQUZqQixJQUFNLG1DQUFtQztBQUl6QyxJQUFPLHNCQUFRLGFBQWE7QUFBQSxFQUN4QixTQUFTLENBQUMsSUFBSSxDQUFDO0FBQUEsRUFDZixRQUFRO0FBQUEsSUFDSixNQUFNO0FBQUEsSUFDTixNQUFNO0FBQUEsSUFDTixNQUFNO0FBQUEsSUFDTixLQUFLO0FBQUEsSUFDTCxPQUFPO0FBQUEsTUFDSCxjQUFjO0FBQUE7QUFBQSxRQUVWLFFBQVE7QUFBQSxRQUNSLGNBQWM7QUFBQSxRQUNkLFFBQVE7QUFBQSxRQUNSLFNBQVMsQ0FBQ0EsVUFBU0EsTUFBSyxRQUFRLGdCQUFnQixXQUFXO0FBQUEsUUFDM0QsV0FBVyxDQUFDLE9BQU8sWUFBWTtBQUMzQixnQkFBTSxHQUFHLFlBQVksQ0FBQyxXQUFXLFFBQVE7QUFDckMsb0JBQVEsSUFBSSxXQUFXLElBQUksTUFBTSxJQUFJLElBQUksR0FBRyxPQUFPLE1BQU0sTUFBTSxHQUFHLElBQUksR0FBRyxFQUFFO0FBQUEsVUFDL0UsQ0FBQztBQUFBLFFBQ0w7QUFBQSxNQUNKO0FBQUEsSUFDSjtBQUFBLEVBQ0o7QUFBQSxFQUNBLE9BQU87QUFBQSxJQUNILFdBQVc7QUFBQSxFQUNmO0FBQUEsRUFDQSxTQUFTO0FBQUEsSUFDTCxPQUFPO0FBQUEsTUFDSCxLQUFLLEtBQUssUUFBUSxrQ0FBVyxPQUFPO0FBQUEsSUFDeEM7QUFBQSxFQUNKO0FBQ0osQ0FBQzsiLAogICJuYW1lcyI6IFsicGF0aCJdCn0K

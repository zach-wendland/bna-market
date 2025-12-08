import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    // Optimize chunk splitting for code-splitting
    rollupOptions: {
      output: {
        manualChunks: {
          // Core Vue framework - always loaded
          'vue-core': ['vue', 'pinia'],
          // Charting library - lazy loaded
          'charts': ['chart.js', 'vue-chartjs'],
          // Map libraries - lazy loaded
          'maps': ['leaflet', 'leaflet.markercluster'],
          // UI libraries
          'ui': ['@headlessui/vue', '@heroicons/vue'],
        },
      },
    },
    // Increase warning limit since we're code-splitting
    chunkSizeWarningLimit: 300,
  },
})

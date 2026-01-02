import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    host: true,
  },
  build: {
    // Enable source maps for production debugging (optional, can be disabled for smaller bundles)
    sourcemap: false,

    // Minify the code with esbuild (built-in, faster than terser)
    minify: 'esbuild',

    // Report compressed bundle sizes
    reportCompressedSize: true,

    // Chunk size warning limit (in kB)
    chunkSizeWarningLimit: 1000,

    // Code splitting configuration
    rollupOptions: {
      output: {
        // Manual chunks for better caching
        manualChunks: (id) => {
          // Vendor chunk for React and related libraries
          if (id.includes('node_modules/react') || id.includes('node_modules/react-dom')) {
            return 'react-vendor';
          }

          // Router and state management
          if (id.includes('node_modules/zustand') || id.includes('node_modules/@tanstack')) {
            return 'state-vendor';
          }

          // UI components
          if (id.includes('node_modules/framer-motion') || id.includes('node_modules/react-markdown')) {
            return 'ui-vendor';
          }

          // WebSocket client
          if (id.includes('node_modules/socket.io-client')) {
            return 'network-vendor';
          }

          // Radix UI components
          if (id.includes('node_modules/@radix-ui')) {
            return 'radix-vendor';
          }
        },

        // Asset naming for better caching
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: (assetInfo) => {
          const info = assetInfo.name?.split('.') || [];
          const extType = info[info.length - 1];

          // Organize assets by type
          if (/png|jpe?g|svg|gif|tiff|bmp|ico/i.test(extType)) {
            return `assets/images/[name]-[hash][extname]`;
          }
          if (/css/i.test(extType)) {
            return `assets/css/[name]-[hash][extname]`;
          }
          return `assets/[name]-[hash][extname]`;
        },
      },
    },

    // Target modern browsers for smaller bundles
    target: 'es2015',
  },
})

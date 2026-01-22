import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  // Define environment variables prefix
  // VITE_API_URL will be available as import.meta.env.VITE_API_URL
  define: {
    // Make process.env available for compatibility
    'process.env': {}
  }
})


import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/token': 'http://localhost:8000',
      '/appointments': 'http://localhost:8000',
      '/summary': 'http://localhost:8000',
      '/health': 'http://localhost:8000',
    },
  },
})

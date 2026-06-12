import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// The dev server proxies /api/* to the FastAPI backend. This means the browser
// only ever talks to the Vite origin (same-origin) -> NO CORS issues in dev.
// Override the backend with:  VITE_API_TARGET=http://localhost:8000 npm run dev
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: process.env.VITE_API_TARGET || 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})

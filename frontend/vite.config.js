import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In production nginx proxies /api to the backend container. In dev there is
// no nginx, so Vite proxies the same prefix to the backend's host port — which
// means the app can always call /api/... regardless of where it's running.
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8100',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})

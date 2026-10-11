import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: '/',
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/admin': 'http://127.0.0.1:5000',
      '^/log($|/)': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      '/dashboard': 'http://127.0.0.1:5000',
      '/heatmap': 'http://127.0.0.1:5000',
      '/history': 'http://127.0.0.1:5000',
      '/goals': 'http://127.0.0.1:5000',
      '/logout': 'http://127.0.0.1:5000',
      '/profile': 'http://127.0.0.1:5000',
      '/tour': 'http://127.0.0.1:5000',
      '/onboarding': 'http://127.0.0.1:5000',
      '/contact': 'http://127.0.0.1:5000',
      '/help': 'http://127.0.0.1:5000',
      '/manual': 'http://127.0.0.1:5000',
      '/api-docs': 'http://127.0.0.1:5000',
      '/privacy': 'http://127.0.0.1:5000',
      '/terms': 'http://127.0.0.1:5000',
      '/report': 'http://127.0.0.1:5000',
      '/export': 'http://127.0.0.1:5000',
      '/api': 'http://127.0.0.1:5000',
      '/static': 'http://127.0.0.1:5000',
    }
  }
});

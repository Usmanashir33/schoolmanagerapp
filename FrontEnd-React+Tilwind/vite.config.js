import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react-swc';
import tailwindcss from '@tailwindcss/vite' ;

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
   server: {
    host: '0.0.0.0', // ← This allows access from your local network
    port: 5173       // (optional) force using port 5173
  }
})

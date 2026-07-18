import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Local FE proxies /api → local backend (no Koyeb redeploy needed for API work).
// Override: VITE_PROXY_TARGET=https://your-koyeb-app.koyeb.app
const proxyTarget = process.env.VITE_PROXY_TARGET || "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true,
    proxy: {
      "/api": {
        target: proxyTarget,
        changeOrigin: true,
      },
    },
  },
});

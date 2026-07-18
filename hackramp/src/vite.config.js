import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev proxy /api → deployed API (override with VITE_PROXY_TARGET if needed).
const proxyTarget =
  process.env.VITE_PROXY_TARGET || "https://holy-merrill-tormame-aafedec0.koyeb.app";

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

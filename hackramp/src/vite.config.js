import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Local FE → proxy /api to backend so you can iterate UI without redeploying.
// Override with VITE_PROXY_TARGET=http://127.0.0.1:8000 for a local API.
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
        secure: true,
      },
    },
  },
});

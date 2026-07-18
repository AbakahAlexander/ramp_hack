import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Dev proxy only /api/v1 to deployed API.
// Do NOT proxy `/api` alone — that steals the local module `/api.js` and blanks the page.
const proxyTarget =
  process.env.VITE_PROXY_TARGET || "https://holy-merrill-tormame-aafedec0.koyeb.app";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    open: true,
    proxy: {
      "/api/v1": {
        target: proxyTarget,
        changeOrigin: true,
      },
    },
  },
});

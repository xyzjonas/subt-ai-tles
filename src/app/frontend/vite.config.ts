import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";
import { VitePWA } from "vite-plugin-pwa";
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
      vue(),
      vueDevTools(),
      VitePWA({
        registerType: "autoUpdate",
        includeAssets: ["favicon.ico", "favicon.svg", "apple-touch-icon-180x180.png"],
        manifest: {
          name: "subt-ai-tles",
          short_name: "subt-ai-tles",
          description: "AI-powered contextual subtitle translation for SRT files.",
          theme_color: "#4f46e5",
          background_color: "#f7f9fb",
          display: "standalone",
          start_url: "/",
          icons: [
            { src: "pwa-64x64.png", sizes: "64x64", type: "image/png" },
            { src: "pwa-192x192.png", sizes: "192x192", type: "image/png" },
            { src: "pwa-512x512.png", sizes: "512x512", type: "image/png" },
            { src: "maskable-icon-512x512.png", sizes: "512x512", type: "image/png", purpose: "maskable" },
          ],
        },
        workbox: {
          navigateFallbackDenylist: [/^\/api\//],
        },
      }),
  ],
  server: {
    proxy: { "/api": "http://127.0.0.1:8000" },
  },
});

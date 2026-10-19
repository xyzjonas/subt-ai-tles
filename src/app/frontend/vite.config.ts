import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";
import vueDevTools from 'vite-plugin-vue-devtools'

export default defineConfig({
  plugins: [
      vue(),
      vueDevTools()
  ],
  server: {
    proxy: { "/api": "http://127.0.0.1:8000" },
  },
});

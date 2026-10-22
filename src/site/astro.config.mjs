import { defineConfig } from "astro/config";
import vue from "@astrojs/vue";

// Served from https://xyzjonas.github.io/subt-ai-tles/ (GitHub project page).
export default defineConfig({
  site: "https://xyzjonas.github.io",
  base: "/subt-ai-tles",
  trailingSlash: "always",
  integrations: [vue()],
  i18n: {
    defaultLocale: "en",
    locales: ["en", "cs"],
    routing: { prefixDefaultLocale: false },
  },
});

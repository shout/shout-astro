import { defineConfig } from "astro/config";
import tailwindcss from "@tailwindcss/vite";
import sitemap from "@astrojs/sitemap";
import icon from "astro-icon";
import { fileURLToPath, URL } from "node:url";

import cloudflare from "@astrojs/cloudflare";

export default defineConfig({
  site: "https://shout.com",
  output: 'static',
  integrations: [sitemap(), icon()],

  vite: {
    plugins: [tailwindcss()],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
      },
    },
  },

  adapter: cloudflare(),
});
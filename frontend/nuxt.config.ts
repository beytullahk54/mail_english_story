import Aura from "@primeuix/themes/aura";

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-07-15",
  devtools: { enabled: true },
  modules: ["@primevue/nuxt-module"],
  css: [
    'primeicons/primeicons.css',
    '~/assets/css/main.css'
  ],
  primevue: {
    options: {
      theme: {
        preset: Aura,
      },
    },
  },
  runtimeConfig: {
    public: {
      apiBase: '' // Default value, will be overridden by NUXT_PUBLIC_API_BASE
    }
  }
});

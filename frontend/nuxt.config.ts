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
  routeRules: {
    '/admin/**': {
      headers: {
        'X-Robots-Tag': 'noindex, nofollow, noarchive',
      },
    },
    '/admin': {
      headers: {
        'X-Robots-Tag': 'noindex, nofollow, noarchive',
      },
    },
  },

  runtimeConfig: {
    public: {
      apiBase: '',   // NUXT_PUBLIC_API_BASE
      siteUrl: '',   // NUXT_PUBLIC_SITE_URL  (frontend URL, SEO canonical için)
    }
  }
});

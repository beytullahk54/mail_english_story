export default defineEventHandler((event) => {
  const config = useRuntimeConfig(event);
  return {
    apiBase: config.public.apiBase,
    siteUrl: config.public.siteUrl,
  };
});

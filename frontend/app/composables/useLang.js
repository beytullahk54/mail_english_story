export const useLang = () => {
  const route = useRoute();
  const lang = computed(() => route.params.lang === 'tr' ? 'tr' : 'en');
  const isTr = computed(() => lang.value === 'tr');
  const pick = (en, tr) => (isTr.value && tr) ? tr : en;

  return { lang, isTr, pick };
};

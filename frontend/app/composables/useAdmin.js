export const useAdmin = () => {
  const config = useRuntimeConfig();
  const token = useCookie('admin_token', { maxAge: 60 * 60 * 24 * 7, sameSite: 'lax' });

  const isLoggedIn = computed(() => !!token.value);

  const login = async (password) => {
    const data = await $fetch(`${config.public.apiBase}/api/v1/admin/login`, {
      method: 'POST',
      body: { password },
    });
    token.value = data.token;
  };

  const logout = () => { token.value = null; };

  const authHeaders = computed(() => ({ 'X-Api-Token': token.value || '' }));

  return { isLoggedIn, login, logout, authHeaders, token };
};

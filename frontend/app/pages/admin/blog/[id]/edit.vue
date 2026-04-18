<template>
  <div class="admin-container">
    <div class="background-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
    </div>

    <div class="admin-wrapper">
      <header class="topbar glass-effect">
        <NuxtLink to="/admin/blog" class="back-btn">
          <i class="pi pi-arrow-left"></i> Yazılar
        </NuxtLink>
        <span class="topbar-title">Yazıyı Düzenle</span>
        <div style="width:80px"></div>
      </header>

      <div v-if="loading" class="state-box">
        <i class="pi pi-spinner pi-spin"></i>
      </div>

      <BlogForm
        v-else-if="initialData"
        :initial="initialData"
        :saving="saving"
        :error="error"
        @submit="handleSubmit"
      />
    </div>
  </div>
</template>

<script setup>
import BlogForm from '~/components/admin/BlogForm.vue';

definePageMeta({ middleware: 'admin', layout: false });

const config = useRuntimeConfig();
const route = useRoute();
const { authHeaders } = useAdmin();

const loading = ref(true);
const saving = ref(false);
const error = ref('');
const initialData = ref(null);

// Fetch existing post by id via admin/all then find by id
// Actually fetch by slug — we'll use a direct admin endpoint
try {
  const data = await $fetch(`${config.public.apiBase}/api/v1/blog/admin/all`, {
    headers: authHeaders.value,
    query: { page_size: 100 },
  });
  const post = data.items.find(p => p.id === Number(route.params.id));
  if (post) {
    // Fetch full detail
    initialData.value = await $fetch(`${config.public.apiBase}/api/v1/blog/${post.slug}`, {
      headers: authHeaders.value,
    });
  }
} catch (e) {
  if (e.status === 401) navigateTo('/admin/login');
} finally {
  loading.value = false;
}

const handleSubmit = async (form) => {
  saving.value = true;
  error.value = '';
  try {
    await $fetch(`${config.public.apiBase}/api/v1/blog/${route.params.id}`, {
      method: 'PUT',
      headers: authHeaders.value,
      body: form,
    });
    await navigateTo('/admin/blog');
  } catch (e) {
    error.value = e?.data?.detail || 'Bir hata oluştu.';
  } finally {
    saving.value = false;
  }
};

useHead({
  title: 'Düzenle — Admin',
  meta: [{ name: 'robots', content: 'noindex, nofollow, noarchive' }],
});
</script>

<style scoped>
.admin-container { min-height: 100vh; position: relative; overflow: hidden; }
.background-shapes { position: absolute; inset: 0; z-index: 0; overflow: hidden; }
.shape { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.4; animation: float 10s infinite alternate ease-in-out; }
.shape-1 { width: 500px; height: 500px; background: #6366f1; top: -15%; left: -5%; }
.shape-2 { width: 600px; height: 600px; background: #c084fc; bottom: -25%; right: -10%; animation-delay: -5s; }
@keyframes float { 0% { transform: translate(0,0) scale(1); } 100% { transform: translate(30px,50px) scale(1.1); } }

.admin-wrapper { position: relative; z-index: 10; max-width: 900px; margin: 0 auto; padding: 1.5rem; display: flex; flex-direction: column; gap: 1.5rem; }

.topbar { display: flex; align-items: center; justify-content: space-between; padding: 1rem 1.5rem; border-radius: 16px; }
.topbar-title { font-weight: 600; }
.back-btn { display: inline-flex; align-items: center; gap: 0.4rem; color: var(--text-muted); font-size: 0.9rem; text-decoration: none; transition: color 0.2s; }
.back-btn:hover { color: var(--text-main); }
.state-box { display: flex; align-items: center; justify-content: center; padding: 4rem; font-size: 2rem; color: var(--text-muted); }
</style>

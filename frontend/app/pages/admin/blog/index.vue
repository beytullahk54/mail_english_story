<template>
  <div class="admin-container">
    <div class="background-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
    </div>

    <div class="admin-wrapper">

      <!-- Topbar -->
      <header class="topbar glass-effect">
        <div class="topbar-left">
          <i class="pi pi-pencil"></i>
          <span>Blog Yönetimi</span>
        </div>
        <div class="topbar-right">
          <NuxtLink to="/admin/subscribers" class="icon-btn" title="Aboneler">
            <i class="pi pi-users"></i>
          </NuxtLink>
          <NuxtLink to="/en/blog" class="icon-btn" target="_blank" title="Siteyi Görüntüle">
            <i class="pi pi-external-link"></i>
          </NuxtLink>
          <button class="icon-btn danger" @click="handleLogout" title="Çıkış">
            <i class="pi pi-sign-out"></i>
          </button>
        </div>
      </header>

      <!-- Content -->
      <main class="admin-content">
        <div class="content-header">
          <h2>Yazılar <span class="count">{{ total }}</span></h2>
          <div class="header-actions">
            <button class="generate-btn" :disabled="generating" @click="generateNext" :title="'topics.md\'deki sıradaki konuyu üret'">
              <i v-if="generating" class="pi pi-spinner pi-spin"></i>
              <i v-else class="pi pi-sparkles"></i>
              {{ generating ? 'Üretiliyor...' : 'AI Üret' }}
            </button>
            <NuxtLink to="/admin/blog/create" class="create-btn">
              <i class="pi pi-plus"></i>
              Yeni Yazı
            </NuxtLink>
          </div>
        </div>

        <!-- Generate result message -->
        <div v-if="generateMsg" class="generate-msg" :class="generateMsg.type">
          <i :class="generateMsg.type === 'success' ? 'pi pi-check-circle' : 'pi pi-exclamation-circle'"></i>
          {{ generateMsg.text }}
        </div>

        <!-- Loading -->
        <div v-if="loading" class="state-box">
          <i class="pi pi-spinner pi-spin"></i>
        </div>

        <!-- Empty -->
        <div v-else-if="posts.length === 0" class="state-box glass-effect">
          <i class="pi pi-inbox"></i>
          <p>Henüz yazı yok.</p>
        </div>

        <!-- Table -->
        <div v-else class="posts-table glass-effect">
          <div v-for="post in posts" :key="post.id" class="post-row">
            <div class="post-row-info">
              <div class="post-row-title">
                <span class="pub-badge" :class="{ unpublished: !isPublished(post) }">
                  {{ isPublished(post) ? 'Yayında' : 'Taslak' }}
                </span>
                {{ post.title }}
              </div>
              <div class="post-row-meta">
                <span><i class="pi pi-calendar"></i> {{ formatDate(post.published_at) }}</span>
                <span v-if="post.slug_tr"><i class="pi pi-globe"></i> TR slug var</span>
              </div>
            </div>
            <div class="post-row-actions">
              <a :href="`/en/blog/${post.slug}`" target="_blank" class="action-btn" title="Önizle">
                <i class="pi pi-eye"></i>
              </a>
              <NuxtLink :to="`/admin/blog/${post.id}/edit`" class="action-btn" title="Düzenle">
                <i class="pi pi-pencil"></i>
              </NuxtLink>
              <button class="action-btn danger" @click="confirmDelete(post)" title="Sil">
                <i class="pi pi-trash"></i>
              </button>
            </div>
          </div>
        </div>

      </main>
    </div>

    <!-- Delete Confirm Dialog -->
    <div v-if="deleteTarget" class="dialog-overlay" @click.self="deleteTarget = null">
      <div class="dialog glass-effect">
        <i class="pi pi-exclamation-triangle dialog-icon"></i>
        <h3>Yazıyı sil?</h3>
        <p>{{ deleteTarget.title }}</p>
        <div class="dialog-actions">
          <button class="dialog-cancel" @click="deleteTarget = null">İptal</button>
          <button class="dialog-confirm" :disabled="deleting" @click="doDelete">
            {{ deleting ? 'Siliniyor...' : 'Evet, Sil' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

definePageMeta({ middleware: 'admin', layout: false });

const config = useRuntimeConfig();
const { authHeaders, logout } = useAdmin();

const posts = ref([]);
const total = ref(0);
const loading = ref(false);
const deleteTarget = ref(null);
const deleting = ref(false);

const fetchPosts = async () => {
  loading.value = true;
  try {
    const data = await $fetch(`${config.public.apiBase}/api/v1/blog/admin/all`, {
      headers: authHeaders.value,
    });
    posts.value = data.items;
    total.value = data.total;
  } catch (e) {
    if (e.status === 401) navigateTo('/admin/login');
  } finally {
    loading.value = false;
  }
};

const isPublished = (post) => post.published !== false;

const formatDate = (d) => new Date(d).toLocaleDateString('tr-TR', {
  day: 'numeric', month: 'short', year: 'numeric'
});

const confirmDelete = (post) => { deleteTarget.value = post; };

const doDelete = async () => {
  deleting.value = true;
  try {
    await $fetch(`${config.public.apiBase}/api/v1/blog/${deleteTarget.value.id}`, {
      method: 'DELETE',
      headers: authHeaders.value,
    });
    deleteTarget.value = null;
    await fetchPosts();
  } finally {
    deleting.value = false;
  }
};

const generating = ref(false);
const generateMsg = ref(null);

const generateNext = async () => {
  generating.value = true;
  generateMsg.value = null;
  try {
    const res = await $fetch(`${config.public.apiBase}/api/v1/blog/generate-next`, {
      method: 'POST',
      headers: authHeaders.value,
    });
    if (res.status === 'started') {
      const prevTotal = total.value;
      generateMsg.value = { type: 'success', text: `⏳ Üretiliyor: "${res.topic}"` };

      // Her 15 saniyede bir yeni yazı geldi mi kontrol et (max 3 dakika)
      let attempts = 0;
      const poll = setInterval(async () => {
        attempts++;
        await fetchPosts();
        if (total.value > prevTotal) {
          clearInterval(poll);
          generating.value = false;
          generateMsg.value = { type: 'success', text: `✅ Yazı oluşturuldu: "${posts.value[0]?.title}"` };
          setTimeout(() => { generateMsg.value = null; }, 6000);
        } else if (attempts >= 12) {
          clearInterval(poll);
          generating.value = false;
          generateMsg.value = { type: 'error', text: '⚠️ 3 dakikada tamamlanamadı. Railway loglarını kontrol edin.' };
          setTimeout(() => { generateMsg.value = null; }, 8000);
        }
      }, 15000);
    } else {
      generateMsg.value = { type: 'success', text: res.message };
      generating.value = false;
      setTimeout(() => { generateMsg.value = null; }, 5000);
    }
  } catch (e) {
    generating.value = false;
    generateMsg.value = { type: 'error', text: e?.data?.detail || 'Üretim başarısız.' };
    setTimeout(() => { generateMsg.value = null; }, 6000);
  }
};

const handleLogout = () => { logout(); navigateTo('/admin/login'); };

useHead({
  title: 'Blog Yönetimi — Admin',
  meta: [{ name: 'robots', content: 'noindex, nofollow, noarchive' }],
});
onMounted(fetchPosts);
</script>

<style scoped>
.admin-container {
  min-height: 100vh; position: relative; overflow: hidden;
}
.background-shapes { position: absolute; inset: 0; z-index: 0; overflow: hidden; }
.shape { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.4; animation: float 10s infinite alternate ease-in-out; }
.shape-1 { width: 500px; height: 500px; background: #6366f1; top: -15%; left: -5%; }
.shape-2 { width: 600px; height: 600px; background: #c084fc; bottom: -25%; right: -10%; animation-delay: -5s; }
@keyframes float { 0% { transform: translate(0,0) scale(1); } 100% { transform: translate(30px,50px) scale(1.1); } }

.admin-wrapper {
  position: relative; z-index: 10;
  max-width: 900px; margin: 0 auto; padding: 1.5rem;
  display: flex; flex-direction: column; gap: 1.5rem;
}

.topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 1.5rem; border-radius: 16px;
}
.topbar-left { display: flex; align-items: center; gap: 0.6rem; font-weight: 600; font-size: 1rem; }
.topbar-left i { color: #818cf8; }
.topbar-right { display: flex; align-items: center; gap: 0.5rem; }

.icon-btn {
  display: flex; align-items: center; justify-content: center;
  width: 36px; height: 36px; border-radius: 8px;
  background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.12);
  color: var(--text-muted); cursor: pointer; transition: all 0.2s; text-decoration: none;
  font-size: 0.9rem;
}
.icon-btn:hover { background: rgba(255,255,255,0.12); color: var(--text-main); }
.icon-btn.danger:hover { background: rgba(239,68,68,0.15); border-color: rgba(239,68,68,0.3); color: #ef4444; }

.admin-content { display: flex; flex-direction: column; gap: 1.25rem; }

.content-header {
  display: flex; align-items: center; justify-content: space-between;
}
.content-header h2 { margin: 0; font-size: 1.3rem; font-weight: 600; display: flex; align-items: center; gap: 0.5rem; }
.count { font-size: 0.85rem; background: rgba(129,140,248,0.15); border: 1px solid rgba(129,140,248,0.25); color: #818cf8; padding: 0.1rem 0.6rem; border-radius: 50px; }

.header-actions { display: flex; align-items: center; gap: 0.6rem; }

.generate-btn {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.6rem 1.1rem; border-radius: 10px;
  background: rgba(192,132,252,0.15); border: 1px solid rgba(192,132,252,0.35);
  color: #c084fc; font-weight: 600; font-size: 0.88rem; font-family: inherit;
  cursor: pointer; transition: all 0.2s;
}
.generate-btn:hover:not(:disabled) { background: rgba(192,132,252,0.25); }
.generate-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.generate-msg {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.75rem 1.25rem; border-radius: 10px; font-size: 0.88rem;
}
.generate-msg.success { background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.25); color: #34d399; }
.generate-msg.error { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.25); color: #ef4444; }

.create-btn {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.6rem 1.25rem; border-radius: 10px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white; font-weight: 600; font-size: 0.9rem; text-decoration: none;
  transition: opacity 0.2s, transform 0.2s;
}
.create-btn:hover { opacity: 0.9; transform: translateY(-1px); }

.state-box {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  gap: 1rem; padding: 4rem; color: var(--text-muted); font-size: 1.5rem;
}

.posts-table { border-radius: 16px; overflow: hidden; }

.post-row {
  display: flex; align-items: center; justify-content: space-between; gap: 1rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  transition: background 0.2s;
}
.post-row:last-child { border-bottom: none; }
.post-row:hover { background: rgba(255,255,255,0.03); }

.post-row-info { display: flex; flex-direction: column; gap: 0.35rem; flex: 1; min-width: 0; }
.post-row-title {
  display: flex; align-items: center; gap: 0.6rem;
  font-weight: 500; font-size: 0.95rem;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.post-row-meta { display: flex; align-items: center; gap: 1rem; font-size: 0.78rem; color: var(--text-muted); }
.post-row-meta i { font-size: 0.75rem; }

.pub-badge {
  flex-shrink: 0; padding: 0.15rem 0.55rem; border-radius: 50px; font-size: 0.72rem; font-weight: 600;
  background: rgba(52,211,153,0.15); border: 1px solid rgba(52,211,153,0.3); color: #34d399;
}
.pub-badge.unpublished { background: rgba(251,191,36,0.1); border-color: rgba(251,191,36,0.3); color: #fbbf24; }

.post-row-actions { display: flex; align-items: center; gap: 0.4rem; flex-shrink: 0; }
.action-btn {
  display: flex; align-items: center; justify-content: center;
  width: 34px; height: 34px; border-radius: 8px;
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
  color: var(--text-muted); cursor: pointer; transition: all 0.2s; text-decoration: none; font-size: 0.85rem;
}
.action-btn:hover { background: rgba(129,140,248,0.15); border-color: rgba(129,140,248,0.3); color: #818cf8; }
.action-btn.danger:hover { background: rgba(239,68,68,0.15); border-color: rgba(239,68,68,0.3); color: #ef4444; }

/* Dialog */
.dialog-overlay {
  position: fixed; inset: 0; z-index: 100;
  background: rgba(0,0,0,0.6); backdrop-filter: blur(4px);
  display: flex; align-items: center; justify-content: center; padding: 1rem;
}
.dialog {
  width: 100%; max-width: 380px; padding: 2rem;
  display: flex; flex-direction: column; align-items: center; gap: 1rem; text-align: center;
}
.dialog-icon { font-size: 2.5rem; color: #f97316; }
.dialog h3 { margin: 0; font-size: 1.1rem; }
.dialog p { margin: 0; color: var(--text-muted); font-size: 0.9rem; }
.dialog-actions { display: flex; gap: 0.75rem; margin-top: 0.5rem; }
.dialog-cancel {
  padding: 0.6rem 1.25rem; border-radius: 8px;
  background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.15);
  color: var(--text-muted); cursor: pointer; font-family: inherit; font-size: 0.9rem;
  transition: all 0.2s;
}
.dialog-cancel:hover { color: var(--text-main); }
.dialog-confirm {
  padding: 0.6rem 1.25rem; border-radius: 8px;
  background: rgba(239,68,68,0.2); border: 1px solid rgba(239,68,68,0.4);
  color: #ef4444; cursor: pointer; font-family: inherit; font-size: 0.9rem; font-weight: 600;
  transition: all 0.2s;
}
.dialog-confirm:hover:not(:disabled) { background: rgba(239,68,68,0.3); }
.dialog-confirm:disabled { opacity: 0.5; cursor: not-allowed; }

@media (max-width: 640px) {
  .admin-wrapper { padding: 1rem; }
  .post-row { flex-direction: column; align-items: flex-start; }
  .post-row-actions { align-self: flex-end; }
}
</style>

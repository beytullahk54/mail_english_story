<template>
  <div class="page-container">
    <div class="background-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <main class="content-wrapper anim-fade-in">

      <!-- Header -->
      <div class="page-header anim-slide-up">
        <div class="header-top-row">
          <NuxtLink to="/" class="back-btn">
            <i class="pi pi-arrow-left"></i>
            {{ isTr ? 'Geri' : 'Back' }}
          </NuxtLink>
          <NuxtLink :to="isTr ? '/en/blog' : '/tr/blog'" class="lang-toggle">
            <i class="pi pi-globe"></i>
            {{ isTr ? 'EN' : 'TR' }}
          </NuxtLink>
        </div>
        <div class="header-title">
          <i class="pi pi-pencil"></i>
          <h1>Blog</h1>
        </div>
        <p class="header-sub">
          {{ isTr
            ? 'İngilizce öğrenmek için ipuçları, rehberler ve içgörüler'
            : 'Tips, insights, and guides for learning English' }}
        </p>
      </div>

      <!-- Tag Filter -->
      <div class="filters-bar glass-effect anim-slide-up delay-1">
        <div class="tags-row">
          <button class="tag-chip" :class="{ active: !activeTag }" @click="setTag(null)">
            {{ isTr ? 'Tümü' : 'All' }}
          </button>
          <button
            v-for="tag in popularTags"
            :key="tag"
            class="tag-chip"
            :class="{ active: activeTag === tag }"
            @click="setTag(tag)"
          >{{ tag }}</button>
        </div>
        <div class="total-badge" v-if="total > 0">
          <i class="pi pi-file"></i>
          {{ total }} {{ isTr ? 'yazı' : 'articles' }}
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <i class="pi pi-spinner pi-spin"></i>
      </div>

      <!-- Empty -->
      <div v-else-if="posts.length === 0" class="empty-state glass-effect">
        <i class="pi pi-inbox"></i>
        <p>{{ isTr ? 'Yazı bulunamadı.' : 'No articles found.' }}</p>
      </div>

      <!-- Post list -->
      <div v-else class="posts-list">
        <NuxtLink
          v-for="post in posts"
          :key="post.id"
          :to="postUrl(post)"
          class="post-card glass-effect"
        >
          <div class="post-card-body">
            <div class="post-meta">
              <span class="date-text">
                <i class="pi pi-calendar"></i>
                {{ formatDate(post.published_at) }}
              </span>
              <span class="author-text">
                <i class="pi pi-user"></i>
                {{ post.author }}
              </span>
            </div>
            <h2 class="post-title">{{ pick(post.title, post.title_tr) }}</h2>
            <p class="post-excerpt">{{ pick(post.excerpt, post.excerpt_tr) }}</p>
            <div class="post-footer">
              <div class="tags-inline">
                <span v-for="tag in post.tags.slice(0, 3)" :key="tag" class="tag-badge">{{ tag }}</span>
              </div>
              <span class="read-more">
                {{ isTr ? 'Devamını oku' : 'Read article' }} <i class="pi pi-arrow-right"></i>
              </span>
            </div>
          </div>
        </NuxtLink>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <button class="page-btn" :disabled="page === 1" @click="goToPage(page - 1)">
          <i class="pi pi-chevron-left"></i>
        </button>
        <span class="page-info">{{ page }} / {{ totalPages }}</span>
        <button class="page-btn" :disabled="page === totalPages" @click="goToPage(page + 1)">
          <i class="pi pi-chevron-right"></i>
        </button>
      </div>

    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';

const config = useRuntimeConfig();
const route = useRoute();
const { lang, isTr, pick } = useLang();

// Redirect if invalid lang param
if (!['en', 'tr'].includes(route.params.lang)) {
  await navigateTo('/en/blog');
}

const posts = ref([]);
const total = ref(0);
const page = ref(1);
const pageSize = 10;
const loading = ref(false);
const activeTag = ref(null);

const popularTags = ['tips', 'learning', 'vocabulary', 'ai', 'stories', 'science'];
const totalPages = computed(() => Math.ceil(total.value / pageSize));

const postUrl = (post) => {
  const slug = isTr.value ? (post.slug_tr || post.slug) : post.slug;
  return `/${lang.value}/blog/${slug}`;
};

const fetchPosts = async () => {
  loading.value = true;
  const params = new URLSearchParams({ page: page.value, page_size: pageSize });
  if (activeTag.value) params.set('tag', activeTag.value);
  try {
    const data = await $fetch(`${config.public.apiBase}/api/v1/blog?${params}`);
    posts.value = data.items;
    total.value = data.total;
  } catch {
    posts.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
};

const setTag = (tag) => { activeTag.value = tag; page.value = 1; fetchPosts(); };

const goToPage = (p) => {
  page.value = p;
  fetchPosts();
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const formatDate = (dateStr) =>
  new Date(dateStr).toLocaleDateString(isTr.value ? 'tr-TR' : 'en-GB', {
    day: 'numeric', month: 'long', year: 'numeric'
  });

const pageTitle = isTr.value ? 'Blog — English Story' : 'Blog — English Story';
const pageDesc = isTr.value
  ? 'İngilizce öğrenmek için ipuçları, rehberler ve yazılar. Hikaye temelli öğrenme, CEFR seviyeleri ve yapay zeka hakkında bilgi edinin.'
  : 'Tips, insights, and guides for learning English through storytelling. Explore CEFR levels, AI-powered learning, and daily habits.';

const siteUrl = config.public.siteUrl || config.public.apiBase;

useHead({
  title: pageTitle,
  htmlAttrs: { lang: lang.value },
  meta: [
    { name: 'description', content: pageDesc },
    { property: 'og:title', content: pageTitle },
    { property: 'og:description', content: pageDesc },
    { property: 'og:type', content: 'website' },
    { property: 'og:url', content: `${siteUrl}/${lang.value}/blog` },
    { name: 'twitter:card', content: 'summary' },
    { name: 'twitter:title', content: pageTitle },
    { name: 'twitter:description', content: pageDesc },
  ],
  link: [
    { rel: 'canonical', href: `${siteUrl}/${lang.value}/blog` },
    { rel: 'alternate', hreflang: 'en', href: `${siteUrl}/en/blog` },
    { rel: 'alternate', hreflang: 'tr', href: `${siteUrl}/tr/blog` },
    { rel: 'alternate', hreflang: 'x-default', href: `${siteUrl}/en/blog` },
  ],
});

onMounted(fetchPosts);
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  position: relative;
  overflow: hidden;
  padding: 2rem;
}
.background-shapes { position: absolute; inset: 0; z-index: 0; overflow: hidden; }
.shape {
  position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.5;
  animation: float 10s infinite alternate ease-in-out;
}
.shape-1 { width: 400px; height: 400px; background: #6366f1; top: -10%; left: -5%; }
.shape-2 { width: 500px; height: 500px; background: #c084fc; bottom: -20%; right: -10%; animation-delay: -5s; }
.shape-3 { width: 300px; height: 300px; background: #3b82f6; top: 40%; left: 50%; opacity: 0.3; animation-duration: 15s; }
@keyframes float {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(30px, 50px) scale(1.1); }
}

.content-wrapper {
  position: relative; z-index: 10; width: 100%; max-width: 760px;
  padding: 2rem 0; display: flex; flex-direction: column; gap: 1.5rem;
}

.header-top-row {
  display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem;
}
.back-btn {
  display: inline-flex; align-items: center; gap: 0.5rem;
  color: var(--text-muted); font-size: 0.9rem; transition: color 0.2s; text-decoration: none;
}
.back-btn:hover { color: var(--text-main); }

.lang-toggle {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.35rem 0.9rem; border-radius: 50px;
  background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.15);
  color: var(--text-muted); font-size: 0.82rem; font-weight: 600;
  cursor: pointer; transition: all 0.2s; font-family: inherit;
  letter-spacing: 0.04em; text-decoration: none;
}
.lang-toggle:hover {
  background: rgba(129,140,248,0.15); border-color: rgba(129,140,248,0.4); color: #818cf8;
}

.header-title { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 0.4rem; }
.header-title i { font-size: 1.5rem; color: #818cf8; }
.header-title h1 { margin: 0; font-size: 2rem; font-weight: 700; }
.header-sub { margin: 0; color: var(--text-muted); font-size: 0.95rem; }

.filters-bar {
  display: flex; align-items: center; gap: 1rem; padding: 1rem 1.25rem; flex-wrap: wrap;
}
.tags-row { display: flex; flex-wrap: wrap; gap: 0.5rem; flex: 1; }
.tag-chip {
  padding: 0.3rem 0.85rem; border-radius: 50px;
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.15);
  color: var(--text-muted); font-size: 0.82rem; cursor: pointer; transition: all 0.2s; font-family: inherit;
}
.tag-chip:hover { border-color: rgba(129,140,248,0.4); color: var(--text-main); }
.tag-chip.active { background: rgba(99,102,241,0.2); border-color: rgba(99,102,241,0.5); color: #818cf8; }
.total-badge { display: flex; align-items: center; gap: 0.4rem; font-size: 0.85rem; color: var(--text-muted); white-space: nowrap; }

.loading-state { display: flex; align-items: center; justify-content: center; padding: 4rem; color: var(--text-muted); font-size: 2rem; }
.empty-state { display: flex; flex-direction: column; align-items: center; gap: 1rem; padding: 4rem 2rem; color: var(--text-muted); }
.empty-state i { font-size: 2rem; opacity: 0.5; }

.posts-list { display: flex; flex-direction: column; gap: 1.25rem; }
.post-card {
  display: block; text-decoration: none; color: inherit;
  transition: border-color 0.2s, transform 0.2s; overflow: hidden;
}
.post-card:hover { border-color: rgba(129,140,248,0.4); transform: translateY(-2px); }
.post-card-body { padding: 1.75rem; display: flex; flex-direction: column; gap: 0.75rem; }
.post-meta { display: flex; align-items: center; gap: 1rem; }
.date-text, .author-text { display: flex; align-items: center; gap: 0.35rem; font-size: 0.8rem; color: var(--text-muted); }
.post-title { margin: 0; font-size: 1.2rem; font-weight: 600; line-height: 1.4; color: var(--text-main); transition: color 0.2s; }
.post-card:hover .post-title { color: #818cf8; }
.post-excerpt { margin: 0; font-size: 0.92rem; line-height: 1.7; color: var(--text-muted); display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
.post-footer { display: flex; align-items: center; justify-content: space-between; gap: 1rem; flex-wrap: wrap; }
.tags-inline { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.tag-badge { padding: 0.15rem 0.6rem; border-radius: 50px; background: rgba(129,140,248,0.1); border: 1px solid rgba(129,140,248,0.2); color: #818cf8; font-size: 0.75rem; }
.read-more { display: flex; align-items: center; gap: 0.4rem; font-size: 0.85rem; color: var(--text-muted); transition: color 0.2s; white-space: nowrap; }
.post-card:hover .read-more { color: #818cf8; }

.pagination { display: flex; align-items: center; justify-content: center; gap: 1rem; }
.page-btn { display: flex; align-items: center; justify-content: center; width: 40px; height: 40px; border-radius: 50%; background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.15); color: var(--text-main); cursor: pointer; transition: background 0.2s; }
.page-btn:hover:not(:disabled) { background: rgba(255,255,255,0.12); }
.page-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.page-info { font-size: 0.9rem; color: var(--text-muted); min-width: 60px; text-align: center; }

@media (max-width: 640px) {
  .page-container { padding: 1rem 1rem 4rem; }
  .header-title h1 { font-size: 1.6rem; }
  .post-card-body { padding: 1.25rem; }
}
</style>

<template>
  <div class="page-container">
    <div class="background-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <main class="content-wrapper anim-fade-in">

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <i class="pi pi-spinner pi-spin"></i>
      </div>

      <!-- 404 -->
      <div v-else-if="!post" class="empty-state glass-effect">
        <i class="pi pi-exclamation-circle"></i>
        <p>{{ isTr ? 'Yazı bulunamadı.' : 'Article not found.' }}</p>
        <NuxtLink to="/blog" class="back-link">
          <i class="pi pi-arrow-left"></i> Blog
        </NuxtLink>
      </div>

      <!-- Article -->
      <article v-else>

        <!-- Top nav -->
        <div class="top-nav">
          <NuxtLink to="/blog" class="back-btn">
            <i class="pi pi-arrow-left"></i>
            {{ isTr ? 'Blog' : 'Blog' }}
          </NuxtLink>
          <button class="lang-toggle" @click="toggle">
            <i class="pi pi-globe"></i>
            {{ isTr ? 'EN' : 'TR' }}
          </button>
        </div>

        <!-- Post header -->
        <header class="post-header glass-effect anim-slide-up delay-1">
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
          <h1 class="post-title">{{ pick(post.title, post.title_tr) }}</h1>
          <p class="post-excerpt">{{ pick(post.excerpt, post.excerpt_tr) }}</p>
          <div class="tags-inline" v-if="post.tags.length">
            <span v-for="tag in post.tags" :key="tag" class="tag-badge">{{ tag }}</span>
          </div>
        </header>

        <!-- Content -->
        <div class="post-content glass-effect anim-slide-up delay-2" v-html="pick(post.content, post.content_tr)"></div>

        <!-- CTA -->
        <div class="cta-box glass-effect anim-slide-up delay-3">
          <i class="pi pi-envelope cta-icon"></i>
          <div class="cta-text">
            <strong>{{ isTr ? 'Her gün ücretsiz İngilizce hikaye al' : 'Get a free English story every day' }}</strong>
            <span>{{ isTr ? 'Seviyene göre hazırlanmış, AI destekli hikayeler e-postana gelsin.' : 'Level-matched, AI-generated stories delivered to your inbox.' }}</span>
          </div>
          <NuxtLink to="/" class="cta-btn">
            {{ isTr ? 'Ücretsiz Abone Ol' : 'Subscribe Free' }}
          </NuxtLink>
        </div>

        <!-- Back link -->
        <NuxtLink to="/blog" class="back-footer-link">
          <i class="pi pi-arrow-left"></i>
          {{ isTr ? 'Tüm yazılar' : 'More articles' }}
        </NuxtLink>

      </article>
    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const config = useRuntimeConfig();
const route = useRoute();
const { isTr, toggle, pick } = useLang();
const pageUrl = computed(() => `${config.public.siteUrl || config.public.apiBase}/blog/${route.params.slug}`);

const post = ref(null);
const loading = ref(true);

const formatDate = (dateStr) =>
  new Date(dateStr).toLocaleDateString(isTr.value ? 'tr-TR' : 'en-GB', {
    day: 'numeric', month: 'long', year: 'numeric'
  });

try {
  post.value = await $fetch(`${config.public.apiBase}/api/v1/blog/${route.params.slug}`);
} catch {
  post.value = null;
} finally {
  loading.value = false;
}

const pageTitle = computed(() =>
  post.value
    ? `${pick(post.value.title, post.value.title_tr)} — English Story Blog`
    : 'Article Not Found — English Story'
);
const metaDesc = computed(() =>
  pick(post.value?.meta_description, post.value?.meta_description_tr) || pick(post.value?.excerpt, post.value?.excerpt_tr) || ''
);

useHead(computed(() => ({
  title: pageTitle.value,
  meta: [
    { name: 'description', content: metaDesc.value },
    { property: 'og:title', content: pageTitle.value },
    { property: 'og:description', content: metaDesc.value },
    { property: 'og:type', content: 'article' },
    { property: 'og:url', content: pageUrl.value },
    ...(post.value?.cover_image ? [{ property: 'og:image', content: post.value.cover_image }] : []),
    { name: 'twitter:card', content: 'summary_large_image' },
    ...(post.value?.published_at ? [{ property: 'article:published_time', content: post.value.published_at }] : []),
    ...(post.value?.tags?.map((tag) => ({ property: 'article:tag', content: tag })) || []),
  ],
  link: [{ rel: 'canonical', href: pageUrl.value }],
  script: post.value
    ? [{
        type: 'application/ld+json',
        children: JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'Article',
          headline: post.value.title,
          description: post.value.excerpt,
          author: { '@type': 'Organization', name: post.value.author },
          publisher: { '@type': 'Organization', name: 'English Story' },
          datePublished: post.value.published_at,
          url: pageUrl.value,
        }),
      }]
    : [],
})));
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

.background-shapes {
  position: absolute;
  inset: 0;
  z-index: 0;
  overflow: hidden;
}
.shape {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.45;
  animation: float 10s infinite alternate ease-in-out;
}
.shape-1 { width: 400px; height: 400px; background: #6366f1; top: -10%; left: -5%; }
.shape-2 { width: 500px; height: 500px; background: #c084fc; bottom: -20%; right: -10%; animation-delay: -5s; }
.shape-3 { width: 300px; height: 300px; background: #3b82f6; top: 40%; left: 50%; opacity: 0.25; animation-duration: 15s; }

@keyframes float {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(30px, 50px) scale(1.1); }
}

.content-wrapper {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 760px;
  padding: 2rem 0;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* States */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6rem 2rem;
  color: var(--text-muted);
  font-size: 2rem;
}
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 4rem 2rem;
  color: var(--text-muted);
}
.empty-state i { font-size: 2.5rem; opacity: 0.5; }

.back-link {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: #818cf8;
  font-size: 0.9rem;
  text-decoration: none;
}

/* Article */
article {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.top-nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.9rem;
  transition: color 0.2s;
  text-decoration: none;
}
.back-btn:hover { color: var(--text-main); }

.lang-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.9rem;
  border-radius: 50px;
  background: rgba(255, 255, 255, 0.07);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: var(--text-muted);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  font-family: inherit;
  letter-spacing: 0.04em;
}
.lang-toggle:hover {
  background: rgba(129, 140, 248, 0.15);
  border-color: rgba(129, 140, 248, 0.4);
  color: #818cf8;
}

/* Post header */
.post-header {
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.post-meta {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.date-text, .author-text {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.82rem;
  color: var(--text-muted);
}

.post-title {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.35;
  color: var(--text-main);
}

.post-excerpt {
  margin: 0;
  font-size: 1rem;
  line-height: 1.7;
  color: var(--text-muted);
  border-left: 3px solid rgba(129, 140, 248, 0.5);
  padding-left: 1rem;
}

.tags-inline {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.tag-badge {
  padding: 0.2rem 0.65rem;
  border-radius: 50px;
  background: rgba(129, 140, 248, 0.1);
  border: 1px solid rgba(129, 140, 248, 0.2);
  color: #818cf8;
  font-size: 0.75rem;
}

/* Content */
.post-content {
  padding: 2rem 2.5rem;
  line-height: 1.8;
  font-size: 1rem;
  color: var(--text-main);
}

:deep(.post-content h2) {
  font-size: 1.3rem;
  font-weight: 600;
  margin: 2rem 0 0.75rem;
  color: #c4b5fd;
}
:deep(.post-content p) {
  margin: 0 0 1.25rem;
  color: rgba(248, 250, 252, 0.85);
}
:deep(.post-content ul), :deep(.post-content ol) {
  margin: 0 0 1.25rem;
  padding-left: 1.5rem;
}
:deep(.post-content li) {
  margin-bottom: 0.5rem;
  color: rgba(248, 250, 252, 0.85);
}
:deep(.post-content strong) { color: var(--text-main); font-weight: 600; }
:deep(.post-content em) { color: #c084fc; font-style: italic; }
:deep(.post-content a) {
  color: #818cf8;
  text-decoration: underline;
  text-underline-offset: 3px;
  transition: color 0.2s;
}
:deep(.post-content a:hover) { color: #c4b5fd; }

/* CTA */
.cta-box {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.5rem 2rem;
  flex-wrap: wrap;
}
.cta-icon { font-size: 2rem; color: #818cf8; flex-shrink: 0; }
.cta-text {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  flex: 1;
}
.cta-text strong { font-size: 1rem; color: var(--text-main); }
.cta-text span { font-size: 0.88rem; color: var(--text-muted); }

.cta-btn {
  padding: 0.65rem 1.5rem;
  border-radius: 50px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: white;
  font-weight: 600;
  font-size: 0.9rem;
  text-decoration: none;
  white-space: nowrap;
  transition: opacity 0.2s, transform 0.2s;
}
.cta-btn:hover { opacity: 0.9; transform: translateY(-1px); }

.back-footer-link {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.9rem;
  text-decoration: none;
  transition: color 0.2s;
  padding: 0.25rem 0;
}
.back-footer-link:hover { color: #818cf8; }

@media (max-width: 640px) {
  .page-container { padding: 1rem 1rem 4rem; }
  .post-header { padding: 1.25rem; }
  .post-title { font-size: 1.4rem; }
  .post-content { padding: 1.5rem 1.25rem; }
  .cta-box { flex-direction: column; align-items: flex-start; }
}
</style>

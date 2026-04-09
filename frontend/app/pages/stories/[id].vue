<template>
  <div class="page-container">
    <div class="background-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <main class="content-wrapper anim-fade-in">

      <!-- Back -->
      <NuxtLink to="/stories" class="back-btn anim-slide-up">
        <i class="pi pi-arrow-left"></i>
        Story Archive
      </NuxtLink>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <i class="pi pi-spinner pi-spin"></i>
        <span>Loading story...</span>
      </div>

      <!-- Not found -->
      <div v-else-if="!story" class="empty-state glass-effect">
        <i class="pi pi-exclamation-circle"></i>
        <p>Story not found.</p>
        <NuxtLink to="/stories" class="back-link">← Back to archive</NuxtLink>
      </div>

      <!-- Story card -->
      <article v-else class="story-card glass-effect anim-slide-up delay-1">

        <!-- Meta row -->
        <div class="story-meta">
          <span class="level-badge" :class="`level-${story.level.toLowerCase()}`">
            {{ story.level.toUpperCase() }}
          </span>
          <span class="date-text">
            <i class="pi pi-calendar"></i>
            {{ formatDate(story.created_at) }}
          </span>
          <button class="copy-btn" @click="copyStory">
            <i :class="copied ? 'pi pi-check' : 'pi pi-copy'" />
            {{ copied ? 'Copied!' : 'Copy' }}
          </button>
        </div>

        <!-- Topic -->
        <h1 class="story-topic">
          <i class="pi pi-tag topic-icon"></i>
          {{ story.topic }}
        </h1>

        <hr class="divider" />

        <!-- Illustration -->
        <div class="illustration-section">
          <Transition name="fade">
            <!-- Loading skeleton -->
            <div v-if="imageLoading" class="illustration-skeleton">
              <i class="pi pi-spinner pi-spin"></i>
              <span>Generating illustration...</span>
            </div>
            <!-- Generated image -->
            <div v-else-if="imageUrl" class="illustration-wrapper">
              <img :src="imageUrl" :alt="`Illustration for ${story.topic}`" class="story-image" />
            </div>
          </Transition>
        </div>

        <hr class="divider" />

        <!-- Content -->
        <p class="story-text">{{ story.content }}</p>

      </article>

    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const route = useRoute();
const config = useRuntimeConfig();

const story = ref(null);
const loading = ref(true);
const copied = ref(false);
const imageUrl = ref(null);
const imageLoading = ref(false);

const fetchStory = async () => {
  loading.value = true;
  try {
    story.value = await $fetch(`${config.public.apiBase}/api/v1/story/${route.params.id}`);
  } catch {
    story.value = null;
  } finally {
    loading.value = false;
  }
};

const generateImage = async () => {
  imageLoading.value = true;
  // Revoke previous object URL to free memory
  if (imageUrl.value) {
    URL.revokeObjectURL(imageUrl.value);
    imageUrl.value = null;
  }
  try {
    const blob = await $fetch(`${config.public.apiBase}/api/v1/story/${route.params.id}/image`, {
      responseType: 'blob',
    });
    imageUrl.value = URL.createObjectURL(blob);
  } catch {
    // silently fail — user can retry
  } finally {
    imageLoading.value = false;
  }
};

const copyStory = async () => {
  if (!story.value) return;
  await navigator.clipboard.writeText(story.value.content);
  copied.value = true;
  setTimeout(() => { copied.value = false; }, 2000);
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('en-GB', {
    day: 'numeric', month: 'long', year: 'numeric'
  });
};

useHead(computed(() => ({
  title: story.value ? `${story.value.topic} — English Story` : 'Story — English Story'
})));

onMounted(async () => {
  await fetchStory();
  if (story.value) generateImage();
});
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
  opacity: 0.5;
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
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 720px;
  padding: 2rem 0;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.9rem;
  transition: color 0.2s;
  width: fit-content;
}
.back-btn:hover { color: var(--text-main); }

/* States */
.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 4rem 2rem;
  color: var(--text-muted);
  text-align: center;
}
.loading-state i, .empty-state i { font-size: 2.5rem; opacity: 0.5; }

.back-link {
  color: #818cf8;
  font-size: 0.9rem;
  transition: opacity 0.2s;
}
.back-link:hover { opacity: 0.75; }

/* Story card */
.story-card {
  padding: 2.5rem;
}

.story-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 1.25rem;
}

.level-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 50px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  background: rgba(129,140,248,0.2);
  border: 1px solid rgba(129,140,248,0.3);
  color: #818cf8;
}
.level-badge.level-a1 { background: rgba(52,211,153,0.15); border-color: rgba(52,211,153,0.3); color: #34d399; }
.level-badge.level-a2 { background: rgba(96,165,250,0.15); border-color: rgba(96,165,250,0.3); color: #60a5fa; }
.level-badge.level-b1 { background: rgba(251,191,36,0.15); border-color: rgba(251,191,36,0.3); color: #fbbf24; }
.level-badge.level-b2 { background: rgba(249,115,22,0.15); border-color: rgba(249,115,22,0.3); color: #f97316; }
.level-badge.level-beginner { background: rgba(52,211,153,0.15); border-color: rgba(52,211,153,0.3); color: #34d399; }
.level-badge.level-intermediate { background: rgba(251,191,36,0.15); border-color: rgba(251,191,36,0.3); color: #fbbf24; }
.level-badge.level-advanced { background: rgba(239,68,68,0.15); border-color: rgba(239,68,68,0.3); color: #ef4444; }

.date-text {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.copy-btn {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.9rem;
  border-radius: 50px;
  background: rgba(99,102,241,0.15);
  border: 1px solid rgba(99,102,241,0.3);
  color: #818cf8;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background 0.2s;
}
.copy-btn:hover { background: rgba(99,102,241,0.25); }

.story-topic {
  margin: 0 0 1.25rem;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-main);
  display: flex;
  align-items: center;
  gap: 0.6rem;
  line-height: 1.3;
}
.topic-icon { color: #f59e0b; font-size: 1.1rem; flex-shrink: 0; }

.divider {
  border: none;
  border-top: 1px solid rgba(255,255,255,0.08);
  margin: 0 0 1.5rem;
}

/* Illustration */
.illustration-section {
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.illustration-wrapper {
  width: 100%;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.1);
}

.story-image {
  width: 100%;
  display: block;
  object-fit: cover;
  max-height: 420px;
}

.illustration-skeleton {
  width: 100%;
  min-height: 200px;
  border-radius: 16px;
  background: rgba(255,255,255,0.04);
  border: 1px dashed rgba(255,255,255,0.12);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}
.illustration-skeleton i { font-size: 1.8rem; opacity: 0.5; }

/* Fade transition */
.fade-enter-active, .fade-leave-active { transition: opacity 0.4s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.story-text {
  font-size: 1.05rem;
  line-height: 1.95;
  color: var(--text-main);
  margin: 0;
  white-space: pre-wrap;
}

@media (max-width: 640px) {
  .page-container { padding: 1rem; }
  .story-card { padding: 1.5rem; }
  .story-topic { font-size: 1.25rem; }
}
</style>

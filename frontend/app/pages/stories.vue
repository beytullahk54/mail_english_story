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
        <NuxtLink to="/" class="back-btn">
          <i class="pi pi-arrow-left"></i>
          Back
        </NuxtLink>
        <div class="header-title">
          <i class="pi pi-book"></i>
          <h1>Story Archive</h1>
        </div>
        <p class="header-sub">Browse all generated English stories</p>
      </div>

      <!-- Filters -->
      <div class="filters-bar glass-effect anim-slide-up delay-1">
        <Select
          v-model="filterLevel"
          :options="levelOptions"
          option-label="label"
          option-value="value"
          placeholder="All Levels"
          class="filter-select"
          @change="fetchStories"
        />
        <div class="total-badge" v-if="total > 0">
          <i class="pi pi-list"></i>
          {{ total }} stories
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="loading-state">
        <i class="pi pi-spinner pi-spin"></i>
        <span>Loading stories...</span>
      </div>

      <!-- Empty state -->
      <div v-else-if="stories.length === 0" class="empty-state glass-effect">
        <i class="pi pi-inbox"></i>
        <p>No stories found.</p>
      </div>

      <!-- Stories grid -->
      <div v-else class="stories-grid">
        <div
          v-for="story in stories"
          :key="story.id"
          class="story-card glass-effect"
          :class="{ expanded: expandedId === story.id }"
        >
          <div class="story-card-header" @click="toggleExpand(story.id)">
            <div class="story-meta">
              <span class="level-badge" :class="`level-${story.level.toLowerCase()}`">
                {{ story.level.toUpperCase() }}
              </span>
              <span class="date-text">
                <i class="pi pi-calendar"></i>
                {{ formatDate(story.created_at) }}
              </span>
            </div>
            <div class="story-topic">
              <i class="pi pi-tag"></i>
              {{ story.topic }}
            </div>
            <i class="pi expand-icon" :class="expandedId === story.id ? 'pi-chevron-up' : 'pi-chevron-down'"></i>
          </div>

          <Transition name="expand">
            <div v-if="expandedId === story.id" class="story-body">
              <p class="story-text">{{ story.content }}</p>
              <button class="copy-btn" @click="copyStory(story)">
                <i :class="copiedId === story.id ? 'pi pi-check' : 'pi pi-copy'" />
                {{ copiedId === story.id ? 'Copied!' : 'Copy' }}
              </button>
            </div>
          </Transition>
        </div>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination anim-slide-up">
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

const stories = ref([]);
const total = ref(0);
const page = ref(1);
const pageSize = 10;
const loading = ref(false);
const filterLevel = ref(null);
const expandedId = ref(null);
const copiedId = ref(null);

const totalPages = computed(() => Math.ceil(total.value / pageSize));

const levelOptions = [
  { label: 'All Levels', value: null },
  { label: 'A1', value: 'a1' },
  { label: 'A2', value: 'a2' },
  { label: 'B1', value: 'b1' },
  { label: 'B2', value: 'b2' },
  { label: 'Beginner', value: 'beginner' },
  { label: 'Intermediate', value: 'intermediate' },
  { label: 'Advanced', value: 'advanced' },
];

const fetchStories = async () => {
  loading.value = true;
  expandedId.value = null;

  const params = new URLSearchParams({
    page: page.value,
    page_size: pageSize,
  });
  if (filterLevel.value) params.set('level', filterLevel.value);

  try {
    const data = await $fetch(`${config.public.apiBase}/api/v1/story/list?${params}`);
    stories.value = data.items;
    total.value = data.total;
  } catch {
    stories.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
};

const goToPage = (p) => {
  page.value = p;
  fetchStories();
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

const toggleExpand = (id) => {
  expandedId.value = expandedId.value === id ? null : id;
};

const copyStory = async (story) => {
  await navigator.clipboard.writeText(story.content);
  copiedId.value = story.id;
  setTimeout(() => { copiedId.value = null; }, 2000);
};

const formatDate = (dateStr) => {
  return new Date(dateStr).toLocaleDateString('en-GB', {
    day: 'numeric', month: 'short', year: 'numeric'
  });
};

useHead({ title: 'Story Archive — English Story' });

onMounted(fetchStories);
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
  max-width: 760px;
  padding: 2rem 0;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Header */
.back-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.9rem;
  transition: color 0.2s;
  width: fit-content;
  margin-bottom: 0.5rem;
}
.back-btn:hover { color: var(--text-main); }

.header-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.4rem;
}
.header-title i { font-size: 1.5rem; color: #c084fc; }
.header-title h1 { margin: 0; font-size: 2rem; font-weight: 700; }

.header-sub { margin: 0; color: var(--text-muted); font-size: 0.95rem; }

/* Filters */
.filters-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
}

:deep(.filter-select) {
  border-radius: 10px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.15);
  min-width: 160px;
}
:deep(.filter-select .p-select-label) { color: white; padding: 0.6rem 0.85rem; }

.total-badge {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: var(--text-muted);
}

/* States */
.loading-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 4rem 2rem;
  color: var(--text-muted);
  font-size: 1rem;
}
.loading-state i, .empty-state i { font-size: 2rem; opacity: 0.5; }

/* Stories grid */
.stories-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.story-card {
  overflow: hidden;
  transition: border-color 0.2s;
}
.story-card.expanded {
  border-color: rgba(129,140,248,0.4);
}

.story-card-header {
  padding: 1.25rem 1.5rem;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  position: relative;
  user-select: none;
}

.story-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.level-badge {
  padding: 0.2rem 0.65rem;
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

.story-topic {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-main);
}
.story-topic i { color: #f59e0b; font-size: 0.85rem; }

.expand-icon {
  position: absolute;
  right: 1.5rem;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  font-size: 0.85rem;
}

/* Story body */
.story-body {
  padding: 0 1.5rem 1.5rem;
  border-top: 1px solid rgba(255,255,255,0.07);
}

.story-text {
  font-size: 1rem;
  line-height: 1.9;
  color: var(--text-main);
  margin: 1.25rem 0 1rem;
  white-space: pre-wrap;
}

.copy-btn {
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

/* Expand transition */
.expand-enter-active, .expand-leave-active {
  transition: all 0.3s ease;
  overflow: hidden;
}
.expand-enter-from, .expand-leave-to {
  opacity: 0;
  max-height: 0;
}
.expand-enter-to, .expand-leave-from {
  opacity: 1;
  max-height: 2000px;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 0.5rem 0;
}

.page-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.15);
  color: var(--text-main);
  cursor: pointer;
  transition: background 0.2s;
}
.page-btn:hover:not(:disabled) { background: rgba(255,255,255,0.12); }
.page-btn:disabled { opacity: 0.3; cursor: not-allowed; }

.page-info {
  font-size: 0.9rem;
  color: var(--text-muted);
  min-width: 60px;
  text-align: center;
}

@media (max-width: 640px) {
  .page-container { padding: 1rem; }
  .header-title h1 { font-size: 1.6rem; }
}
</style>

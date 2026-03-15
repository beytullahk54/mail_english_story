<template>
  <div class="page-container">
    <Toast />

    <div class="background-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <main class="content-wrapper anim-fade-in">

      <!-- Back button -->
      <NuxtLink to="/" class="back-btn anim-slide-up">
        <i class="pi pi-arrow-left"></i>
        Geri
      </NuxtLink>

      <!-- Form Card -->
      <div class="card glass-effect anim-slide-up delay-1">
        <div class="card-header">
          <div class="icon-wrapper">
            <i class="pi pi-sparkles sparkle-icon"></i>
          </div>
          <h1 class="title">
            <span class="glow-text">AI</span> ile Hikaye Oluştur
          </h1>
          <p class="subtitle">Konuyu ve seviyeyi seç, Gemini senin için bir İngilizce hikaye yazsın.</p>
        </div>

        <form class="story-form" @submit.prevent="generateStory">
          <div class="form-row">
            <div class="form-field">
              <label>Konu</label>
              <div class="input-wrapper">
                <i class="pi pi-pencil field-icon" />
                <InputText
                  v-model="topic"
                  placeholder="örn: a dog lost in the forest"
                  class="field-input"
                  required
                />
              </div>
            </div>
          </div>

          <div class="form-row two-col">
            <div class="form-field">
              <label>Seviye</label>
              <Select
                v-model="level"
                :options="levels"
                option-label="label"
                option-value="value"
                placeholder="Seç"
                class="field-select"
              />
            </div>
            <div class="form-field">
              <label>Kelime Sayısı <span class="muted">({{ wordCount }})</span></label>
              <Slider v-model="wordCount" :min="50" :max="500" :step="50" class="word-slider" />
            </div>
          </div>

          <Button type="submit" class="generate-btn" :loading="loading" :disabled="!topic.trim()">
            <i class="pi pi-sparkles" />
            Hikaye Oluştur
          </Button>
        </form>
      </div>

      <!-- Story Result -->
      <Transition name="fade-up">
        <div v-if="story" class="story-card glass-effect">
          <div class="story-meta">
            <span class="meta-badge">
              <i class="pi pi-flag"></i>
              {{ levelLabel }}
            </span>
            <span class="meta-badge">
              <i class="pi pi-book"></i>
              {{ wordCountDisplay }} kelime
            </span>
            <button class="copy-btn" @click="copyStory">
              <i :class="copied ? 'pi pi-check' : 'pi pi-copy'" />
              {{ copied ? 'Kopyalandı' : 'Kopyala' }}
            </button>
          </div>
          <div class="story-topic">
            <i class="pi pi-tag"></i>
            {{ story.topic }}
          </div>
          <p class="story-text">{{ story.story }}</p>
        </div>
      </Transition>

    </main>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useToast } from 'primevue/usetoast';

const toast = useToast();
const config = useRuntimeConfig();

const topic = ref('');
const level = ref('beginner');
const wordCount = ref(150);
const loading = ref(false);
const story = ref(null);
const copied = ref(false);

const levels = [
  { label: 'Beginner (A1-A2)', value: 'beginner' },
  { label: 'Intermediate (B1-B2)', value: 'intermediate' },
  { label: 'Advanced (C1-C2)', value: 'advanced' },
];

const levelLabel = computed(() => levels.find(l => l.value === level.value)?.label ?? level.value);
const wordCountDisplay = computed(() => story.value?.story.split(/\s+/).length ?? 0);

const generateStory = async () => {
  loading.value = true;
  story.value = null;

  try {
    const result = await $fetch(`${config.public.apiBase}/api/v1/story/generate`, {
      method: 'POST',
      body: {
        topic: topic.value,
        level: level.value,
        word_count: wordCount.value,
      }
    });

    story.value = result;
  } catch (error) {
    toast.add({
      severity: 'error',
      summary: 'Hata',
      detail: error.data?.detail || 'Hikaye oluşturulamadı.',
      life: 4000,
    });
  } finally {
    loading.value = false;
  }
};

const copyStory = async () => {
  if (!story.value) return;
  await navigator.clipboard.writeText(story.value.story);
  copied.value = true;
  setTimeout(() => { copied.value = false; }, 2000);
};
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
  max-width: 680px;
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

/* Form card */
.card {
  padding: 2.5rem;
}

.card-header {
  text-align: center;
  margin-bottom: 2rem;
}

.icon-wrapper {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  width: 68px;
  height: 68px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  margin-bottom: 1.2rem;
  border: 1px solid rgba(255,255,255,0.15);
}

.sparkle-icon {
  font-size: 2rem;
  color: #f59e0b;
}

.title {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
}

.subtitle {
  color: var(--text-muted);
  font-size: 0.95rem;
  margin: 0;
}

/* Form */
.story-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-row.two-col {
  flex-direction: row;
  gap: 1.2rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex: 1;
}

.form-field label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.muted { font-weight: 400; }

.input-wrapper {
  position: relative;
  display: flex;
}

.field-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255,255,255,0.4);
  z-index: 1;
}

:deep(.field-input) {
  width: 100%;
  padding: 0.85rem 0.85rem 0.85rem 2.8rem !important;
  font-size: 1rem;
  border-radius: 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.15);
  color: white;
  transition: all 0.2s;
}

:deep(.field-input:focus) {
  background: rgba(255,255,255,0.08);
  border-color: #818cf8;
  box-shadow: 0 0 0 2px rgba(129,140,248,0.2);
  outline: none;
}

:deep(.field-select) {
  border-radius: 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.15);
}

:deep(.field-select .p-select-label) {
  color: white;
  padding: 0.85rem;
}

:deep(.field-select .p-select-dropdown) {
  color: rgba(255,255,255,0.6);
}

:deep(.word-slider) {
  margin-top: 0.6rem;
}

:deep(.generate-btn) {
  width: 100%;
  padding: 1rem;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

:deep(.generate-btn:hover:not(:disabled)) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(245,158,11,0.3);
}

/* Story result */
.story-card {
  padding: 2rem;
}

.story-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.meta-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.8rem;
  border-radius: 50px;
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.12);
  font-size: 0.8rem;
  color: var(--text-muted);
}

.copy-btn {
  margin-left: auto;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.3rem 0.9rem;
  border-radius: 50px;
  background: rgba(99,102,241,0.15);
  border: 1px solid rgba(99,102,241,0.3);
  color: #818cf8;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}
.copy-btn:hover { background: rgba(99,102,241,0.25); }

.story-topic {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #f59e0b;
  margin-bottom: 1.2rem;
  font-style: italic;
}

.story-text {
  font-size: 1.05rem;
  line-height: 1.9;
  color: var(--text-main);
  margin: 0;
  white-space: pre-wrap;
}

/* Transition */
.fade-up-enter-active { transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1); }
.fade-up-enter-from { opacity: 0; transform: translateY(20px); }

@media (max-width: 640px) {
  .form-row.two-col { flex-direction: column; }
  .card { padding: 1.5rem; }
  .title { font-size: 1.6rem; }
}
</style>

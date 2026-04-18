<template>
  <div class="form-wrapper">

    <!-- Tabs: EN / TR -->
    <div class="lang-tabs glass-effect">
      <button class="tab-btn" :class="{ active: tab === 'en' }" @click="tab = 'en'">
        <i class="pi pi-flag"></i> English
      </button>
      <button class="tab-btn" :class="{ active: tab === 'tr' }" @click="tab = 'tr'">
        <i class="pi pi-flag"></i> Türkçe
      </button>
      <div class="tab-separator"></div>
      <label class="pub-toggle">
        <span>Yayında</span>
        <ToggleSwitch v-model="form.published" />
      </label>
    </div>

    <!-- EN Fields -->
    <div v-show="tab === 'en'" class="fields-card glass-effect">
      <h3 class="section-title"><i class="pi pi-flag"></i> English Content</h3>

      <div class="field">
        <label>Title <span class="req">*</span></label>
        <InputText v-model="form.title" placeholder="Article title" class="w-full" @input="autoSlug('en')" />
      </div>

      <div class="field">
        <label>Slug <span class="req">*</span></label>
        <InputText v-model="form.slug" placeholder="url-friendly-slug" class="w-full" />
        <small>Otomatik oluşturulur, düzenleyebilirsin</small>
      </div>

      <div class="field">
        <label>Excerpt / Kısa Açıklama <span class="req">*</span></label>
        <Textarea v-model="form.excerpt" rows="3" placeholder="1-2 cümle özet" class="w-full" autoResize />
      </div>

      <div class="field">
        <label>Content (HTML) <span class="req">*</span></label>
        <Textarea v-model="form.content" rows="14" placeholder="<p>İçerik buraya...</p>" class="w-full content-area" />
      </div>

      <div class="field">
        <label>Meta Description (SEO)</label>
        <InputText v-model="form.meta_description" placeholder="Max 160 karakter" class="w-full" maxlength="160" />
        <small>{{ (form.meta_description || '').length }} / 160</small>
      </div>
    </div>

    <!-- TR Fields -->
    <div v-show="tab === 'tr'" class="fields-card glass-effect">
      <h3 class="section-title"><i class="pi pi-flag"></i> Türkçe İçerik</h3>

      <div class="field">
        <label>Başlık</label>
        <InputText v-model="form.title_tr" placeholder="Makale başlığı" class="w-full" @input="autoSlug('tr')" />
      </div>

      <div class="field">
        <label>Slug (TR)</label>
        <InputText v-model="form.slug_tr" placeholder="url-uyumlu-slug" class="w-full" />
        <small>Otomatik oluşturulur, düzenleyebilirsin</small>
      </div>

      <div class="field">
        <label>Özet</label>
        <Textarea v-model="form.excerpt_tr" rows="3" placeholder="1-2 cümle özet" class="w-full" autoResize />
      </div>

      <div class="field">
        <label>İçerik (HTML)</label>
        <Textarea v-model="form.content_tr" rows="14" placeholder="<p>İçerik buraya...</p>" class="w-full content-area" />
      </div>

      <div class="field">
        <label>Meta Description (SEO)</label>
        <InputText v-model="form.meta_description_tr" placeholder="Max 160 karakter" class="w-full" maxlength="160" />
        <small>{{ (form.meta_description_tr || '').length }} / 160</small>
      </div>
    </div>

    <!-- Common Fields -->
    <div class="fields-card glass-effect">
      <h3 class="section-title"><i class="pi pi-cog"></i> Genel</h3>

      <div class="fields-row">
        <div class="field">
          <label>Yazar</label>
          <InputText v-model="form.author" placeholder="English Story Team" class="w-full" />
        </div>
        <div class="field">
          <label>Etiketler (virgülle ayır)</label>
          <InputText v-model="tagsInput" placeholder="learning, tips, vocabulary" class="w-full" />
        </div>
      </div>

      <div class="field">
        <label>Kapak Görseli URL</label>
        <InputText v-model="form.cover_image" placeholder="https://..." class="w-full" />
      </div>
    </div>

    <!-- Error -->
    <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>

    <!-- Submit -->
    <div class="form-footer">
      <NuxtLink to="/admin/blog" class="cancel-btn">İptal</NuxtLink>
      <button class="save-btn" :disabled="saving || !form.title || !form.slug" @click="handleSubmit">
        <i v-if="saving" class="pi pi-spinner pi-spin"></i>
        <i v-else class="pi pi-check"></i>
        {{ saving ? 'Kaydediliyor...' : 'Kaydet' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const props = defineProps({
  initial: { type: Object, default: null },
  saving: Boolean,
  error: String,
});

const emit = defineEmits(['submit']);

const tab = ref('en');

const toSlug = (text) =>
  (text || '')
    .toLowerCase()
    .replace(/[çÇ]/g, 'c').replace(/[ğĞ]/g, 'g')
    .replace(/[ıİ]/g, 'i').replace(/[öÖ]/g, 'o')
    .replace(/[şŞ]/g, 's').replace(/[üÜ]/g, 'u')
    .replace(/[^a-z0-9\s-]/g, '')
    .trim().replace(/\s+/g, '-').replace(/-+/g, '-');

const form = ref({
  title: '', title_tr: '',
  slug: '', slug_tr: '',
  excerpt: '', excerpt_tr: '',
  content: '', content_tr: '',
  author: 'English Story Team',
  cover_image: '',
  meta_description: '', meta_description_tr: '',
  published: true,
});

const tagsInput = ref('');

// Populate from initial (edit mode)
if (props.initial) {
  const p = props.initial;
  form.value = {
    title: p.title || '',
    title_tr: p.title_tr || '',
    slug: p.slug || '',
    slug_tr: p.slug_tr || '',
    excerpt: p.excerpt || '',
    excerpt_tr: p.excerpt_tr || '',
    content: p.content || '',
    content_tr: p.content_tr || '',
    author: p.author || 'English Story Team',
    cover_image: p.cover_image || '',
    meta_description: p.meta_description || '',
    meta_description_tr: p.meta_description_tr || '',
    published: p.published !== false,
  };
  tagsInput.value = (p.tags || []).join(', ');
}

const autoSlug = (lang) => {
  if (lang === 'en' && form.value.title) {
    form.value.slug = toSlug(form.value.title);
  }
  if (lang === 'tr' && form.value.title_tr) {
    form.value.slug_tr = toSlug(form.value.title_tr);
  }
};

const handleSubmit = () => {
  const tags = tagsInput.value
    ? tagsInput.value.split(',').map(t => t.trim()).filter(Boolean)
    : [];
  emit('submit', { ...form.value, tags });
};
</script>

<style scoped>
.form-wrapper { display: flex; flex-direction: column; gap: 1.25rem; }

.lang-tabs {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.75rem 1.25rem; border-radius: 16px; flex-wrap: wrap;
}
.tab-btn {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.45rem 1rem; border-radius: 8px;
  background: transparent; border: 1px solid rgba(255,255,255,0.1);
  color: var(--text-muted); font-family: inherit; font-size: 0.88rem;
  cursor: pointer; transition: all 0.2s;
}
.tab-btn:hover { color: var(--text-main); }
.tab-btn.active { background: rgba(99,102,241,0.2); border-color: rgba(99,102,241,0.5); color: #818cf8; }

.tab-separator { flex: 1; }

.pub-toggle {
  display: flex; align-items: center; gap: 0.6rem;
  font-size: 0.88rem; color: var(--text-muted); cursor: pointer;
}

.fields-card {
  padding: 1.75rem; border-radius: 16px;
  display: flex; flex-direction: column; gap: 1.25rem;
}

.section-title {
  margin: 0 0 0.25rem; font-size: 0.95rem; font-weight: 600;
  color: var(--text-muted); display: flex; align-items: center; gap: 0.4rem;
}
.section-title i { color: #818cf8; }

.fields-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }

.field { display: flex; flex-direction: column; gap: 0.4rem; }
.field label { font-size: 0.83rem; color: var(--text-muted); font-weight: 500; }
.field small { font-size: 0.75rem; color: rgba(203,213,225,0.5); }
.req { color: #f97316; }

:deep(.p-inputtext), :deep(.p-textarea) {
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  color: var(--text-main) !important;
  border-radius: 10px !important;
  font-family: inherit !important;
}
:deep(.p-inputtext:focus), :deep(.p-textarea:focus) {
  border-color: rgba(129,140,248,0.5) !important;
  box-shadow: 0 0 0 2px rgba(99,102,241,0.15) !important;
}
.content-area { font-family: 'Courier New', monospace !important; font-size: 0.85rem !important; }

.form-footer {
  display: flex; align-items: center; justify-content: flex-end; gap: 0.75rem; padding-top: 0.5rem;
}
.cancel-btn {
  padding: 0.7rem 1.5rem; border-radius: 10px;
  background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.12);
  color: var(--text-muted); font-size: 0.9rem; text-decoration: none; transition: all 0.2s;
}
.cancel-btn:hover { color: var(--text-main); }
.save-btn {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.7rem 1.75rem; border-radius: 10px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6); border: none;
  color: white; font-weight: 600; font-size: 0.9rem; font-family: inherit;
  cursor: pointer; transition: opacity 0.2s, transform 0.2s;
}
.save-btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
.save-btn:disabled { opacity: 0.5; cursor: not-allowed; }

@media (max-width: 640px) {
  .fields-row { grid-template-columns: 1fr; }
  .fields-card { padding: 1.25rem; }
}
</style>

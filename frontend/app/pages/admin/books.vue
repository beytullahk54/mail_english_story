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
          <i class="pi pi-book"></i>
          <span>Kitap Özetleri</span>
        </div>
        <div class="topbar-right">
          <NuxtLink to="/admin/blog" class="icon-btn" title="Blog Yönetimi">
            <i class="pi pi-pencil"></i>
          </NuxtLink>
          <NuxtLink to="/admin/subscribers" class="icon-btn" title="Aboneler">
            <i class="pi pi-users"></i>
          </NuxtLink>
          <button class="icon-btn danger" @click="handleLogout" title="Çıkış">
            <i class="pi pi-sign-out"></i>
          </button>
        </div>
      </header>

      <main class="admin-content">

        <!-- Send button + result -->
        <div class="send-card glass-effect">
          <div class="send-info">
            <div class="send-title">
              <i class="pi pi-send"></i>
              Günlük Özet Gönder
            </div>
            <div class="send-sub">Sıradaki kitabın Türkçe özetini {{ adminEmail }} adresine gönderir.</div>
          </div>
          <button class="send-btn" :disabled="sending" @click="sendDaily">
            <i v-if="sending" class="pi pi-spinner pi-spin"></i>
            <i v-else class="pi pi-paper-plane"></i>
            {{ sending ? 'Gönderiliyor...' : 'Gönder' }}
          </button>
        </div>

        <div v-if="sendResult" class="result-msg" :class="sendResult.type">
          <i :class="sendResult.type === 'success' ? 'pi pi-check-circle' : 'pi pi-exclamation-circle'"></i>
          {{ sendResult.text }}
        </div>

        <!-- Add book -->
        <div class="add-card glass-effect">
          <form class="add-form" @submit.prevent="addBook">
            <input v-model="newTitle" type="text" placeholder="Kitap adı" class="add-input" required />
            <input v-model="newAuthor" type="text" placeholder="Yazar" class="add-input" required />
            <button class="add-btn" type="submit" :disabled="adding">
              <i v-if="adding" class="pi pi-spinner pi-spin"></i>
              <i v-else class="pi pi-plus"></i>
              {{ adding ? 'Ekleniyor...' : 'Ekle' }}
            </button>
          </form>
          <button class="ai-btn" @click="suggestAi" :disabled="aiSuggesting">
            <i v-if="aiSuggesting" class="pi pi-spinner pi-spin"></i>
            <i v-else class="pi pi-sparkles"></i>
            {{ aiSuggesting ? 'AI Öneriyor...' : 'AI ile 10 Kitap Ekle' }}
          </button>
        </div>

        <!-- Book list -->
        <div class="section-header">
          <h2>Kitap Listesi <span class="count">{{ books.length }}</span></h2>
          <button class="seed-btn" @click="seedBooks" :disabled="seeding">
            <i class="pi pi-database"></i>
            {{ seeding ? 'Ekleniyor...' : 'Seed (30 Kitap)' }}
          </button>
        </div>

        <div v-if="loading" class="state-box">
          <i class="pi pi-spinner pi-spin"></i>
        </div>

        <div v-else-if="books.length === 0" class="state-box glass-effect">
          <i class="pi pi-inbox"></i>
          <p>Kitap yok. "Seed" butonuyla 30 klasik kitabı ekleyebilirsin.</p>
        </div>

        <div v-else class="table-wrap glass-effect">
          <table class="book-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Kitap</th>
                <th>Yazar</th>
                <th>Son Gönderim</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="b in books" :key="b.id">
                <td class="muted">{{ b.id }}</td>
                <td class="book-title">{{ b.title }}</td>
                <td class="muted">{{ b.author }}</td>
                <td class="muted">{{ b.last_sent_at ? formatDate(b.last_sent_at) : '—' }}</td>
                <td>
                  <button class="del-btn" @click="deleteBook(b.id)" title="Sil">
                    <i class="pi pi-trash"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

definePageMeta({ middleware: 'admin', layout: false })

const config = useRuntimeConfig()
const { authHeaders, logout } = useAdmin()

const books = ref([])
const loading = ref(false)
const sending = ref(false)
const seeding = ref(false)
const adding = ref(false)
const aiSuggesting = ref(false)
const newTitle = ref('')
const newAuthor = ref('')
const sendResult = ref(null)
const adminEmail = ref('admin')

const fetchBooks = async () => {
  loading.value = true
  try {
    const data = await $fetch(`${config.public.apiBase}/api/v1/books`, {
      headers: authHeaders.value,
    })
    books.value = data.items
  } catch (e) {
    if (e.status === 401) navigateTo('/admin/login')
  } finally {
    loading.value = false
  }
}

const sendDaily = async () => {
  sending.value = true
  sendResult.value = null
  try {
    const res = await $fetch(`${config.public.apiBase}/api/v1/books/send-daily`, {
      method: 'POST',
      headers: authHeaders.value,
    })
    if (res.status === 'sent') {
      sendResult.value = { type: 'success', text: `✅ Gönderildi: "${res.book}" → ${res.to}` }
      await fetchBooks()
    } else {
      sendResult.value = { type: 'warn', text: `⚠️ ${res.reason}` }
    }
  } catch (e) {
    sendResult.value = { type: 'error', text: `❌ ${e?.data?.detail || 'Gönderilemedi'}` }
  } finally {
    sending.value = false
    setTimeout(() => { sendResult.value = null }, 7000)
  }
}

const seedBooks = async () => {
  seeding.value = true
  try {
    const res = await $fetch(`${config.public.apiBase}/api/v1/books/seed`, {
      method: 'POST',
      headers: authHeaders.value,
    })
    await fetchBooks()
    sendResult.value = { type: 'success', text: `✅ ${res.message}` }
    setTimeout(() => { sendResult.value = null }, 5000)
  } finally {
    seeding.value = false
  }
}

const addBook = async () => {
  adding.value = true
  try {
    await $fetch(`${config.public.apiBase}/api/v1/books`, {
      method: 'POST',
      headers: authHeaders.value,
      body: { title: newTitle.value.trim(), author: newAuthor.value.trim() },
    })
    newTitle.value = ''
    newAuthor.value = ''
    await fetchBooks()
    sendResult.value = { type: 'success', text: '✅ Kitap eklendi.' }
    setTimeout(() => { sendResult.value = null }, 5000)
  } catch (e) {
    sendResult.value = { type: 'error', text: `❌ ${e?.data?.detail || 'Eklenemedi'}` }
    setTimeout(() => { sendResult.value = null }, 5000)
  } finally {
    adding.value = false
  }
}

const suggestAi = async () => {
  aiSuggesting.value = true
  try {
    const res = await $fetch(`${config.public.apiBase}/api/v1/books/suggest-ai`, {
      method: 'POST',
      headers: authHeaders.value,
    })
    await fetchBooks()
    sendResult.value = { type: 'success', text: `✅ ${res.message}` }
    setTimeout(() => { sendResult.value = null }, 6000)
  } catch (e) {
    sendResult.value = { type: 'error', text: `❌ ${e?.data?.detail || 'AI önerisi alınamadı'}` }
    setTimeout(() => { sendResult.value = null }, 6000)
  } finally {
    aiSuggesting.value = false
  }
}

const deleteBook = async (id) => {
  if (!confirm('Bu kitabı silmek istiyor musun?')) return
  try {
    await $fetch(`${config.public.apiBase}/api/v1/books/${id}`, {
      method: 'DELETE',
      headers: authHeaders.value,
    })
    await fetchBooks()
  } catch (e) {
    alert('Silinemedi')
  }
}

const formatDate = (d) => new Date(d).toLocaleDateString('tr-TR', {
  day: 'numeric', month: 'short', year: 'numeric',
})

const handleLogout = () => { logout(); navigateTo('/admin/login') }

useHead({ title: 'Kitap Özetleri — Admin' })
onMounted(fetchBooks)
</script>

<style scoped>
.admin-container { min-height: 100vh; display: flex; justify-content: center; background: var(--bg-main); position: relative; overflow: hidden; }
.background-shapes { position: absolute; inset: 0; z-index: 0; overflow: hidden; }
.shape { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.4; animation: float 12s infinite alternate ease-in-out; }
.shape-1 { width: 500px; height: 500px; background: #6366f1; top: -15%; left: -10%; }
.shape-2 { width: 400px; height: 400px; background: #c084fc; bottom: -15%; right: -10%; animation-delay: -6s; }
@keyframes float { 0% { transform: translate(0,0); } 100% { transform: translate(30px,40px); } }

.admin-wrapper { position: relative; z-index: 10; width: 100%; max-width: 900px; padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem; }

.topbar { display: flex; align-items: center; justify-content: space-between; padding: 0.85rem 1.25rem; border-radius: 14px; }
.topbar-left { display: flex; align-items: center; gap: 0.6rem; font-weight: 600; font-size: 1rem; }
.topbar-left i { color: #818cf8; }
.topbar-right { display: flex; gap: 0.5rem; }
.icon-btn { display: flex; align-items: center; justify-content: center; width: 36px; height: 36px; border-radius: 8px; background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.12); color: var(--text-muted); cursor: pointer; transition: all 0.2s; text-decoration: none; font-size: 0.9rem; }
.icon-btn:hover { background: rgba(255,255,255,0.14); color: white; }
.icon-btn.danger:hover { background: rgba(239,68,68,0.15); border-color: rgba(239,68,68,0.3); color: #f87171; }

.admin-content { display: flex; flex-direction: column; gap: 1.25rem; }

/* Send card */
.send-card { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 1.25rem 1.5rem; border-radius: 14px; flex-wrap: wrap; }
.send-title { display: flex; align-items: center; gap: 0.5rem; font-weight: 600; font-size: 1rem; margin-bottom: 0.3rem; }
.send-title i { color: #818cf8; }
.send-sub { font-size: 0.82rem; color: var(--text-muted); }
.send-btn { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.65rem 1.4rem; border-radius: 10px; background: linear-gradient(135deg,#6366f1,#8b5cf6); border: none; color: white; font-weight: 600; font-size: 0.9rem; font-family: inherit; cursor: pointer; transition: opacity 0.2s; white-space: nowrap; }
.send-btn:hover:not(:disabled) { opacity: 0.85; }
.send-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.result-msg { display: flex; align-items: center; gap: 0.5rem; padding: 0.75rem 1.25rem; border-radius: 10px; font-size: 0.88rem; }
.result-msg.success { background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.25); color: #34d399; }
.result-msg.error   { background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.25); color: #ef4444; }
.result-msg.warn    { background: rgba(251,191,36,0.1); border: 1px solid rgba(251,191,36,0.25); color: #fbbf24; }

/* Add card */
.add-card { display: flex; align-items: center; justify-content: space-between; gap: 1rem; padding: 1.1rem 1.5rem; border-radius: 14px; flex-wrap: wrap; }
.add-form { display: flex; align-items: center; gap: 0.6rem; flex: 1; flex-wrap: wrap; min-width: 260px; }
.add-input { flex: 1; min-width: 140px; padding: 0.6rem 0.9rem; border-radius: 8px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); color: var(--text-main, #fff); font-size: 0.88rem; font-family: inherit; }
.add-input::placeholder { color: var(--text-muted); }
.add-input:focus { outline: none; border-color: #818cf8; }
.add-btn { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.6rem 1.1rem; border-radius: 8px; background: rgba(129,140,248,0.15); border: 1px solid rgba(129,140,248,0.3); color: #818cf8; font-weight: 600; font-size: 0.85rem; font-family: inherit; cursor: pointer; transition: all 0.2s; white-space: nowrap; }
.add-btn:hover:not(:disabled) { background: rgba(129,140,248,0.25); }
.add-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.ai-btn { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.65rem 1.2rem; border-radius: 10px; background: linear-gradient(135deg,#6366f1,#8b5cf6); border: none; color: white; font-weight: 600; font-size: 0.85rem; font-family: inherit; cursor: pointer; transition: opacity 0.2s; white-space: nowrap; }
.ai-btn:hover:not(:disabled) { opacity: 0.85; }
.ai-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* Section header */
.section-header { display: flex; align-items: center; justify-content: space-between; }
.section-header h2 { margin: 0; font-size: 1.1rem; font-weight: 600; display: flex; align-items: center; gap: 0.5rem; }
.count { font-size: 0.8rem; background: rgba(129,140,248,0.15); border: 1px solid rgba(129,140,248,0.25); color: #818cf8; padding: 0.1rem 0.55rem; border-radius: 50px; }
.seed-btn { display: inline-flex; align-items: center; gap: 0.4rem; padding: 0.5rem 1rem; border-radius: 8px; background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.12); color: var(--text-muted); font-size: 0.83rem; font-family: inherit; cursor: pointer; transition: all 0.2s; }
.seed-btn:hover:not(:disabled) { background: rgba(255,255,255,0.1); color: white; }
.seed-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* Table */
.state-box { display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.75rem; padding: 3rem; color: var(--text-muted); border-radius: 14px; }
.table-wrap { border-radius: 14px; overflow: hidden; }
.book-table { width: 100%; border-collapse: collapse; }
.book-table th { padding: 0.8rem 1.25rem; text-align: left; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); border-bottom: 1px solid rgba(255,255,255,0.08); }
.book-table td { padding: 0.8rem 1.25rem; font-size: 0.875rem; border-bottom: 1px solid rgba(255,255,255,0.05); }
.book-table tr:last-child td { border-bottom: none; }
.book-table tr:hover td { background: rgba(255,255,255,0.03); }
.book-title { font-weight: 500; }
.muted { color: var(--text-muted); }
.del-btn { background: none; border: none; color: var(--text-muted); cursor: pointer; font-size: 0.85rem; padding: 0.3rem 0.5rem; border-radius: 6px; transition: all 0.2s; }
.del-btn:hover { background: rgba(239,68,68,0.15); color: #ef4444; }

.glass-effect { background: rgba(255,255,255,0.05); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); }
</style>

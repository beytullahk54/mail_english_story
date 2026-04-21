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
          <i class="pi pi-users"></i>
          <span>Aboneler</span>
        </div>
        <div class="topbar-right">
          <NuxtLink to="/admin/blog" class="icon-btn" title="Blog Yönetimi">
            <i class="pi pi-pencil"></i>
          </NuxtLink>
          <button class="icon-btn danger" @click="handleLogout" title="Çıkış">
            <i class="pi pi-sign-out"></i>
          </button>
        </div>
      </header>

      <main class="admin-content">

        <!-- Özet kartlar -->
        <div class="stats-row">
          <div class="stat-card glass-effect">
            <div class="stat-icon"><i class="pi pi-users"></i></div>
            <div class="stat-info">
              <span class="stat-value">{{ total }}</span>
              <span class="stat-label">Toplam Abone</span>
            </div>
          </div>
          <div v-for="(count, level) in levelCounts" :key="level" class="stat-card glass-effect">
            <div class="stat-icon level-icon" :class="`level-${level.toLowerCase()}`">
              {{ level.toUpperCase() }}
            </div>
            <div class="stat-info">
              <span class="stat-value">{{ count }}</span>
              <span class="stat-label">{{ level.toUpperCase() }}</span>
            </div>
          </div>
        </div>

        <!-- Arama -->
        <div class="search-bar glass-effect">
          <i class="pi pi-search"></i>
          <input v-model="search" type="text" placeholder="E-posta ara..." />
        </div>

        <!-- Tablo -->
        <div class="table-wrap glass-effect">
          <div v-if="loading" class="state-box">
            <i class="pi pi-spinner pi-spin"></i> Yükleniyor...
          </div>
          <div v-else-if="filtered.length === 0" class="state-box">
            <i class="pi pi-inbox"></i> Abone bulunamadı.
          </div>
          <table v-else class="sub-table">
            <thead>
              <tr>
                <th>#</th>
                <th>E-posta</th>
                <th>Seviye</th>
                <th>Dil</th>
                <th>Kayıt Tarihi</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in filtered" :key="s.id">
                <td class="muted">{{ s.id }}</td>
                <td>{{ s.email }}</td>
                <td>
                  <span class="level-badge" :class="`level-${(s.level || '').toLowerCase()}`">
                    {{ s.level?.toUpperCase() || '—' }}
                  </span>
                </td>
                <td class="muted">{{ s.language || '—' }}</td>
                <td class="muted">{{ formatDate(s.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'

const config = useRuntimeConfig()
const router = useRouter()

const subscribers = ref([])
const total = ref(0)
const loading = ref(false)
const search = ref('')

const token = computed(() => {
  if (process.client) return localStorage.getItem('admin_token') || ''
  return ''
})

const filtered = computed(() => {
  if (!search.value) return subscribers.value
  return subscribers.value.filter(s =>
    s.email.toLowerCase().includes(search.value.toLowerCase())
  )
})

const levelCounts = computed(() => {
  const counts = {}
  for (const s of subscribers.value) {
    const lvl = s.level?.toUpperCase() || 'Diğer'
    counts[lvl] = (counts[lvl] || 0) + 1
  }
  return counts
})

const fetchSubscribers = async () => {
  loading.value = true
  try {
    const data = await $fetch(`${config.public.apiBase}/api/v1/subscribers`, {
      headers: { 'X-Api-Token': token.value },
    })
    subscribers.value = data.items
    total.value = data.total
  } catch (e) {
    if (e.status === 401) router.push('/admin/login')
  } finally {
    loading.value = false
  }
}

const formatDate = (d) => {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('tr-TR', {
    day: 'numeric', month: 'short', year: 'numeric'
  })
}

const handleLogout = () => {
  localStorage.removeItem('admin_token')
  router.push('/admin/login')
}

useHead({ title: 'Aboneler — Admin' })
onMounted(fetchSubscribers)
</script>

<style scoped>
.admin-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  background: var(--bg-main);
  position: relative;
  overflow: hidden;
}
.background-shapes { position: absolute; inset: 0; z-index: 0; overflow: hidden; }
.shape { position: absolute; border-radius: 50%; filter: blur(80px); opacity: 0.4; animation: float 12s infinite alternate ease-in-out; }
.shape-1 { width: 500px; height: 500px; background: #6366f1; top: -15%; left: -10%; }
.shape-2 { width: 400px; height: 400px; background: #c084fc; bottom: -15%; right: -10%; animation-delay: -6s; }
@keyframes float { 0% { transform: translate(0,0); } 100% { transform: translate(30px, 40px); } }

.admin-wrapper { position: relative; z-index: 10; width: 100%; max-width: 960px; padding: 1.5rem; display: flex; flex-direction: column; gap: 1.25rem; }

.topbar { display: flex; align-items: center; justify-content: space-between; padding: 0.85rem 1.25rem; border-radius: 14px; }
.topbar-left { display: flex; align-items: center; gap: 0.6rem; font-weight: 600; font-size: 1rem; }
.topbar-left i { color: #818cf8; }
.topbar-right { display: flex; gap: 0.5rem; }
.icon-btn { background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.12); color: var(--text-muted); border-radius: 8px; padding: 0.45rem 0.65rem; cursor: pointer; transition: all 0.2s; font-size: 0.9rem; }
.icon-btn:hover { background: rgba(255,255,255,0.14); color: white; }
.icon-btn.danger:hover { background: rgba(239,68,68,0.15); border-color: rgba(239,68,68,0.3); color: #f87171; }

/* Stats */
.stats-row { display: flex; gap: 1rem; flex-wrap: wrap; }
.stat-card { display: flex; align-items: center; gap: 1rem; padding: 1rem 1.5rem; border-radius: 14px; flex: 1; min-width: 130px; }
.stat-icon { font-size: 1.5rem; color: #818cf8; }
.level-icon { font-size: 0.85rem; font-weight: 700; padding: 0.3rem 0.6rem; border-radius: 50px; background: rgba(129,140,248,0.15); border: 1px solid rgba(129,140,248,0.3); color: #818cf8; }
.level-icon.level-a1 { background: rgba(52,211,153,0.15); border-color: rgba(52,211,153,0.3); color: #34d399; }
.level-icon.level-a2 { background: rgba(96,165,250,0.15); border-color: rgba(96,165,250,0.3); color: #60a5fa; }
.level-icon.level-b1 { background: rgba(251,191,36,0.15); border-color: rgba(251,191,36,0.3); color: #fbbf24; }
.level-icon.level-b2 { background: rgba(249,115,22,0.15); border-color: rgba(249,115,22,0.3); color: #f97316; }
.stat-value { font-size: 1.6rem; font-weight: 700; color: white; line-height: 1; }
.stat-label { font-size: 0.75rem; color: var(--text-muted); margin-top: 0.2rem; }
.stat-info { display: flex; flex-direction: column; }

/* Search */
.search-bar { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1.25rem; border-radius: 12px; }
.search-bar i { color: var(--text-muted); }
.search-bar input { background: none; border: none; outline: none; color: white; font-size: 0.95rem; width: 100%; }
.search-bar input::placeholder { color: var(--text-muted); }

/* Table */
.table-wrap { border-radius: 14px; overflow: hidden; }
.state-box { display: flex; align-items: center; justify-content: center; gap: 0.75rem; padding: 3rem; color: var(--text-muted); }
.sub-table { width: 100%; border-collapse: collapse; }
.sub-table th { padding: 0.85rem 1.25rem; text-align: left; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted); border-bottom: 1px solid rgba(255,255,255,0.08); }
.sub-table td { padding: 0.85rem 1.25rem; font-size: 0.875rem; border-bottom: 1px solid rgba(255,255,255,0.05); }
.sub-table tr:last-child td { border-bottom: none; }
.sub-table tr:hover td { background: rgba(255,255,255,0.03); }
.muted { color: var(--text-muted); }

.level-badge { padding: 0.2rem 0.6rem; border-radius: 50px; font-size: 0.72rem; font-weight: 600; background: rgba(129,140,248,0.15); border: 1px solid rgba(129,140,248,0.3); color: #818cf8; }
.level-badge.level-a1 { background: rgba(52,211,153,0.15); border-color: rgba(52,211,153,0.3); color: #34d399; }
.level-badge.level-a2 { background: rgba(96,165,250,0.15); border-color: rgba(96,165,250,0.3); color: #60a5fa; }
.level-badge.level-b1 { background: rgba(251,191,36,0.15); border-color: rgba(251,191,36,0.3); color: #fbbf24; }
.level-badge.level-b2 { background: rgba(249,115,22,0.15); border-color: rgba(249,115,22,0.3); color: #f97316; }
.level-badge.level-beginner { background: rgba(52,211,153,0.15); border-color: rgba(52,211,153,0.3); color: #34d399; }
.level-badge.level-intermediate { background: rgba(251,191,36,0.15); border-color: rgba(251,191,36,0.3); color: #fbbf24; }
.level-badge.level-advanced { background: rgba(239,68,68,0.15); border-color: rgba(239,68,68,0.3); color: #ef4444; }

.glass-effect { background: rgba(255,255,255,0.05); backdrop-filter: blur(12px); border: 1px solid rgba(255,255,255,0.1); }
</style>

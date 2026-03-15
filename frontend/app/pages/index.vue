<template>
  <div class="landing-container">
    <Toast />

    <div class="background-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
      <div class="shape shape-3"></div>
    </div>

    <main class="content-wrapper anim-fade-in">
      <div class="hero glass-effect anim-slide-up">
        <div class="lang-selector-container">
          <Select
            v-model="selectedLanguage"
            :options="displayLanguages"
            optionLabel="label"
            optionValue="value"
            class="lang-selector-premium"
          >
            <template #value="slotProps">
              <div class="flex items-center gap-2">
                <i class="pi pi-globe text-xs opacity-70"></i>
                <span>{{ slotProps.value }}</span>
              </div>
            </template>
          </Select>
        </div>

        <div class="icon-wrapper">
          <i class="pi pi-book book-icon"></i>
        </div>

        <h1 class="title" v-html="t('title')"></h1>

        <p class="subtitle">
          {{ t('subtitle') }}
        </p>

        <form class="subscribe-form delay-1 anim-slide-up" @submit.prevent="subscribe">
          <div class="input-group">
            <Select
              v-model="selectedLevel"
              :options="levels"
              :placeholder="t('levelPlaceholder')"
              class="level-select"
            />
            <div class="email-input-wrapper">
              <i class="pi pi-envelope input-icon" />
              <InputText
                v-model="email"
                type="email"
                :placeholder="t('emailPlaceholder')"
                class="email-input w-full"
                required
              />
            </div>
          </div>
          <Button
            type="submit"
            class="submit-btn"
            :loading="loading"
          >
            {{ t('button') }}
          </Button>
        </form>

        <div class="features delay-2 anim-slide-up">
          <div class="feature">
            <i class="pi pi-check-circle"></i>
            <span>{{ t('feature1') }}</span>
          </div>
          <div class="feature">
            <i class="pi pi-check-circle"></i>
            <span>{{ t('feature2') }}</span>
          </div>
          <div class="feature">
            <i class="pi pi-check-circle"></i>
            <span>{{ t('feature3') }}</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';

const email = ref('');
const selectedLanguage = ref('Türkçe');
const displayLanguages = ref([
    { label: 'Türkçe', value: 'Türkçe' },
    { label: 'English', value: 'English' },
    { label: 'Deutsch', value: 'Deutsch' },
    { label: 'Español', value: 'Español' },
    { label: 'Bahasa Melayu', value: 'Malay' },
    { label: 'Svenska', value: 'Swedish' },
    { label: 'Nederlands', value: 'Dutch' },
    { label: 'Dansk', value: 'Danish' }
]);
const selectedLevel = ref(null);
const levels = ref(['A1', 'A2', 'B1', 'B2']);
const loading = ref(false);
const toast = useToast();
const config = useRuntimeConfig();

const translations = {
  'Türkçe': {
    title: 'Her Gün Bir <span class="glow-text">İngilizce Hikaye</span>',
    subtitle: 'İngilizce okuma pratiğinizi eğlenceli hale getirin. Abone olun ve her gün özenle seçilmiş, seviyenize uygun İngilizce kısa hikayeler e-posta kutunuza gelsin.',
    button: 'Hemen Abone Ol',
    levelPlaceholder: 'Seviye',
    emailPlaceholder: 'E-posta adresiniz...',
    feature1: 'Tamamen Ücretsiz',
    feature2: 'Kelime Dağarcığı Geliştirme',
    feature3: 'Günlük Okuma Alışkanlığı',
    successSummary: 'Harika!',
    successDetail: (lvl) => `${lvl || 'Herhangi bir'} seviyesi için bültene başarıyla abone oldunuz.`,
    errorSummary: 'Hata',
    errorDetail: 'Abonelik işlemi sırasında bir hata oluştu.'
  },
  'English': {
    title: 'A New <span class="glow-text">English Story</span> Every Day',
    subtitle: 'Make your English reading practice fun. Subscribe and get carefully selected short stories suited to your level in your inbox every day.',
    button: 'Subscribe Now',
    levelPlaceholder: 'Level',
    emailPlaceholder: 'Your email address...',
    feature1: 'Completely Free',
    feature2: 'Vocabulary Building',
    feature3: 'Daily Reading Habit',
    successSummary: 'Awesome!',
    successDetail: (lvl) => `Successfully subscribed to the newsletter for ${lvl || 'any'} level.`,
    errorSummary: 'Error',
    errorDetail: 'An error occurred during subscription.'
  },
  'Deutsch': {
    title: 'Jeden Tag eine neue <span class="glow-text">deutsche Geschichte</span>',
    subtitle: 'Machen Sie Ihr Deutsch-Lesetraining zum Vergnügen. Abonnieren Sie und erhalten Sie jeden Tag sorgfältig ausgewählte Kurzgeschichten in Ihren Posteingang.',
    button: 'Jetzt Abonnieren',
    levelPlaceholder: 'Niveau',
    emailPlaceholder: 'Ihre E-Mail-Adresse...',
    feature1: 'Völlig Kostenlos',
    feature2: 'Wortschatzaufbau',
    feature3: 'Tägliche Lesegewohnheit',
    successSummary: 'Großartig!',
    successDetail: (lvl) => `Erfolgreich für den Newsletter auf ${lvl || 'beliebigem'} Niveau angemeldet.`,
    errorSummary: 'Fehler',
    errorDetail: 'Ein Fehler ist beim Abonnement aufgetreten.'
  },
  'Español': {
    title: 'Una nueva <span class="glow-text">historia en español</span> cada día',
    subtitle: 'Haz que tu práctica de lectura en español sea divertida. Suscríbete y recibe cada día historias cortas cuidadosamente seleccionadas en tu bandeja de entrada.',
    button: 'Suscríbete Ahora',
    levelPlaceholder: 'Nivel',
    emailPlaceholder: 'Tu correo electrónico...',
    feature1: 'Completamente Gratis',
    feature2: 'Construcción de Vocabulario',
    feature3: 'Hábito de Lectura Diario',
    successSummary: '¡Genial!',
    successDetail: (lvl) => `Suscrito con éxito al boletín para el nivel ${lvl || 'cualquiera'}.`,
    errorSummary: 'Error',
    errorDetail: 'Ocurrió un error durante la suscripción.'
  },
  'Malay': {
    title: 'Cerita <span class="glow-text">Bahasa Inggeris</span> Baru Setiap Hari',
    subtitle: 'Jadikan amalan membaca Bahasa Inggeris anda menyeronokkan. Langgan dan dapatkan cerita pendek yang dipilih khas sesuai dengan tahap anda setiap hari.',
    button: 'Langgan Sekarang',
    levelPlaceholder: 'Tahap',
    emailPlaceholder: 'Alamat e-mel anda...',
    feature1: 'Percuma Sepenuhnya',
    feature2: 'Membina Perbendaharaan Kata',
    feature3: 'Tabiat Membaca Harian',
    successSummary: 'Hebat!',
    successDetail: (lvl) => `Berjaya melanggan buletin untuk tahap ${lvl || 'sebarang'}.`,
    errorSummary: 'Ralat',
    errorDetail: 'Ralat berlaku semasa langganan.'
  },
  'Swedish': {
    title: 'En ny <span class="glow-text">engelsk berättelse</span> varje dag',
    subtitle: 'Gör din engelska lästräning rolig. Prenumerera och få noggrant utvalda noveller som passar din nivå i din inkorg varje dag.',
    button: 'Prenumerera nu',
    levelPlaceholder: 'Nivå',
    emailPlaceholder: 'Din e-postadress...',
    feature1: 'Helt gratis',
    feature2: 'Ordförrådsbyggande',
    feature3: 'Daglig läsvana',
    successSummary: 'Grymt!',
    successDetail: (lvl) => `Prenumerationen på nyhetsbrevet för nivån ${lvl || 'valfri'} lyckades.`,
    errorSummary: 'Fel',
    errorDetail: 'Ett fel uppstod vid prenumerationen.'
  },
  'Dutch': {
    title: 'Elke dag een nieuw <span class="glow-text">Engels verhaal</span>',
    subtitle: 'Maak je Engelse leesvaardigheid leuk. Abonneer je en ontvang elke dag zorgvuldig geselecteerde korte verhalen die passen bij jouw niveau in je inbox.',
    button: 'Nu abonneren',
    levelPlaceholder: 'Niveau',
    emailPlaceholder: 'Uw e-mailadres...',
    feature1: 'Helemaal gratis',
    feature2: 'Woordenschat opbouwen',
    feature3: 'Dagelijkse leesgewohnte',
    successSummary: 'Geweldig!',
    successDetail: (lvl) => `Succesvol geabonneerd op de nieuwsbrief voor niveau ${lvl || 'elk'}.`,
    errorSummary: 'Fout',
    errorDetail: 'Er is een fout opgetreden tijdens het abonneren.'
  },
  'Danish': {
    title: 'En ny <span class="glow-text">engelsk historie</span> hver dag',
    subtitle: 'Gør din engelske læsetræning sjov. Tilmeld dig og få omhyggeligt udvalgte noveller, der passer til dit niveau, i din indbakke hver dag.',
    button: 'Tilmeld dig nu',
    levelPlaceholder: 'Niveau',
    emailPlaceholder: 'Din e-mailadresse...',
    feature1: 'Helt gratis',
    feature2: 'Ordforrådsopbygning',
    feature3: 'Daglig læsevane',
    successSummary: 'Fantastisk!',
    successDetail: (lvl) => `Tilmelding til nyhedsbrevet for niveau ${lvl || 'vilkårligt'} lykkedes.`,
    errorSummary: 'Fejl',
    errorDetail: 'Der opstod en fejl under tilmeldingen.'
  }
};

const t = (key) => {
  return translations[selectedLanguage.value][key];
};

onMounted(() => {
  const browserLang = navigator.language || navigator.userLanguage;
  const shortLang = browserLang.split('-')[0].toLowerCase();

  const langMap = {
    'tr': 'Türkçe',
    'en': 'English',
    'de': 'Deutsch',
    'es': 'Español',
    'ms': 'Malay',
    'sv': 'Swedish',
    'nl': 'Dutch',
    'da': 'Danish'
  };

  if (langMap[shortLang]) {
    selectedLanguage.value = langMap[shortLang];
  } else {
    selectedLanguage.value = 'English';
  }
});

const subscribe = async () => {
  if (!email.value) return;

  loading.value = true;

  try {
    await $fetch(`${config.public.apiBase}/api/v1/subscribe`, {
      method: 'POST',
      body: {
        email: email.value,
        level: selectedLevel.value || 'None',
        language: selectedLanguage.value
      }
    });

    loading.value = false;
    toast.add({
      severity: 'success',
      summary: t('successSummary'),
      detail: t('successDetail')(selectedLevel.value),
      life: 4000
    });

    email.value = '';
    selectedLevel.value = null;
  } catch (error) {
    loading.value = false;
    toast.add({
      severity: 'error',
      summary: t('errorSummary'),
      detail: error.data?.error || t('errorDetail'),
      life: 4000
    });
  }
}
</script>

<style scoped>
.landing-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
  padding: 2rem;
}

.background-shapes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
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

.shape-1 {
  width: 400px;
  height: 400px;
  background: #6366f1;
  top: -10%;
  left: -5%;
}

.shape-2 {
  width: 500px;
  height: 500px;
  background: #c084fc;
  bottom: -20%;
  right: -10%;
  animation-delay: -5s;
}

.shape-3 {
  width: 300px;
  height: 300px;
  background: #3b82f6;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
  opacity: 0.3;
  animation-duration: 15s;
}

@keyframes float {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(30px, 50px) scale(1.1); }
}

.content-wrapper {
  position: relative;
  z-index: 10;
  width: 100%;
  max-width: 600px;
}

.hero {
  padding: 4.5rem 3rem 3rem 3rem;
  text-align: center;
  position: relative;
}

.lang-selector-container {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  z-index: 20;
}

:deep(.lang-selector-premium) {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  width: 130px;
  transition: all 0.3s ease;
}

:deep(.lang-selector-premium:hover) {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

:deep(.lang-selector-premium .p-select-label) {
  padding: 0.5rem 0.75rem;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.85);
  display: flex;
  align-items: center;
}

:deep(.lang-selector-premium .p-select-dropdown) {
  width: 2rem;
}

.icon-wrapper {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 24px;
  margin-bottom: 2rem;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  border: 1px solid rgba(255,255,255,0.2);
}

.book-icon {
  font-size: 2.5rem;
  color: #c084fc;
}

.title {
  font-size: 3rem;
  font-weight: 700;
  margin: 0 0 1rem 0;
  line-height: 1.2;
}

.subtitle {
  font-size: 1.1rem;
  color: var(--text-muted);
  line-height: 1.6;
  margin-bottom: 2.5rem;
}

.subscribe-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 3rem;
}

.input-group {
  width: 100%;
  display: flex;
  gap: 1rem;
}

.email-input-wrapper {
  flex: 1;
  position: relative;
  display: flex;
}

.input-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: rgba(255, 255, 255, 0.5);
  z-index: 10;
}

:deep(.level-select) {
  width: 140px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

:deep(.level-select:not(.p-disabled):hover) {
  border-color: rgba(255, 255, 255, 0.4);
}

:deep(.level-select .p-select-label) {
  color: white;
  padding: 1rem;
  font-size: 1.1rem;
}

:deep(.level-select .p-select-dropdown) {
  color: rgba(255, 255, 255, 0.7);
}

:deep(.email-input) {
  width: 100%;
  padding: 1rem 1rem 1rem 3rem !important;
  font-size: 1.1rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  transition: all 0.3s ease;
}

:deep(.email-input:focus) {
  background: rgba(255, 255, 255, 0.1);
  border-color: #818cf8;
  box-shadow: 0 0 0 2px rgba(129, 140, 248, 0.2);
  outline: none;
}

:deep(.submit-btn) {
  width: 100%;
  padding: 1rem;
  font-size: 1.1rem;
  font-weight: 600;
  border-radius: 12px;
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
  border: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

:deep(.submit-btn:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.4);
}

.features {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  flex-wrap: wrap;
  margin-bottom: 2rem;
}

.feature {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  color: var(--text-muted);
}

.feature i {
  color: #34d399;
}

.story-link {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 1.5rem;
}

.story-cta {
  display: inline-flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.75rem 1.5rem;
  border-radius: 50px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #c084fc;
  font-size: 0.95rem;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}

.story-cta:hover {
  background: rgba(192, 132, 252, 0.1);
  border-color: #c084fc;
  transform: translateY(-1px);
}

@media (max-width: 640px) {
  .lang-selector-container {
    position: static;
    display: flex;
    justify-content: center;
    margin-bottom: 2rem;
  }

  :deep(.lang-selector-premium) {
    width: 100%;
    max-width: 200px;
  }

  .input-group {
    flex-direction: column;
  }

  :deep(.level-select) {
    width: 100%;
  }

  .hero {
    padding: 2rem 1.5rem;
  }

  .title {
    font-size: 2.2rem;
  }

  .features {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>

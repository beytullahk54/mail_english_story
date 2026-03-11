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
        
        <div class="icon-wrapper">
          <i class="pi pi-book book-icon"></i>
        </div>

        <h1 class="title">
          Her Gün Bir <span class="glow-text">İngilizce Hikaye</span>
        </h1>
        
        <p class="subtitle">
          İngilizce okuma pratiğinizi eğlenceli hale getirin. Abone olun ve her gün özenle seçilmiş, seviyenize uygun İngilizce kısa hikayeler e-posta kutunuza gelsin.
        </p>

        <form class="subscribe-form delay-1 anim-slide-up" @submit.prevent="subscribe">
          <div class="input-group">
            <Select 
              v-model="selectedLevel" 
              :options="levels" 
              placeholder="Seviye" 
              class="level-select"
            />
            <div class="email-input-wrapper">
              <i class="pi pi-envelope input-icon" />
              <InputText 
                v-model="email" 
                type="email" 
                placeholder="E-posta adresiniz..." 
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
            Hemen Abone Ol
          </Button>
        </form>

        <div class="features delay-2 anim-slide-up">
          <div class="feature">
            <i class="pi pi-check-circle"></i>
            <span>Tamamen Ücretsiz</span>
          </div>
          <div class="feature">
            <i class="pi pi-check-circle"></i>
            <span>Kelime Dağarcığı Geliştirme</span>
          </div>
          <div class="feature">
            <i class="pi pi-check-circle"></i>
            <span>Günlük Okuma Alışkanlığı</span>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useToast } from 'primevue/usetoast';

const email = ref('');
const selectedLevel = ref(null);
const levels = ref(['A1', 'A2', 'B1', 'B2']);
const loading = ref(false);
const toast = useToast();

const subscribe = async () => {
  if (!email.value) return;

  loading.value = true;
  
  try {
    const response = await $fetch('http://localhost:8000/api/v1/subscribe', {
      method: 'POST',
      body: {
        email: email.value,
        level: selectedLevel.value || 'None'
      }
    });

    loading.value = false;
    toast.add({ 
      severity: 'success', 
      summary: 'Harika!', 
      detail: `${selectedLevel.value || 'Herhangi bir'} seviyesi için bültene başarıyla abone oldunuz.`, 
      life: 4000 
    });
    
    email.value = '';
    selectedLevel.value = null;
  } catch (error) {
    loading.value = false;
    toast.add({ 
      severity: 'error', 
      summary: 'Hata', 
      detail: error.data?.error || 'Abonelik işlemi sırasında bir hata oluştu.', 
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
  padding: 3rem;
  text-align: center;
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

@media (max-width: 640px) {
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

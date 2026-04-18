<template>
  <div class="login-container">
    <div class="background-shapes">
      <div class="shape shape-1"></div>
      <div class="shape shape-2"></div>
    </div>

    <div class="login-card glass-effect anim-slide-up">
      <div class="login-header">
        <i class="pi pi-lock"></i>
        <h1>Admin Panel</h1>
        <p>English Story Blog Yönetimi</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="field">
          <label>Şifre</label>
          <Password
            v-model="password"
            :feedback="false"
            toggleMask
            placeholder="Şifreyi girin"
            class="w-full"
            inputClass="w-full"
          />
        </div>

        <Message v-if="error" severity="error" :closable="false">{{ error }}</Message>

        <Button
          type="submit"
          label="Giriş Yap"
          icon="pi pi-sign-in"
          :loading="loading"
          class="login-btn w-full"
        />
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

definePageMeta({ layout: false });

const { login } = useAdmin();

const password = ref('');
const loading = ref(false);
const error = ref('');

const handleLogin = async () => {
  if (!password.value) return;
  loading.value = true;
  error.value = '';
  try {
    await login(password.value);
    await navigateTo('/admin/blog');
  } catch {
    error.value = 'Hatalı şifre.';
  } finally {
    loading.value = false;
  }
};

useHead({ title: 'Admin Giriş — English Story' });
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
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

@keyframes float {
  0% { transform: translate(0, 0) scale(1); }
  100% { transform: translate(30px, 50px) scale(1.1); }
}

.login-card {
  position: relative; z-index: 10;
  width: 100%; max-width: 400px;
  padding: 2.5rem;
  display: flex; flex-direction: column; gap: 2rem;
}

.login-header {
  text-align: center;
  display: flex; flex-direction: column; align-items: center; gap: 0.75rem;
}
.login-header i { font-size: 2rem; color: #818cf8; }
.login-header h1 { margin: 0; font-size: 1.5rem; font-weight: 700; }
.login-header p { margin: 0; color: var(--text-muted); font-size: 0.9rem; }

.login-form { display: flex; flex-direction: column; gap: 1.25rem; }

.field { display: flex; flex-direction: column; gap: 0.5rem; }
.field label { font-size: 0.85rem; color: var(--text-muted); }

:deep(.p-password) { width: 100%; }
:deep(.p-password-input) {
  width: 100%;
  background: rgba(255,255,255,0.07);
  border: 1px solid rgba(255,255,255,0.15);
  color: var(--text-main);
  border-radius: 10px;
  padding: 0.75rem 1rem;
}

.login-btn {
  background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
  border: none !important;
  border-radius: 10px !important;
  padding: 0.85rem !important;
  font-weight: 600 !important;
}
</style>

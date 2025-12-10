<script setup lang="ts">
import { ref, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRoute } from 'vue-router';

const authStore = useAuthStore();
const route = useRoute();

const email = ref('');
const emailSent = ref(false);
const isSubmitting = ref(false);

const isValidEmail = computed(() => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email.value);
});

const canSubmit = computed(() => {
  return isValidEmail.value && !isSubmitting.value && !emailSent.value;
});

async function handleSubmit() {
  if (!canSubmit.value) return;

  isSubmitting.value = true;
  authStore.clearError();

  try {
    // Get redirect URL from query params or default to /auth/callback
    const redirectTo = (route.query.redirect as string) || '/auth/callback';
    const fullRedirectUrl = `${window.location.origin}${redirectTo}`;

    await authStore.sendMagicLink(email.value, fullRedirectUrl);
    emailSent.value = true;
  } catch (error) {
    console.error('Failed to send magic link:', error);
  } finally {
    isSubmitting.value = false;
  }
}

function resetForm() {
  email.value = '';
  emailSent.value = false;
  authStore.clearError();
}
</script>

<template>
  <div class="w-full max-w-md mx-auto">
    <!-- Success State -->
    <div v-if="emailSent" class="bg-white rounded-lg shadow-lg p-8">
      <div class="text-center mb-6">
        <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
          <svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <h3 class="text-2xl font-bold text-gray-900 mb-2">Check your email</h3>
        <p class="text-gray-600 mb-6">
          We've sent a magic link to <span class="font-semibold">{{ email }}</span>
        </p>
        <p class="text-sm text-gray-500 mb-8">
          Click the link in the email to sign in. The link will expire in 1 hour.
        </p>
      </div>

      <button
        @click="resetForm"
        type="button"
        class="w-full px-4 py-3 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
      >
        Send to a different email
      </button>
    </div>

    <!-- Form State -->
    <div v-else class="bg-white rounded-lg shadow-lg p-8">
      <div class="text-center mb-8">
        <h2 class="text-3xl font-bold text-gray-900 mb-2">Welcome to BNA Market</h2>
        <p class="text-gray-600">Sign in with your email address</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-6">
        <!-- Email Input -->
        <div>
          <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
            Email address
          </label>
          <input
            id="email"
            v-model="email"
            type="email"
            autocomplete="email"
            required
            :disabled="isSubmitting"
            placeholder="you@example.com"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors disabled:bg-gray-100 disabled:cursor-not-allowed"
            :class="{
              'border-red-300 focus:ring-red-500': authStore.error,
              'border-gray-300': !authStore.error
            }"
          />
          <p v-if="email && !isValidEmail" class="mt-2 text-sm text-red-600">
            Please enter a valid email address
          </p>
        </div>

        <!-- Error Message -->
        <div
          v-if="authStore.error"
          class="p-4 bg-red-50 border border-red-200 rounded-lg"
        >
          <div class="flex">
            <div class="flex-shrink-0">
              <svg class="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </div>
            <div class="ml-3">
              <p class="text-sm text-red-800">{{ authStore.error }}</p>
            </div>
          </div>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="!canSubmit"
          class="w-full px-4 py-3 text-white font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          :class="{
            'bg-blue-600 hover:bg-blue-700': canSubmit,
            'bg-gray-300 cursor-not-allowed': !canSubmit
          }"
        >
          <span v-if="isSubmitting" class="flex items-center justify-center">
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Sending magic link...
          </span>
          <span v-else>
            Send magic link
          </span>
        </button>
      </form>

      <!-- Info Text -->
      <div class="mt-6 text-center">
        <p class="text-xs text-gray-500">
          No password required. We'll send you a secure link to sign in.
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Additional custom styles if needed */
</style>

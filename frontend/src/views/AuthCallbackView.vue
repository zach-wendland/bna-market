<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const router = useRouter();
const route = useRoute();
const authStore = useAuthStore();

const status = ref<'verifying' | 'success' | 'error'>('verifying');
const errorMessage = ref('');

onMounted(async () => {
  // Extract token and type from URL hash or query params
  // Supabase sends tokens in URL hash like: #access_token=...&token_type=bearer&type=magiclink
  const hashParams = new URLSearchParams(window.location.hash.substring(1));
  const queryParams = route.query;

  // Try to get token from hash first (Supabase default), then query params
  const token = hashParams.get('access_token') || queryParams.token as string;
  const type = hashParams.get('type') || queryParams.type as string || 'magiclink';

  if (!token) {
    status.value = 'error';
    errorMessage.value = 'No authentication token found. Please try logging in again.';
    return;
  }

  try {
    // Verify the magic link token
    await authStore.verifyMagicLink(token, type);
    status.value = 'success';

    // Get redirect path from query params or default to dashboard
    const redirectPath = (queryParams.redirect as string) || '/';

    // Redirect after a brief delay to show success message
    setTimeout(() => {
      router.push(redirectPath);
    }, 1500);
  } catch (error: any) {
    status.value = 'error';
    errorMessage.value = error.response?.data?.error || 'Failed to verify magic link. The link may have expired or is invalid.';
    console.error('Magic link verification failed:', error);
  }
});

function goToLogin() {
  router.push('/login');
}

function goToDashboard() {
  router.push('/');
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <div class="bg-white rounded-lg shadow-lg p-8">
        <!-- Verifying State -->
        <div v-if="status === 'verifying'" class="text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 mb-4">
            <svg class="animate-spin h-12 w-12 text-blue-600" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
          </div>
          <h3 class="text-2xl font-bold text-gray-900 mb-2">Verifying your login</h3>
          <p class="text-gray-600">Please wait while we verify your magic link...</p>
        </div>

        <!-- Success State -->
        <div v-else-if="status === 'success'" class="text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-green-100 mb-4">
            <svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h3 class="text-2xl font-bold text-gray-900 mb-2">Successfully signed in!</h3>
          <p class="text-gray-600 mb-6">Redirecting you to your dashboard...</p>

          <button
            @click="goToDashboard"
            type="button"
            class="w-full px-4 py-3 text-white font-medium bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            Go to Dashboard
          </button>
        </div>

        <!-- Error State -->
        <div v-else class="text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100 mb-4">
            <svg class="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h3 class="text-2xl font-bold text-gray-900 mb-2">Authentication failed</h3>
          <p class="text-gray-600 mb-6">{{ errorMessage }}</p>

          <div class="space-y-3">
            <button
              @click="goToLogin"
              type="button"
              class="w-full px-4 py-3 text-white font-medium bg-blue-600 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              Try logging in again
            </button>

            <button
              @click="goToDashboard"
              type="button"
              class="w-full px-4 py-3 text-gray-700 font-medium bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
            >
              Go to Dashboard
            </button>
          </div>
        </div>
      </div>

      <!-- Help Text -->
      <div class="mt-6 text-center">
        <p class="text-sm text-gray-600">
          Having trouble?
          <a href="#" class="font-medium text-blue-600 hover:text-blue-500">Contact support</a>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Additional custom styles if needed */
</style>

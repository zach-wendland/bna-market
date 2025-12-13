<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';

const authStore = useAuthStore();
const router = useRouter();
const isSigningIn = ref(false);
const signInError = ref<string | null>(null);

// If already authenticated, redirect to dashboard
onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push('/');
  }
});

async function handleGoogleSignIn() {
  isSigningIn.value = true;
  signInError.value = null;

  try {
    await authStore.signInWithGoogle();
    // Supabase will redirect to Google, so we won't reach here normally
  } catch (e: any) {
    signInError.value = e.message || 'Failed to sign in with Google';
    isSigningIn.value = false;
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-cottage-cream to-cottage-sand flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <!-- Logo/Brand -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-cyber-navy mb-2">
          BNA Market
        </h1>
        <p class="text-lg text-cottage-forest">
          Nashville Real Estate Analytics
        </p>
      </div>

      <!-- Sign In Card -->
      <div class="bg-white py-8 px-6 shadow-lg rounded-xl border border-cottage-sand">
        <div class="text-center mb-6">
          <h2 class="text-xl font-semibold text-cyber-navy">Sign In</h2>
          <p class="text-sm text-cottage-forest mt-1">Access your saved properties and searches</p>
        </div>

        <!-- Error Message -->
        <div v-if="signInError" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-600">{{ signInError }}</p>
        </div>

        <!-- Google Sign-In Button -->
        <button
          @click="handleGoogleSignIn"
          :disabled="isSigningIn"
          class="w-full flex items-center justify-center gap-3 px-4 py-3 bg-white border border-cottage-wheat rounded-lg shadow-sm hover:shadow-md hover:border-primary-300 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <svg v-if="!isSigningIn" class="w-5 h-5" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          <div v-else class="w-5 h-5 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
          <span class="text-sm font-medium text-gray-700">
            {{ isSigningIn ? 'Signing in...' : 'Continue with Google' }}
          </span>
        </button>

        <!-- Divider -->
        <div class="relative my-6">
          <div class="absolute inset-0 flex items-center">
            <div class="w-full border-t border-cottage-sand"></div>
          </div>
          <div class="relative flex justify-center text-xs">
            <span class="px-2 bg-white text-cottage-wheat">or continue without account</span>
          </div>
        </div>

        <!-- Guest Access Button -->
        <button
          @click="router.push('/')"
          class="w-full px-4 py-2 text-sm text-cottage-forest hover:text-cyber-navy transition-colors"
        >
          Browse as Guest
        </button>
      </div>

      <!-- Footer Links -->
      <div class="mt-8 text-center">
        <p class="text-sm text-gray-600">
          By signing in, you agree to our
          <a href="#" class="font-medium text-blue-600 hover:text-blue-500">Terms of Service</a>
          and
          <a href="#" class="font-medium text-blue-600 hover:text-blue-500">Privacy Policy</a>
        </p>
      </div>
    </div>

    <!-- Features Section -->
    <div class="mt-12 sm:mx-auto sm:w-full sm:max-w-4xl">
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 px-4">
        <div class="text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 mb-4">
            <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">Save Properties</h3>
          <p class="text-sm text-gray-600">
            Create custom lists to organize properties you're interested in
          </p>
        </div>

        <div class="text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 mb-4">
            <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">Save Searches</h3>
          <p class="text-sm text-gray-600">
            Save your search filters for quick access to properties that match your criteria
          </p>
        </div>

        <div class="text-center">
          <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-blue-100 mb-4">
            <svg class="h-6 w-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-900 mb-2">Market Analytics</h3>
          <p class="text-sm text-gray-600">
            Access comprehensive market data and economic indicators for Nashville
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Additional custom styles if needed */
</style>

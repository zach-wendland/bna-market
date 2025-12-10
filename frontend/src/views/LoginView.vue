<script setup lang="ts">
import { onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useRouter } from 'vue-router';
import MagicLinkForm from '@/components/auth/MagicLinkForm.vue';

const authStore = useAuthStore();
const router = useRouter();

// If already authenticated, redirect to dashboard
onMounted(() => {
  if (authStore.isAuthenticated) {
    router.push('/');
  }
});
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <!-- Logo/Brand -->
      <div class="text-center mb-8">
        <h1 class="text-4xl font-bold text-gray-900 mb-2">
          BNA Market
        </h1>
        <p class="text-lg text-gray-600">
          Nashville Real Estate Analytics
        </p>
      </div>

      <!-- Magic Link Form -->
      <MagicLinkForm />

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

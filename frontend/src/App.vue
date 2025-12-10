<script setup lang="ts">
import { onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import AppHeader from '@/components/layout/AppHeader.vue';

const authStore = useAuthStore();

onMounted(async () => {
  // Load user session on app start
  await authStore.loadSession();
});
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header (shown on all pages) -->
    <AppHeader />

    <!-- Router View (main content) -->
    <router-view />

    <!-- Footer -->
    <footer class="bg-white border-t border-gray-200 mt-12">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <p class="text-center text-sm text-gray-500">
          BNA Market Analytics &copy; {{ new Date().getFullYear() }} &mdash; Nashville Real Estate Data
        </p>
      </div>
    </footer>
  </div>
</template>

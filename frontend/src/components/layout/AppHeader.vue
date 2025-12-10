<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useDashboardStore } from '@/stores/dashboard';
import { useAuthStore } from '@/stores/auth';

const store = useDashboardStore();
const authStore = useAuthStore();
const router = useRouter();

const showUserMenu = ref(false);

async function handleLogout() {
  await authStore.logout();
  showUserMenu.value = false;
  router.push('/login');
}

function goToLogin() {
  router.push('/login');
}

function goToProfile() {
  router.push('/profile');
  showUserMenu.value = false;
}

function goToLists() {
  router.push('/lists');
  showUserMenu.value = false;
}

function goToDashboard() {
  router.push('/');
}
</script>

<template>
  <header class="bg-gradient-to-r from-primary-600 via-primary-700 to-accent-700 text-white shadow-lg">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div class="cursor-pointer" @click="goToDashboard">
          <h1 class="text-2xl sm:text-3xl font-bold tracking-tight">
            Nashville Real Estate Market
          </h1>
          <p class="mt-1 text-primary-100 text-sm sm:text-base">
            Comprehensive analytics for the BNA metro area
          </p>
        </div>

        <div class="mt-4 sm:mt-0 flex items-center gap-4">
          <!-- Data Freshness Indicator -->
          <div v-if="store.relativeFreshness" class="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full text-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke-width="2" />
              <polyline points="12 6 12 12 16 14" stroke-width="2" />
            </svg>
            <span>Updated {{ store.relativeFreshness }}</span>
          </div>

          <!-- Auth Section -->
          <div>
            <!-- Sign In Button (when not authenticated) -->
            <button
              v-if="!authStore.isAuthenticated"
              @click="goToLogin"
              class="inline-flex items-center gap-2 bg-white text-primary-700 px-4 py-2 rounded-lg font-medium hover:bg-primary-50 transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
              </svg>
              Sign In
            </button>

            <!-- User Menu (when authenticated) -->
            <div v-else class="relative">
              <button
                @click="showUserMenu = !showUserMenu"
                class="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-lg font-medium hover:bg-white/20 transition-colors"
              >
                <div class="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center">
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
                <span class="hidden sm:inline">{{ authStore.user?.email }}</span>
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <!-- Dropdown Menu -->
              <div
                v-if="showUserMenu"
                @click.self="showUserMenu = false"
                class="fixed inset-0 z-40"
              >
                <div class="absolute right-4 top-20 sm:top-24 w-56 bg-white rounded-lg shadow-xl border border-gray-200 py-2 z-50">
                  <!-- User Info -->
                  <div class="px-4 py-3 border-b border-gray-200">
                    <p class="text-sm font-medium text-gray-900">{{ authStore.user?.email }}</p>
                    <p class="text-xs text-gray-500 mt-1">{{ authStore.user?.role || 'User' }}</p>
                  </div>

                  <!-- Menu Items -->
                  <nav class="py-2">
                    <button
                      @click="goToDashboard"
                      class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                      </svg>
                      Dashboard
                    </button>

                    <button
                      @click="goToLists"
                      class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                      </svg>
                      My Lists
                    </button>

                    <button
                      @click="goToProfile"
                      class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                      Profile
                    </button>
                  </nav>

                  <!-- Logout -->
                  <div class="border-t border-gray-200 pt-2">
                    <button
                      @click="handleLogout"
                      class="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 flex items-center gap-2"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      Sign Out
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

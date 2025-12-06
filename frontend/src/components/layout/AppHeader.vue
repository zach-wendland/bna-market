<script setup lang="ts">
import { useDashboardStore } from '@/stores/dashboard';

const store = useDashboardStore();
</script>

<template>
  <header class="bg-gradient-to-r from-primary-600 via-primary-700 to-accent-700 text-white shadow-lg">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 class="text-2xl sm:text-3xl font-bold tracking-tight">
            Nashville Real Estate Market
          </h1>
          <p class="mt-1 text-primary-100 text-sm sm:text-base">
            Comprehensive analytics for the BNA metro area
          </p>
        </div>

        <!-- Data Freshness Indicator -->
        <div v-if="store.relativeFreshness" class="mt-4 sm:mt-0">
          <div class="inline-flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-full text-sm">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke-width="2" />
              <polyline points="12 6 12 12 16 14" stroke-width="2" />
            </svg>
            <span>Updated {{ store.relativeFreshness }}</span>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

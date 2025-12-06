<script setup lang="ts">
import { onMounted } from 'vue';
import { useDashboardStore } from '@/stores/dashboard';
import AppHeader from '@/components/layout/AppHeader.vue';
import KPICards from '@/components/dashboard/KPICards.vue';
import ChartSection from '@/components/dashboard/ChartSection.vue';
import PropertyFilters from '@/components/properties/PropertyFilters.vue';
import FilterChips from '@/components/properties/FilterChips.vue';
import PropertyTable from '@/components/properties/PropertyTable.vue';
import PropertyCards from '@/components/properties/PropertyCards.vue';
import PropertyMap from '@/components/properties/PropertyMap.vue';
import ViewToggle from '@/components/ui/ViewToggle.vue';
import Pagination from '@/components/ui/Pagination.vue';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';

const store = useDashboardStore();

onMounted(async () => {
  await store.loadDashboard();
});
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <AppHeader />

    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Loading State -->
      <div v-if="store.isLoading && !store.propertyKPIs" class="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>

      <!-- Error State -->
      <div v-else-if="store.error" class="card p-8 text-center">
        <div class="text-red-500 mb-4">
          <svg class="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-2">Failed to Load Dashboard</h3>
        <p class="text-gray-600 mb-4">{{ store.error }}</p>
        <button @click="store.loadDashboard()" class="btn btn-primary">
          Try Again
        </button>
      </div>

      <!-- Dashboard Content -->
      <template v-else>
        <!-- KPI Cards -->
        <section class="mb-8">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Market Overview</h2>
          <KPICards />
        </section>

        <!-- Charts Section -->
        <section class="mb-8">
          <h2 class="text-lg font-semibold text-gray-900 mb-4">Market Trends</h2>
          <ChartSection />
        </section>

        <!-- Properties Section -->
        <section>
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4">
            <h2 class="text-lg font-semibold text-gray-900 mb-2 sm:mb-0">Property Listings</h2>
            <ViewToggle />
          </div>

          <!-- Filters -->
          <PropertyFilters class="mb-4" />

          <!-- Active Filter Chips -->
          <FilterChips v-if="store.hasActiveFilters" class="mb-4" />

          <!-- Results Count -->
          <div v-if="store.pagination" class="mb-4 text-sm text-gray-600">
            <span class="font-medium">{{ store.pagination.totalCount.toLocaleString() }}</span>
            {{ store.filters.propertyType === 'rental' ? 'rental' : 'for-sale' }} properties found
          </div>

          <!-- Property Views -->
          <div class="relative">
            <LoadingSpinner v-if="store.isLoading" class="absolute top-4 right-4 z-10" />

            <PropertyTable v-if="store.viewMode === 'table'" />
            <PropertyCards v-else-if="store.viewMode === 'cards'" />
            <PropertyMap v-else-if="store.viewMode === 'map'" />
          </div>

          <!-- Pagination -->
          <Pagination v-if="store.pagination && store.pagination.totalPages > 1" class="mt-6" />
        </section>
      </template>
    </main>

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

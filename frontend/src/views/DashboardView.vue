<script setup lang="ts">
import { onMounted, defineAsyncComponent } from 'vue';
import { useDashboardStore } from '@/stores/dashboard';
import KPICards from '@/components/dashboard/KPICards.vue';
import PropertyFilters from '@/components/properties/PropertyFilters.vue';
import FilterChips from '@/components/properties/FilterChips.vue';
import PropertyTable from '@/components/properties/PropertyTable.vue';
import PropertyCards from '@/components/properties/PropertyCards.vue';
import ViewToggle from '@/components/ui/ViewToggle.vue';
import Pagination from '@/components/ui/Pagination.vue';
import LoadingSpinner from '@/components/ui/LoadingSpinner.vue';

// Lazy load heavy components to reduce initial bundle size
// ApexCharts (~500KB) and Leaflet (~200KB) are loaded on demand
const ChartSection = defineAsyncComponent({
  loader: () => import('@/components/dashboard/ChartSection.vue'),
  loadingComponent: LoadingSpinner,
  delay: 200,
});

const PropertyMap = defineAsyncComponent({
  loader: () => import('@/components/properties/PropertyMap.vue'),
  loadingComponent: LoadingSpinner,
  delay: 200,
});

const PropertyCarousel = defineAsyncComponent({
  loader: () => import('@/components/properties/PropertyCarousel.vue'),
  loadingComponent: LoadingSpinner,
  delay: 200,
});

const store = useDashboardStore();

onMounted(async () => {
  await store.loadDashboard();
});
</script>

<template>
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <!-- Loading State -->
    <div v-if="store.isLoading && !store.propertyKPIs" class="flex items-center justify-center min-h-[400px]">
      <div class="spinner-cyber w-8 h-8"></div>
    </div>

    <!-- Error State -->
    <div v-else-if="store.error" class="card p-6 text-center border-cyber-magenta/30">
      <div class="text-cyber-magenta mb-3">
        <svg class="w-10 h-10 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      </div>
      <h3 class="text-base font-medium text-cyber-navy mb-2">Failed to Load Dashboard</h3>
      <p class="text-cottage-forest text-sm mb-4">{{ store.error }}</p>
      <button @click="store.loadDashboard()" class="btn btn-cyber">
        Try Again
      </button>
    </div>

    <!-- Dashboard Content -->
    <template v-else>
      <!-- KPI Cards Section -->
      <section class="mb-6">
        <h2 class="section-heading flex items-center gap-2 mb-3">
          <span class="w-1 h-5 bg-gradient-to-b from-cyber-magenta to-primary-500 rounded-full"></span>
          Market Overview
        </h2>
        <KPICards />
      </section>

      <!-- Charts Section - Compact -->
      <section class="mb-6">
        <ChartSection />
      </section>

      <!-- Properties Section -->
      <section>
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-3">
          <h2 class="section-heading flex items-center gap-2 mb-2 sm:mb-0">
            <span class="w-1 h-5 bg-gradient-to-b from-cottage-sage to-cottage-forest rounded-full"></span>
            Property Listings
          </h2>
          <ViewToggle />
        </div>

        <!-- Filters -->
        <PropertyFilters class="mb-3" />

        <!-- Active Filter Chips -->
        <FilterChips v-if="store.hasActiveFilters" class="mb-3" />

        <!-- Results Count -->
        <div v-if="store.pagination" class="mb-3 text-sm text-cottage-forest">
          <span class="font-semibold text-cyber-navy">{{ store.pagination.totalCount.toLocaleString() }}</span>
          {{ store.filters.propertyType === 'rental' ? 'rental' : 'for-sale' }} properties found
        </div>

        <!-- Property Views -->
        <div class="relative">
          <div v-if="store.isLoading" class="absolute top-4 right-4 z-10">
            <div class="spinner-cyber"></div>
          </div>

          <PropertyCarousel v-if="store.viewMode === 'carousel'" />
          <PropertyCards v-else-if="store.viewMode === 'cards'" />
          <PropertyMap v-else-if="store.viewMode === 'map'" />
          <PropertyTable v-else-if="store.viewMode === 'table'" />
        </div>

        <!-- Pagination -->
        <Pagination v-if="store.pagination && store.pagination.totalPages > 1" class="mt-4" />
      </section>
    </template>
  </main>
</template>

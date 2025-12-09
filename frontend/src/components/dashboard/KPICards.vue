<script setup lang="ts">
import { computed } from 'vue';
import { useDashboardStore } from '@/stores/dashboard';
import { useFormatters } from '@/composables/useFormatters';

const store = useDashboardStore();
const { formatPrice, formatNumber } = useFormatters();

interface KPIItem {
  label: string;
  value: string;
  icon: string;
  color: string;
}

const propertyKpis = computed<KPIItem[]>(() => {
  if (!store.propertyKPIs) return [];

  return [
    {
      label: 'Total Rentals',
      value: formatNumber(store.propertyKPIs.totalRentalListings),
      icon: 'home',
      color: 'from-blue-500 to-blue-600'
    },
    {
      label: 'Avg Rental Price',
      value: store.propertyKPIs.avgRentalPrice ? formatPrice(store.propertyKPIs.avgRentalPrice) : 'N/A',
      icon: 'dollar',
      color: 'from-green-500 to-green-600'
    },
    {
      label: 'For-Sale Listings',
      value: formatNumber(store.propertyKPIs.totalForSaleListings),
      icon: 'building',
      color: 'from-purple-500 to-purple-600'
    },
    {
      label: 'Avg Sale Price',
      value: store.propertyKPIs.avgSalePrice ? formatPrice(store.propertyKPIs.avgSalePrice) : 'N/A',
      icon: 'chart',
      color: 'from-orange-500 to-orange-600'
    }
  ];
});

const fredKpis = computed<KPIItem[]>(() => {
  if (!store.fredKPIs) return [];

  const items: KPIItem[] = [];

  if (store.fredKPIs.medianPrice) {
    items.push({
      label: 'Median List Price',
      value: formatPrice(store.fredKPIs.medianPrice),
      icon: 'tag',
      color: 'from-indigo-500 to-indigo-600'
    });
  }

  if (store.fredKPIs.activeListings) {
    items.push({
      label: 'Active Listings',
      value: formatNumber(store.fredKPIs.activeListings),
      icon: 'list',
      color: 'from-cyan-500 to-cyan-600'
    });
  }

  if (store.fredKPIs.medianDaysOnMarket) {
    items.push({
      label: 'Median DOM',
      value: `${Math.round(store.fredKPIs.medianDaysOnMarket)} days`,
      icon: 'clock',
      color: 'from-rose-500 to-rose-600'
    });
  }

  if (store.fredKPIs.perCapitaIncome) {
    items.push({
      label: 'Per Capita Income',
      value: formatPrice(store.fredKPIs.perCapitaIncome),
      icon: 'user',
      color: 'from-emerald-500 to-emerald-600'
    });
  }

  return items;
});
</script>

<template>
  <div class="space-y-6">
    <!-- Property KPIs -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div
        v-for="kpi in propertyKpis"
        :key="kpi.label"
        class="card p-5 hover:shadow-md transition-shadow"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-500">{{ kpi.label }}</p>
            <p class="mt-1 text-2xl font-bold text-gray-900">{{ kpi.value }}</p>
          </div>
          <div :class="['w-12 h-12 rounded-xl bg-gradient-to-br flex items-center justify-center', kpi.color]">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="kpi.icon === 'home'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              <path v-else-if="kpi.icon === 'dollar'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              <path v-else-if="kpi.icon === 'building'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              <path v-else-if="kpi.icon === 'chart'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- FRED Economic KPIs -->
    <div v-if="fredKpis.length > 0" class="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <div
        v-for="kpi in fredKpis"
        :key="kpi.label"
        class="card p-5 hover:shadow-md transition-shadow"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-500">{{ kpi.label }}</p>
            <p class="mt-1 text-2xl font-bold text-gray-900">{{ kpi.value }}</p>
          </div>
          <div :class="['w-12 h-12 rounded-xl bg-gradient-to-br flex items-center justify-center', kpi.color]">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

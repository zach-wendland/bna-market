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
  glowClass?: string;
}

const propertyKpis = computed<KPIItem[]>(() => {
  if (!store.propertyKPIs) return [];

  return [
    {
      label: 'Total Rentals',
      value: formatNumber(store.propertyKPIs.totalRentalListings),
      icon: 'home',
      color: 'from-cyber-cyan to-cyber-cyan/70',
      glowClass: 'hover:shadow-glow-cyan'
    },
    {
      label: 'Avg Rental Price',
      value: store.propertyKPIs.avgRentalPrice ? formatPrice(store.propertyKPIs.avgRentalPrice) : 'N/A',
      icon: 'dollar',
      color: 'from-cottage-sage to-cottage-forest',
      glowClass: 'hover:shadow-glow-cyan'
    },
    {
      label: 'For-Sale Listings',
      value: formatNumber(store.propertyKPIs.totalForSaleListings),
      icon: 'building',
      color: 'from-primary-500 to-cyber-violet',
      glowClass: 'hover:shadow-glow-violet'
    },
    {
      label: 'Avg Sale Price',
      value: store.propertyKPIs.avgSalePrice ? formatPrice(store.propertyKPIs.avgSalePrice) : 'N/A',
      icon: 'chart',
      color: 'from-cottage-terracotta to-cottage-bark',
      glowClass: 'hover:shadow-glow-violet'
    }
  ];
});

const fredKpis = computed<KPIItem[]>(() => {
  if (!store.fredKPIs) return [];

  const items: KPIItem[] = [];

  // Housing Market KPIs
  if (store.fredKPIs.medianPrice) {
    items.push({
      label: 'Median List Price',
      value: formatPrice(store.fredKPIs.medianPrice),
      icon: 'tag',
      color: 'from-primary-500 to-cyber-magenta',
      glowClass: 'hover:shadow-glow-magenta'
    });
  }

  if (store.fredKPIs.activeListings) {
    items.push({
      label: 'Active Listings',
      value: formatNumber(store.fredKPIs.activeListings),
      icon: 'list',
      color: 'from-cyber-cyan to-accent-600',
      glowClass: 'hover:shadow-glow-cyan'
    });
  }

  if (store.fredKPIs.medianDom) {
    items.push({
      label: 'Days on Market',
      value: `${Math.round(store.fredKPIs.medianDom)}d`,
      icon: 'clock',
      color: 'from-cyber-magenta to-primary-600',
      glowClass: 'hover:shadow-glow-magenta'
    });
  }

  // Employment & Economy
  if (store.fredKPIs.unemploymentRate !== undefined) {
    items.push({
      label: 'Unemployment',
      value: `${store.fredKPIs.unemploymentRate.toFixed(1)}%`,
      icon: 'briefcase',
      color: 'from-cottage-sage to-cottage-forest',
      glowClass: 'hover:shadow-glow-cyan'
    });
  }

  // Financing
  if (store.fredKPIs.mortgageRate30yr !== undefined) {
    items.push({
      label: '30-Yr Rate',
      value: `${store.fredKPIs.mortgageRate30yr.toFixed(2)}%`,
      icon: 'percent',
      color: 'from-cyber-cyan to-cyber-violet',
      glowClass: 'hover:shadow-glow-cyan'
    });
  }

  // Income
  if (store.fredKPIs.perCapitaIncome) {
    items.push({
      label: 'Per Capita Income',
      value: formatPrice(store.fredKPIs.perCapitaIncome),
      icon: 'user',
      color: 'from-cottage-terracotta to-cottage-bark',
      glowClass: 'hover:shadow-glow-violet'
    });
  }

  // Construction
  if (store.fredKPIs.buildingPermits) {
    items.push({
      label: 'Building Permits',
      value: formatNumber(store.fredKPIs.buildingPermits),
      icon: 'building',
      color: 'from-cottage-forest to-cyber-navy',
      glowClass: 'hover:shadow-glow-cyan'
    });
  }

  // Consumer Sentiment
  if (store.fredKPIs.consumerSentiment !== undefined) {
    items.push({
      label: 'Consumer Sentiment',
      value: store.fredKPIs.consumerSentiment.toFixed(1),
      icon: 'chart',
      color: 'from-cyber-magenta to-primary-500',
      glowClass: 'hover:shadow-glow-magenta'
    });
  }

  return items;
});
</script>

<template>
  <div class="space-y-4">
    <!-- Property KPIs - Compact Grid -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-3">
      <div
        v-for="kpi in propertyKpis"
        :key="kpi.label"
        :class="['kpi-card p-4 transition-all duration-200', kpi.glowClass]"
      >
        <div class="flex items-center gap-3">
          <div :class="['w-9 h-9 rounded-lg bg-gradient-to-br flex items-center justify-center flex-shrink-0', kpi.color]">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="kpi.icon === 'home'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              <path v-else-if="kpi.icon === 'dollar'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              <path v-else-if="kpi.icon === 'building'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              <path v-else-if="kpi.icon === 'chart'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <div class="min-w-0">
            <p class="kpi-label truncate">{{ kpi.label }}</p>
            <p class="kpi-value">{{ kpi.value }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- FRED Economic KPIs - Compact Grid -->
    <div v-if="fredKpis.length > 0" class="grid grid-cols-2 lg:grid-cols-4 gap-3">
      <div
        v-for="kpi in fredKpis"
        :key="kpi.label"
        :class="['kpi-card p-4 transition-all duration-200', kpi.glowClass]"
      >
        <div class="flex items-center gap-3">
          <div :class="['w-9 h-9 rounded-lg bg-gradient-to-br flex items-center justify-center flex-shrink-0', kpi.color]">
            <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path v-if="kpi.icon === 'tag'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
              <path v-else-if="kpi.icon === 'list'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              <path v-else-if="kpi.icon === 'clock'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              <path v-else-if="kpi.icon === 'user'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              <path v-else-if="kpi.icon === 'briefcase'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
              <path v-else-if="kpi.icon === 'percent'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              <path v-else-if="kpi.icon === 'building'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              <path v-else-if="kpi.icon === 'chart'" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
              <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
            </svg>
          </div>
          <div class="min-w-0">
            <p class="kpi-label truncate">{{ kpi.label }}</p>
            <p class="kpi-value">{{ kpi.value }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useDashboardStore } from '@/stores/dashboard';
import VueApexCharts from 'vue3-apexcharts';

const store = useDashboardStore();

// Rental price distribution
const rentalPriceData = computed(() => {
  const properties = store.properties.filter(p => p.price !== null);
  if (properties.length === 0) return { categories: [], series: [] };

  // Create price buckets
  const buckets: Record<string, number> = {};
  const bucketSize = store.filters.propertyType === 'rental' ? 500 : 50000;
  const prefix = store.filters.propertyType === 'rental' ? '$' : '$';
  const suffix = store.filters.propertyType === 'rental' ? '' : 'K';
  const divisor = store.filters.propertyType === 'rental' ? 1 : 1000;

  properties.forEach(p => {
    if (p.price) {
      const bucket = Math.floor(p.price / bucketSize) * bucketSize;
      const label = `${prefix}${(bucket / divisor).toLocaleString()}${suffix}`;
      buckets[label] = (buckets[label] || 0) + 1;
    }
  });

  const sortedEntries = Object.entries(buckets).sort((a, b) => {
    const aNum = parseFloat(a[0].replace(/[$K,]/g, ''));
    const bNum = parseFloat(b[0].replace(/[$K,]/g, ''));
    return aNum - bNum;
  });

  return {
    categories: sortedEntries.map(([k]) => k),
    series: [{ name: 'Properties', data: sortedEntries.map(([, v]) => v) }]
  };
});

const priceChartOptions = computed(() => ({
  chart: {
    type: 'bar' as const,
    toolbar: { show: false },
    fontFamily: 'Inter, sans-serif'
  },
  colors: ['#667eea'],
  plotOptions: {
    bar: {
      borderRadius: 4,
      columnWidth: '60%'
    }
  },
  dataLabels: { enabled: false },
  xaxis: {
    categories: rentalPriceData.value.categories,
    labels: {
      style: { colors: '#6b7280', fontSize: '11px' },
      rotate: -45
    }
  },
  yaxis: {
    labels: {
      style: { colors: '#6b7280' }
    }
  },
  grid: {
    borderColor: '#e5e7eb',
    strokeDashArray: 4
  },
  tooltip: {
    theme: 'light'
  }
}));

// FRED metrics time series
const fredChartData = computed(() => {
  if (!store.fredMetrics || store.fredMetrics.length === 0) return null;

  // Get median price data
  const medianPriceData = store.fredMetrics
    .filter(m => m.metricName === 'median_price')
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  if (medianPriceData.length === 0) return null;

  return {
    dates: medianPriceData.map(m => m.date),
    values: medianPriceData.map(m => m.value)
  };
});

const fredChartOptions = computed(() => ({
  chart: {
    type: 'line' as const,
    toolbar: { show: false },
    fontFamily: 'Inter, sans-serif',
    zoom: { enabled: false }
  },
  colors: ['#f59e0b'],
  stroke: {
    width: 3,
    curve: 'smooth' as const
  },
  markers: {
    size: 0,
    hover: { size: 5 }
  },
  xaxis: {
    type: 'datetime' as const,
    categories: fredChartData.value?.dates || [],
    labels: {
      style: { colors: '#6b7280' },
      datetimeFormatter: {
        year: 'yyyy',
        month: "MMM 'yy"
      }
    }
  },
  yaxis: {
    labels: {
      style: { colors: '#6b7280' },
      formatter: (val: number) => `$${(val / 1000).toFixed(0)}K`
    }
  },
  grid: {
    borderColor: '#e5e7eb',
    strokeDashArray: 4
  },
  tooltip: {
    theme: 'light',
    x: { format: 'MMM yyyy' },
    y: {
      formatter: (val: number) => `$${val.toLocaleString()}`
    }
  }
}));
</script>

<template>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <!-- Price Distribution Chart -->
    <div class="card p-6">
      <h3 class="text-base font-semibold text-gray-900 mb-4">
        {{ store.filters.propertyType === 'rental' ? 'Rental' : 'Sale' }} Price Distribution
      </h3>
      <div v-if="rentalPriceData.series[0] && rentalPriceData.series[0].data.length > 0" class="h-64">
        <VueApexCharts
          type="bar"
          height="100%"
          :options="priceChartOptions"
          :series="rentalPriceData.series"
        />
      </div>
      <div v-else class="h-64 flex items-center justify-center text-gray-500">
        No data available
      </div>
    </div>

    <!-- FRED Median Price Trend -->
    <div class="card p-6">
      <h3 class="text-base font-semibold text-gray-900 mb-4">
        Median Listing Price Trend
      </h3>
      <div v-if="fredChartData" class="h-64">
        <VueApexCharts
          type="line"
          height="100%"
          :options="fredChartOptions"
          :series="[{ name: 'Median Price', data: fredChartData.values }]"
        />
      </div>
      <div v-else class="h-64 flex items-center justify-center text-gray-500">
        No FRED data available
      </div>
    </div>
  </div>
</template>

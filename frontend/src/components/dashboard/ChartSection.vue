<script setup lang="ts">
import { computed } from 'vue';
import { useDashboardStore } from '@/stores/dashboard';
import { Bar, Line } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  Filler
} from 'chart.js';
import 'chartjs-adapter-date-fns';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
  Filler
);

const store = useDashboardStore();

// Price distribution data for bar chart
const priceChartData = computed(() => {
  const properties = store.properties.filter(p => p.price !== null);
  if (properties.length === 0) return null;

  // Create price buckets
  const buckets: Record<string, number> = {};
  const bucketSize = store.filters.propertyType === 'rental' ? 500 : 50000;
  const prefix = '$';
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
    labels: sortedEntries.map(([k]) => k),
    datasets: [{
      label: 'Properties',
      data: sortedEntries.map(([, v]) => v),
      backgroundColor: '#667eea',
      borderRadius: 4,
      barPercentage: 0.6
    }]
  };
});

const priceChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#fff',
      titleColor: '#374151',
      bodyColor: '#374151',
      borderColor: '#e5e7eb',
      borderWidth: 1
    }
  },
  scales: {
    x: {
      grid: { display: false },
      ticks: {
        color: '#6b7280',
        font: { size: 11 },
        maxRotation: 45,
        minRotation: 45
      }
    },
    y: {
      grid: {
        color: '#e5e7eb',
        drawBorder: false
      },
      ticks: { color: '#6b7280' }
    }
  }
}));

// FRED metrics time series data
const fredChartData = computed(() => {
  if (!store.fredMetrics || store.fredMetrics.length === 0) return null;

  // Get median price data
  const medianPriceData = store.fredMetrics
    .filter(m => m.metricName === 'median_price')
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  if (medianPriceData.length === 0) return null;

  return {
    labels: medianPriceData.map(m => m.date),
    datasets: [{
      label: 'Median Price',
      data: medianPriceData.map(m => m.value),
      borderColor: '#f59e0b',
      backgroundColor: 'rgba(245, 158, 11, 0.1)',
      borderWidth: 3,
      tension: 0.4,
      fill: true,
      pointRadius: 0,
      pointHoverRadius: 5,
      pointHoverBackgroundColor: '#f59e0b'
    }]
  };
});

const fredChartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    intersect: false,
    mode: 'index' as const
  },
  plugins: {
    legend: { display: false },
    tooltip: {
      backgroundColor: '#fff',
      titleColor: '#374151',
      bodyColor: '#374151',
      borderColor: '#e5e7eb',
      borderWidth: 1,
      callbacks: {
        label: (context: any) => `$${context.raw.toLocaleString()}`
      }
    }
  },
  scales: {
    x: {
      type: 'time' as const,
      time: {
        unit: 'month' as const,
        displayFormats: {
          month: 'MMM yy'
        }
      },
      grid: { display: false },
      ticks: { color: '#6b7280' }
    },
    y: {
      type: 'linear' as const,
      grid: {
        color: '#e5e7eb',
        drawBorder: false
      },
      ticks: {
        color: '#6b7280',
        callback: function(value: string | number) {
          const num = typeof value === 'string' ? parseFloat(value) : value;
          return `$${(num / 1000).toFixed(0)}K`;
        }
      }
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
      <div v-if="priceChartData" class="h-64">
        <Bar :data="priceChartData" :options="priceChartOptions" />
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
        <Line :data="fredChartData" :options="fredChartOptions" />
      </div>
      <div v-else class="h-64 flex items-center justify-center text-gray-500">
        No FRED data available
      </div>
    </div>
  </div>
</template>

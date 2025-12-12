<script setup lang="ts">
import { computed } from 'vue'
import { Bar } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
} from 'chart.js'
import 'chartjs-adapter-date-fns'
import { useDashboardStore } from '@/stores/dashboard'
import { useChartConfig } from '@/composables/useChartConfig'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
)

const store = useDashboardStore()
const { chartColors, formatNumber, timeScaleOptions } = useChartConfig()

const chartData = computed(() => {
  if (!store.fredMetrics || store.fredMetrics.length === 0) return null

  // Filter for active listings
  const listingsData = store.fredMetrics
    .filter(m => m.metricName === 'active_listings')
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())

  // Filter for days on market
  const domData = store.fredMetrics
    .filter(m => m.metricName === 'median_dom')
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())

  if (listingsData.length === 0) return null

  return {
    labels: listingsData.map(m => m.date),
    datasets: [
      {
        label: 'Active Listings',
        data: listingsData.map(m => m.value),
        backgroundColor: chartColors.sage,
        borderRadius: 4,
        yAxisID: 'y',
      },
      ...(domData.length > 0 ? [{
        label: 'Days on Market',
        data: domData.map(m => m.value),
        backgroundColor: chartColors.terracotta,
        borderRadius: 4,
        yAxisID: 'y1',
      }] : [])
    ]
  }
})

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  interaction: {
    intersect: false,
    mode: 'index' as const,
  },
  plugins: {
    legend: {
      display: true,
      position: 'top' as const,
      labels: {
        color: chartColors.bark,
        font: { size: 10 },
        usePointStyle: true,
        padding: 8,
      },
    },
    tooltip: {
      backgroundColor: chartColors.navy,
      titleColor: chartColors.cyan,
      bodyColor: '#fff',
      borderColor: chartColors.cyan,
      borderWidth: 1,
      padding: 10,
      cornerRadius: 6,
    },
  },
  scales: {
    x: {
      ...timeScaleOptions,
    },
    y: {
      type: 'linear' as const,
      position: 'left' as const,
      grid: { color: `${chartColors.sand}60` },
      ticks: {
        color: chartColors.forest,
        font: { size: 9 },
        callback: (value: any) => formatNumber(value)
      },
    },
    y1: {
      type: 'linear' as const,
      position: 'right' as const,
      grid: { display: false },
      ticks: {
        color: chartColors.terracotta,
        font: { size: 9 },
        callback: (value: any) => `${Math.round(value)}d`
      },
    },
  },
}))
</script>

<template>
  <div class="chart-card h-full">
    <h3 class="flex items-center gap-2">
      <span class="w-2 h-2 rounded-full bg-cottage-sage"></span>
      Market Activity
    </h3>
    <div v-if="chartData" class="h-48">
      <Bar :data="chartData" :options="chartOptions" />
    </div>
    <div v-else class="h-48 flex items-center justify-center text-cottage-forest text-sm">
      No data available
    </div>
  </div>
</template>

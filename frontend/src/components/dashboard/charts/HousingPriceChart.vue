<script setup lang="ts">
import { computed } from 'vue'
import { Line } from 'vue-chartjs'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  TimeScale
} from 'chart.js'
import 'chartjs-adapter-date-fns'
import { useDashboardStore } from '@/stores/dashboard'
import { useChartConfig } from '@/composables/useChartConfig'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  TimeScale
)

const store = useDashboardStore()
const { chartColors, formatCurrency, timeScaleOptions } = useChartConfig()

const chartData = computed(() => {
  if (!store.fredMetrics || store.fredMetrics.length === 0) return null

  // Filter for median price data
  const priceData = store.fredMetrics
    .filter(m => m.metricName === 'median_price')
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())

  // Filter for price per sqft data
  const sqftData = store.fredMetrics
    .filter(m => m.metricName === 'median_pp_sqft')
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())

  if (priceData.length === 0) return null

  return {
    labels: priceData.map(m => m.date),
    datasets: [
      {
        label: 'Median Price',
        data: priceData.map(m => m.value),
        borderColor: chartColors.violet,
        backgroundColor: `${chartColors.violet}20`,
        fill: true,
        yAxisID: 'y',
      },
      ...(sqftData.length > 0 ? [{
        label: '$/Sqft',
        data: sqftData.map(m => m.value),
        borderColor: chartColors.cyan,
        backgroundColor: 'transparent',
        fill: false,
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
      callbacks: {
        label: (context: any) => {
          const label = context.dataset.label || ''
          const value = context.raw
          if (label === 'Median Price') return `${label}: ${formatCurrency(value)}`
          return `${label}: $${Math.round(value)}`
        }
      }
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
        callback: (value: any) => formatCurrency(value)
      },
    },
    y1: {
      type: 'linear' as const,
      position: 'right' as const,
      grid: { display: false },
      ticks: {
        color: chartColors.cyan,
        font: { size: 9 },
        callback: (value: any) => `$${Math.round(value)}`
      },
    },
  },
  elements: {
    line: { tension: 0.4, borderWidth: 2 },
    point: { radius: 0, hoverRadius: 4 },
  },
}))
</script>

<template>
  <div class="chart-card h-full">
    <h3 class="flex items-center gap-2">
      <span class="w-2 h-2 rounded-full bg-primary-500"></span>
      Housing Prices
    </h3>
    <div v-if="chartData" class="h-48">
      <Line :data="chartData" :options="chartOptions" />
    </div>
    <div v-else class="h-48 flex items-center justify-center text-cottage-forest text-sm">
      No data available
    </div>
  </div>
</template>

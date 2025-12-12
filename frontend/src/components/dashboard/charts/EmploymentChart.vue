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
const { chartColors, formatNumber, timeScaleOptions } = useChartConfig()

const chartData = computed(() => {
  if (!store.fredMetrics || store.fredMetrics.length === 0) return null

  // Filter for unemployment rate
  const unemploymentData = store.fredMetrics
    .filter(m => m.metricName === 'unemployment_rate')
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())

  // Filter for employment
  const employmentData = store.fredMetrics
    .filter(m => m.metricName === 'employment')
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())

  if (unemploymentData.length === 0 && employmentData.length === 0) return null

  const labels = unemploymentData.length > 0
    ? unemploymentData.map(m => m.date)
    : employmentData.map(m => m.date)

  return {
    labels,
    datasets: [
      ...(unemploymentData.length > 0 ? [{
        label: 'Unemployment Rate',
        data: unemploymentData.map(m => m.value),
        borderColor: chartColors.magenta,
        backgroundColor: `${chartColors.magenta}20`,
        fill: true,
        yAxisID: 'y',
      }] : []),
      ...(employmentData.length > 0 ? [{
        label: 'Employment (K)',
        data: employmentData.map(m => m.value / 1000),
        borderColor: chartColors.sage,
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
          if (label.includes('Unemployment')) return `${label}: ${value.toFixed(1)}%`
          return `${label}: ${formatNumber(value * 1000)}`
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
        color: chartColors.magenta,
        font: { size: 9 },
        callback: (value: any) => `${value}%`
      },
    },
    y1: {
      type: 'linear' as const,
      position: 'right' as const,
      grid: { display: false },
      ticks: {
        color: chartColors.sage,
        font: { size: 9 },
        callback: (value: any) => `${Math.round(value)}K`
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
      <span class="w-2 h-2 rounded-full bg-cyber-magenta"></span>
      Employment Trends
    </h3>
    <div v-if="chartData" class="h-48">
      <Line :data="chartData" :options="chartOptions" />
    </div>
    <div v-else class="h-48 flex items-center justify-center text-cottage-forest text-sm">
      No data available
    </div>
  </div>
</template>

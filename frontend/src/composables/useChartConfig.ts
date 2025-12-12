/**
 * Shared chart configuration for cottage-core + cyberpunk theme
 * Provides consistent styling across all chart components
 */

import { computed } from 'vue'
import type { ChartOptions } from 'chart.js'

// Theme colors matching tailwind.config.js
export const chartColors = {
  // Cottage-core
  cream: '#F5F1E8',
  sand: '#E8DCC8',
  wheat: '#C9B896',
  sage: '#7A9B76',
  terracotta: '#A67B5B',
  forest: '#5B7065',
  bark: '#4A3728',
  // Cyberpunk
  cyan: '#00F5FF',
  magenta: '#FF2E97',
  violet: '#B026FF',
  navy: '#0A0E27',
  deepBlue: '#1A1F3A',
}

// Gradient generators for Chart.js
export function createGradient(ctx: CanvasRenderingContext2D, color: string, alpha = 0.3) {
  const gradient = ctx.createLinearGradient(0, 0, 0, 300)
  gradient.addColorStop(0, `${color}${Math.round(alpha * 255).toString(16).padStart(2, '0')}`)
  gradient.addColorStop(1, `${color}00`)
  return gradient
}

// Shared base chart options
export function useChartConfig() {
  const baseOptions = computed<Partial<ChartOptions>>(() => ({
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
          font: { size: 11, family: 'Inter' },
          padding: 12,
          usePointStyle: true,
          pointStyle: 'circle',
        },
      },
      tooltip: {
        backgroundColor: chartColors.navy,
        titleColor: chartColors.cyan,
        bodyColor: '#fff',
        borderColor: chartColors.cyan,
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
        displayColors: true,
        titleFont: { weight: 'bold' as const },
      },
    },
    scales: {
      x: {
        grid: {
          display: false,
        },
        ticks: {
          color: chartColors.forest,
          font: { size: 10 },
        },
      },
      y: {
        grid: {
          color: `${chartColors.sand}80`,
        },
        ticks: {
          color: chartColors.forest,
          font: { size: 10 },
        },
      },
    },
  }))

  // Line chart specific options
  const lineOptions = computed(() => ({
    ...baseOptions.value,
    elements: {
      line: {
        tension: 0.4,
        borderWidth: 2,
      },
      point: {
        radius: 0,
        hoverRadius: 5,
        hoverBorderWidth: 2,
      },
    },
  }))

  // Bar chart specific options
  const barOptions = computed(() => ({
    ...baseOptions.value,
    elements: {
      bar: {
        borderRadius: 4,
        borderSkipped: false,
      },
    },
  }))

  // Time scale options
  const timeScaleOptions = {
    type: 'time' as const,
    time: {
      unit: 'month' as const,
      displayFormats: {
        month: 'MMM yy',
      },
    },
    grid: { display: false },
    ticks: {
      color: chartColors.forest,
      font: { size: 10 },
      maxTicksLimit: 8,
    },
  }

  // Currency formatter
  const formatCurrency = (value: number) => {
    if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`
    if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`
    return `$${value.toFixed(0)}`
  }

  // Percent formatter
  const formatPercent = (value: number) => `${value.toFixed(1)}%`

  // Number formatter
  const formatNumber = (value: number) => {
    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`
    if (value >= 1000) return `${(value / 1000).toFixed(0)}K`
    return value.toFixed(0)
  }

  return {
    chartColors,
    baseOptions,
    lineOptions,
    barOptions,
    timeScaleOptions,
    formatCurrency,
    formatPercent,
    formatNumber,
    createGradient,
  }
}

export default useChartConfig

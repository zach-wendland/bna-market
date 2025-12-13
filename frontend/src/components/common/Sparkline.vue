<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  data: number[]
  width?: number
  height?: number
  color?: string
  fillColor?: string
  showDots?: boolean
  animate?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  width: 120,
  height: 32,
  color: '#B026FF',
  fillColor: 'rgba(176, 38, 255, 0.1)',
  showDots: false,
  animate: true
})

const padding = 4

interface Point {
  x: number
  y: number
}

const pathData = computed<{ line: string; area: string; points: Point[] }>(() => {
  if (!props.data || props.data.length < 2) return { line: '', area: '', points: [] }

  const filteredData = props.data.filter(v => v !== null && v !== undefined)
  if (filteredData.length < 2) return { line: '', area: '', points: [] }

  const min = Math.min(...filteredData)
  const max = Math.max(...filteredData)
  const range = max - min || 1

  const innerWidth = props.width - padding * 2
  const innerHeight = props.height - padding * 2

  const points: Point[] = filteredData.map((value, index) => {
    const x = padding + (index / (filteredData.length - 1)) * innerWidth
    const y = padding + innerHeight - ((value - min) / range) * innerHeight
    return { x, y }
  })

  // Create SVG path
  const linePath = points.reduce((path, point, index) => {
    return path + (index === 0 ? `M ${point.x},${point.y}` : ` L ${point.x},${point.y}`)
  }, '')

  // Create area path (closed polygon for fill)
  const lastPoint = points[points.length - 1]
  const areaPath = lastPoint
    ? linePath + ` L ${lastPoint.x},${props.height - padding} L ${padding},${props.height - padding} Z`
    : ''

  return { line: linePath, area: areaPath, points }
})
</script>

<template>
  <svg
    :width="width"
    :height="height"
    class="sparkline"
    :class="{ 'sparkline--animate': animate }"
  >
    <!-- Gradient definition -->
    <defs>
      <linearGradient :id="`sparkline-gradient-${$.uid}`" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" :stop-color="fillColor" />
        <stop offset="100%" stop-color="transparent" />
      </linearGradient>
    </defs>

    <!-- Area fill -->
    <path
      v-if="pathData.area"
      :d="pathData.area"
      :fill="`url(#sparkline-gradient-${$.uid})`"
      class="sparkline-area"
    />

    <!-- Line -->
    <path
      v-if="pathData.line"
      :d="pathData.line"
      :stroke="color"
      stroke-width="2"
      fill="none"
      stroke-linecap="round"
      stroke-linejoin="round"
      class="sparkline-line"
    />

    <!-- End dot -->
    <circle
      v-if="pathData.points.length > 0"
      :cx="pathData.points[pathData.points.length - 1]?.x"
      :cy="pathData.points[pathData.points.length - 1]?.y"
      r="3"
      :fill="color"
      class="sparkline-dot"
    />
  </svg>
</template>

<style scoped>
.sparkline {
  display: block;
}

.sparkline--animate .sparkline-line {
  stroke-dasharray: 1000;
  stroke-dashoffset: 1000;
  animation: sparkline-draw 1.5s ease-out forwards;
}

.sparkline--animate .sparkline-area {
  opacity: 0;
  animation: sparkline-fade 0.5s ease-out 1s forwards;
}

.sparkline--animate .sparkline-dot {
  opacity: 0;
  animation: sparkline-fade 0.3s ease-out 1.2s forwards;
}

@keyframes sparkline-draw {
  to {
    stroke-dashoffset: 0;
  }
}

@keyframes sparkline-fade {
  to {
    opacity: 1;
  }
}
</style>

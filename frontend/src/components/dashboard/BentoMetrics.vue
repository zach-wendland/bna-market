<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'
import Sparkline from '@/components/common/Sparkline.vue'
import { fetchPropertyTrends, type PropertyTrendsResponse } from '@/api/client'

const store = useDashboardStore()
const propertyTrends = ref<PropertyTrendsResponse | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

onMounted(async () => {
  try {
    propertyTrends.value = await fetchPropertyTrends(12)
  } catch (e) {
    error.value = 'Failed to load trends'
    console.error('Failed to load property trends:', e)
  } finally {
    loading.value = false
  }
})

// Format currency
const formatPrice = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return 'N/A'
  if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`
  if (value >= 1000) return `$${(value / 1000).toFixed(0)}K`
  return `$${value.toLocaleString()}`
}

// Format DOM
const formatDom = (value: number | null | undefined): string => {
  if (value === null || value === undefined) return 'N/A'
  return `${Math.round(value)} days`
}

// Calculate trend percentage
const calcTrend = (data: { avgPrice: number | null }[]): number => {
  if (!data || data.length < 2) return 0
  const validData = data.filter((d): d is { avgPrice: number } => d.avgPrice !== null)
  if (validData.length < 2) return 0
  const firstItem = validData[0]
  const lastItem = validData[validData.length - 1]
  if (!firstItem || !lastItem) return 0
  const first = firstItem.avgPrice
  const last = lastItem.avgPrice
  return ((last - first) / first) * 100
}

// Extract sparkline data
const rentalPriceData = computed(() => {
  const trends = propertyTrends.value?.rentalTrends
  if (!trends) return []
  return trends.map(t => t.avgPrice).filter((v): v is number => v !== null)
})
const salePriceData = computed(() => {
  const trends = propertyTrends.value?.saleTrends
  if (!trends) return []
  return trends.map(t => t.avgPrice).filter((v): v is number => v !== null)
})
const rentalDomData = computed(() => {
  const trends = propertyTrends.value?.rentalTrends
  if (!trends) return []
  return trends.map(t => t.avgDom).filter((v): v is number => v !== null)
})
const saleDomData = computed(() => {
  const trends = propertyTrends.value?.saleTrends
  if (!trends) return []
  return trends.map(t => t.avgDom).filter((v): v is number => v !== null)
})

// Get FRED metrics for additional cards
const activeListings = computed(() => {
  const metric = store.fredMetrics?.find(m => m.metricName === 'active_listings')
  return metric?.value
})

const marketSentiment = computed(() => {
  const metric = store.fredMetrics?.find(m => m.metricName === 'consumer_sentiment')
  return metric?.value
})

// Trend colors
const trendColor = (value: number): string => {
  if (value > 0) return 'text-green-600'
  if (value < 0) return 'text-red-500'
  return 'text-gray-500'
}

const trendIcon = (value: number): string => {
  if (value > 0) return '▲'
  if (value < 0) return '▼'
  return '—'
}

// Current stats
const currentStats = computed(() => propertyTrends.value?.currentStats)
</script>

<template>
  <div class="bento-grid">
    <!-- Row 1: Price Metrics -->
    <div class="bento-card bento-card--rental">
      <div class="bento-header">
        <span class="bento-dot bento-dot--rental"></span>
        <span class="bento-label">Avg Rental Price</span>
      </div>
      <div class="bento-value">
        {{ loading ? '...' : formatPrice(currentStats?.rental.avgPrice) }}
      </div>
      <div v-if="!loading && rentalPriceData.length > 1" class="bento-trend">
        <span :class="trendColor(calcTrend(propertyTrends?.rentalTrends || []))">
          {{ trendIcon(calcTrend(propertyTrends?.rentalTrends || [])) }}
          {{ Math.abs(calcTrend(propertyTrends?.rentalTrends || [])).toFixed(1) }}%
        </span>
      </div>
      <div class="bento-sparkline">
        <Sparkline
          v-if="rentalPriceData.length > 1"
          :data="rentalPriceData"
          :width="140"
          :height="40"
          color="#00F5FF"
          fill-color="rgba(0, 245, 255, 0.15)"
        />
        <div v-else class="bento-no-data">Accumulating data...</div>
      </div>
    </div>

    <div class="bento-card bento-card--sale">
      <div class="bento-header">
        <span class="bento-dot bento-dot--sale"></span>
        <span class="bento-label">Avg Sale Price</span>
      </div>
      <div class="bento-value">
        {{ loading ? '...' : formatPrice(currentStats?.sale.avgPrice) }}
      </div>
      <div v-if="!loading && salePriceData.length > 1" class="bento-trend">
        <span :class="trendColor(calcTrend(propertyTrends?.saleTrends || []))">
          {{ trendIcon(calcTrend(propertyTrends?.saleTrends || [])) }}
          {{ Math.abs(calcTrend(propertyTrends?.saleTrends || [])).toFixed(1) }}%
        </span>
      </div>
      <div class="bento-sparkline">
        <Sparkline
          v-if="salePriceData.length > 1"
          :data="salePriceData"
          :width="140"
          :height="40"
          color="#B026FF"
          fill-color="rgba(176, 38, 255, 0.15)"
        />
        <div v-else class="bento-no-data">Accumulating data...</div>
      </div>
    </div>

    <div class="bento-card bento-card--dom">
      <div class="bento-header">
        <span class="bento-dot bento-dot--dom"></span>
        <span class="bento-label">Rental DOM</span>
      </div>
      <div class="bento-value">
        {{ loading ? '...' : formatDom(currentStats?.rental.avgDom) }}
      </div>
      <div class="bento-sparkline">
        <Sparkline
          v-if="rentalDomData.length > 1"
          :data="rentalDomData"
          :width="140"
          :height="40"
          color="#FF2E97"
          fill-color="rgba(255, 46, 151, 0.15)"
        />
        <div v-else class="bento-no-data">Accumulating data...</div>
      </div>
    </div>

    <!-- Row 2: DOM and Market Metrics -->
    <div class="bento-card bento-card--dom">
      <div class="bento-header">
        <span class="bento-dot bento-dot--sale"></span>
        <span class="bento-label">For-Sale DOM</span>
      </div>
      <div class="bento-value">
        {{ loading ? '...' : formatDom(currentStats?.sale.avgDom) }}
      </div>
      <div class="bento-sparkline">
        <Sparkline
          v-if="saleDomData.length > 1"
          :data="saleDomData"
          :width="140"
          :height="40"
          color="#B026FF"
          fill-color="rgba(176, 38, 255, 0.15)"
        />
        <div v-else class="bento-no-data">Accumulating data...</div>
      </div>
    </div>

    <div class="bento-card bento-card--listings">
      <div class="bento-header">
        <span class="bento-dot bento-dot--rental"></span>
        <span class="bento-label">Active Listings</span>
      </div>
      <div class="bento-value">
        {{ activeListings?.toLocaleString() || 'N/A' }}
      </div>
      <div class="bento-subtext">Nashville MSA</div>
    </div>

    <div class="bento-card bento-card--sentiment">
      <div class="bento-header">
        <span class="bento-dot bento-dot--dom"></span>
        <span class="bento-label">Market Sentiment</span>
      </div>
      <div class="bento-value">
        {{ marketSentiment?.toFixed(1) || 'N/A' }}
      </div>
      <div class="bento-subtext">Consumer Index</div>
    </div>
  </div>
</template>

<style scoped>
.bento-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

@media (max-width: 1024px) {
  .bento-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .bento-grid {
    grid-template-columns: 1fr;
  }
}

.bento-card {
  @apply bg-white rounded-xl p-5 border border-cottage-sand/50;
  @apply transition-all duration-300;
  background: linear-gradient(135deg, white 0%, #F5F1E8 100%);
  position: relative;
  overflow: hidden;
}

.bento-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--accent-color, #00F5FF), transparent);
  opacity: 0;
  transition: opacity 0.3s;
}

.bento-card:hover::before {
  opacity: 1;
}

.bento-card:hover {
  @apply shadow-lg border-cottage-wheat;
  transform: translateY(-2px);
}

.bento-card--rental {
  --accent-color: #00F5FF;
}

.bento-card--sale {
  --accent-color: #B026FF;
}

.bento-card--dom {
  --accent-color: #FF2E97;
}

.bento-card--listings {
  --accent-color: #00F5FF;
}

.bento-card--sentiment {
  --accent-color: #FF2E97;
}

.bento-header {
  @apply flex items-center gap-2 mb-2;
}

.bento-dot {
  @apply w-2 h-2 rounded-full;
}

.bento-dot--rental {
  @apply bg-cyber-cyan;
  box-shadow: 0 0 8px rgba(0, 245, 255, 0.5);
}

.bento-dot--sale {
  @apply bg-cyber-violet;
  box-shadow: 0 0 8px rgba(176, 38, 255, 0.5);
}

.bento-dot--dom {
  @apply bg-cyber-magenta;
  box-shadow: 0 0 8px rgba(255, 46, 151, 0.5);
}

.bento-label {
  @apply text-xs font-medium text-cottage-forest uppercase tracking-wide;
}

.bento-value {
  @apply text-2xl font-bold text-cyber-navy mb-1;
}

.bento-trend {
  @apply text-sm font-medium mb-2;
}

.bento-subtext {
  @apply text-xs text-cottage-wheat;
}

.bento-sparkline {
  @apply mt-2;
  min-height: 40px;
}

.bento-no-data {
  @apply text-xs text-cottage-wheat italic;
}
</style>

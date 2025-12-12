<script setup lang="ts">
import { defineAsyncComponent } from 'vue'

// Lazy load all chart components for better performance
const HousingPriceChart = defineAsyncComponent(() =>
  import('./charts/HousingPriceChart.vue')
)
const MarketActivityChart = defineAsyncComponent(() =>
  import('./charts/MarketActivityChart.vue')
)
const EmploymentChart = defineAsyncComponent(() =>
  import('./charts/EmploymentChart.vue')
)
const MortgageRatesChart = defineAsyncComponent(() =>
  import('./charts/MortgageRatesChart.vue')
)
const IncomeChart = defineAsyncComponent(() =>
  import('./charts/IncomeChart.vue')
)
const ConsumerSentimentChart = defineAsyncComponent(() =>
  import('./charts/ConsumerSentimentChart.vue')
)
</script>

<template>
  <section class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="section-heading flex items-center gap-2">
        <span class="w-1 h-6 bg-gradient-to-b from-cyber-cyan to-cyber-violet rounded-full"></span>
        Nashville Market Insights
        <span class="text-xs font-normal text-cottage-forest ml-2">(2023-Present)</span>
      </h2>
    </div>

    <!-- 6-Chart Grid Layout -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <Suspense>
        <HousingPriceChart />
        <template #fallback>
          <div class="chart-card h-full">
            <div class="h-48 flex items-center justify-center">
              <div class="spinner-cyber"></div>
            </div>
          </div>
        </template>
      </Suspense>

      <Suspense>
        <MarketActivityChart />
        <template #fallback>
          <div class="chart-card h-full">
            <div class="h-48 flex items-center justify-center">
              <div class="spinner-cyber"></div>
            </div>
          </div>
        </template>
      </Suspense>

      <Suspense>
        <MortgageRatesChart />
        <template #fallback>
          <div class="chart-card h-full">
            <div class="h-48 flex items-center justify-center">
              <div class="spinner-cyber"></div>
            </div>
          </div>
        </template>
      </Suspense>

      <Suspense>
        <EmploymentChart />
        <template #fallback>
          <div class="chart-card h-full">
            <div class="h-48 flex items-center justify-center">
              <div class="spinner-cyber"></div>
            </div>
          </div>
        </template>
      </Suspense>

      <Suspense>
        <IncomeChart />
        <template #fallback>
          <div class="chart-card h-full">
            <div class="h-48 flex items-center justify-center">
              <div class="spinner-cyber"></div>
            </div>
          </div>
        </template>
      </Suspense>

      <Suspense>
        <ConsumerSentimentChart />
        <template #fallback>
          <div class="chart-card h-full">
            <div class="h-48 flex items-center justify-center">
              <div class="spinner-cyber"></div>
            </div>
          </div>
        </template>
      </Suspense>
    </div>
  </section>
</template>

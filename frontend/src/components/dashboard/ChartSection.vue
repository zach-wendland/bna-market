<script setup lang="ts">
import { defineAsyncComponent } from 'vue'
import BentoMetrics from './BentoMetrics.vue'

// Lazy load chart components for better performance
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
</script>

<template>
  <section class="space-y-6">
    <!-- NEW: Bento Grid Metrics -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <h2 class="section-heading flex items-center gap-2">
          <span class="w-1 h-6 bg-gradient-to-b from-cyber-cyan to-cyber-violet rounded-full"></span>
          Nashville Market Insights
          <span class="text-xs font-normal text-cottage-forest ml-2">(Live Data)</span>
        </h2>
      </div>
      <BentoMetrics />
    </div>

    <!-- Economic Indicators Grid (4 charts) -->
    <div>
      <h3 class="text-sm font-medium text-cottage-forest uppercase tracking-wide mb-3">
        Economic Indicators
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
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
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useDashboardStore } from '@/stores/dashboard'

const store = useDashboardStore()
const activeTab = ref<'caprate' | 'dscr' | 'whatif'>('caprate')

// Cap Rate Calculator
const purchasePrice = ref(300000)
const annualRent = ref(24000)
const operatingExpenses = ref(6000)
const vacancyRate = ref(5)

const noi = computed(() => {
  const grossRent = annualRent.value
  const vacancyLoss = grossRent * (vacancyRate.value / 100)
  return grossRent - vacancyLoss - operatingExpenses.value
})

const capRate = computed(() => {
  if (purchasePrice.value <= 0) return 0
  return (noi.value / purchasePrice.value) * 100
})

const cashOnCashReturn = computed(() => {
  const downPayment = purchasePrice.value * 0.25 // Assume 25% down
  if (downPayment <= 0) return 0
  const annualCashFlow = noi.value - (purchasePrice.value * 0.75 * 0.07 / 12 * 12) // Rough mortgage estimate
  return (annualCashFlow / downPayment) * 100
})

// DSCR Calculator
const dscrNoi = ref(18000)
const loanAmount = ref(225000)
const interestRate = ref(7.0)
const loanTerm = ref(30)

const monthlyDebtService = computed(() => {
  const monthlyRate = interestRate.value / 100 / 12
  const numPayments = loanTerm.value * 12
  if (monthlyRate <= 0 || numPayments <= 0) return 0
  return (loanAmount.value * monthlyRate * Math.pow(1 + monthlyRate, numPayments)) /
    (Math.pow(1 + monthlyRate, numPayments) - 1)
})

const annualDebtService = computed(() => monthlyDebtService.value * 12)

const dscr = computed(() => {
  if (annualDebtService.value <= 0) return 0
  return dscrNoi.value / annualDebtService.value
})

const dscrIndicator = computed(() => {
  if (dscr.value >= 1.25) return { label: 'Strong', color: 'text-cottage-sage', bg: 'bg-cottage-sage/20' }
  if (dscr.value >= 1.0) return { label: 'Marginal', color: 'text-cottage-terracotta', bg: 'bg-cottage-terracotta/20' }
  return { label: 'Risky', color: 'text-cyber-magenta', bg: 'bg-cyber-magenta/20' }
})

// What-If Scenarios
const basePrice = ref(350000)
const currentMortgageRate = computed(() => store.fredKPIs?.mortgageRate30yr || 7.0)
const rateAdjustment = ref(0)
const projectedRate = computed(() => currentMortgageRate.value + rateAdjustment.value)

const inventoryChange = ref(0) // Percentage change in inventory
const baseMonthlyRent = ref(2500)

const projectedPayment = computed(() => {
  const principal = basePrice.value * 0.80 // 20% down
  const monthlyRate = projectedRate.value / 100 / 12
  const numPayments = 360 // 30 years
  if (monthlyRate <= 0) return 0
  return (principal * monthlyRate * Math.pow(1 + monthlyRate, numPayments)) /
    (Math.pow(1 + monthlyRate, numPayments) - 1)
})

const projectedCashFlow = computed(() => {
  const rent = baseMonthlyRent.value * (1 + inventoryChange.value / 100 * -0.5) // Inventory affects rent
  const expenses = rent * 0.35 // Assume 35% expense ratio
  return rent - projectedPayment.value - expenses
})

const projectedROI = computed(() => {
  const downPayment = basePrice.value * 0.20
  const annualCashFlow = projectedCashFlow.value * 12
  if (downPayment <= 0) return 0
  return (annualCashFlow / downPayment) * 100
})

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

function formatPercent(value: number): string {
  return `${value.toFixed(2)}%`
}
</script>

<template>
  <main class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <h1 class="section-heading flex items-center gap-2 mb-6">
      <span class="w-1 h-6 bg-gradient-to-b from-cyber-cyan to-primary-500 rounded-full"></span>
      Pricing Intelligence Tools
    </h1>

    <!-- Tab Navigation -->
    <div class="flex gap-2 mb-6 border-b border-cottage-sand pb-2">
      <button
        @click="activeTab = 'caprate'"
        :class="[
          'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors',
          activeTab === 'caprate'
            ? 'bg-gradient-to-r from-primary-500/10 to-cyber-cyan/10 text-primary-600 border-b-2 border-primary-500'
            : 'text-cottage-forest hover:text-cyber-navy'
        ]"
      >
        Cap Rate Calculator
      </button>
      <button
        @click="activeTab = 'dscr'"
        :class="[
          'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors',
          activeTab === 'dscr'
            ? 'bg-gradient-to-r from-primary-500/10 to-cyber-cyan/10 text-primary-600 border-b-2 border-primary-500'
            : 'text-cottage-forest hover:text-cyber-navy'
        ]"
      >
        DSCR Calculator
      </button>
      <button
        @click="activeTab = 'whatif'"
        :class="[
          'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors',
          activeTab === 'whatif'
            ? 'bg-gradient-to-r from-primary-500/10 to-cyber-cyan/10 text-primary-600 border-b-2 border-primary-500'
            : 'text-cottage-forest hover:text-cyber-navy'
        ]"
      >
        What-If Scenarios
      </button>
    </div>

    <!-- Cap Rate Calculator -->
    <div v-if="activeTab === 'caprate'" class="card p-6">
      <h2 class="text-lg font-semibold text-cyber-navy mb-4">Capitalization Rate Analysis</h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Inputs -->
        <div class="space-y-4">
          <div>
            <label class="label">Purchase Price</label>
            <div class="relative">
              <span class="absolute left-3 top-2 text-cottage-forest">$</span>
              <input
                v-model.number="purchasePrice"
                type="number"
                class="input pl-7"
                min="0"
                step="10000"
              />
            </div>
          </div>

          <div>
            <label class="label">Annual Gross Rent</label>
            <div class="relative">
              <span class="absolute left-3 top-2 text-cottage-forest">$</span>
              <input
                v-model.number="annualRent"
                type="number"
                class="input pl-7"
                min="0"
                step="1000"
              />
            </div>
          </div>

          <div>
            <label class="label">Annual Operating Expenses</label>
            <div class="relative">
              <span class="absolute left-3 top-2 text-cottage-forest">$</span>
              <input
                v-model.number="operatingExpenses"
                type="number"
                class="input pl-7"
                min="0"
                step="500"
              />
            </div>
          </div>

          <div>
            <label class="label">Vacancy Rate (%)</label>
            <input
              v-model.number="vacancyRate"
              type="number"
              class="input"
              min="0"
              max="100"
              step="1"
            />
          </div>
        </div>

        <!-- Results -->
        <div class="space-y-4">
          <div class="kpi-card p-4 hover:shadow-glow-cyan">
            <p class="kpi-label">Net Operating Income (NOI)</p>
            <p class="kpi-value text-xl">{{ formatCurrency(noi) }}</p>
          </div>

          <div class="kpi-card p-4 hover:shadow-glow-violet">
            <p class="kpi-label">Cap Rate</p>
            <p class="kpi-value text-2xl text-primary-500">{{ formatPercent(capRate) }}</p>
            <p class="text-xs text-cottage-forest mt-1">
              {{ capRate >= 6 ? 'Good investment potential' : capRate >= 4 ? 'Average market rate' : 'Below market average' }}
            </p>
          </div>

          <div class="kpi-card p-4 hover:shadow-glow-cyan">
            <p class="kpi-label">Cash-on-Cash Return (Est.)</p>
            <p class="kpi-value">{{ formatPercent(cashOnCashReturn) }}</p>
            <p class="text-xs text-cottage-forest mt-1">Assumes 25% down payment</p>
          </div>
        </div>
      </div>
    </div>

    <!-- DSCR Calculator -->
    <div v-if="activeTab === 'dscr'" class="card p-6">
      <h2 class="text-lg font-semibold text-cyber-navy mb-4">Debt Service Coverage Ratio</h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Inputs -->
        <div class="space-y-4">
          <div>
            <label class="label">Annual NOI</label>
            <div class="relative">
              <span class="absolute left-3 top-2 text-cottage-forest">$</span>
              <input
                v-model.number="dscrNoi"
                type="number"
                class="input pl-7"
                min="0"
                step="1000"
              />
            </div>
          </div>

          <div>
            <label class="label">Loan Amount</label>
            <div class="relative">
              <span class="absolute left-3 top-2 text-cottage-forest">$</span>
              <input
                v-model.number="loanAmount"
                type="number"
                class="input pl-7"
                min="0"
                step="10000"
              />
            </div>
          </div>

          <div>
            <label class="label">Interest Rate (%)</label>
            <input
              v-model.number="interestRate"
              type="number"
              class="input"
              min="0"
              max="20"
              step="0.125"
            />
          </div>

          <div>
            <label class="label">Loan Term (Years)</label>
            <select v-model.number="loanTerm" class="select">
              <option :value="15">15 Years</option>
              <option :value="20">20 Years</option>
              <option :value="25">25 Years</option>
              <option :value="30">30 Years</option>
            </select>
          </div>
        </div>

        <!-- Results -->
        <div class="space-y-4">
          <div class="kpi-card p-4">
            <p class="kpi-label">Monthly Debt Service</p>
            <p class="kpi-value text-xl">{{ formatCurrency(monthlyDebtService) }}</p>
          </div>

          <div class="kpi-card p-4">
            <p class="kpi-label">Annual Debt Service</p>
            <p class="kpi-value text-xl">{{ formatCurrency(annualDebtService) }}</p>
          </div>

          <div :class="['kpi-card p-4', dscrIndicator.bg]">
            <p class="kpi-label">DSCR Ratio</p>
            <p :class="['kpi-value text-2xl', dscrIndicator.color]">{{ dscr.toFixed(2) }}x</p>
            <p :class="['text-sm font-medium mt-1', dscrIndicator.color]">{{ dscrIndicator.label }}</p>
          </div>

          <div class="p-3 bg-cottage-cream rounded-lg text-xs text-cottage-forest">
            <p class="font-medium mb-1">DSCR Guidelines:</p>
            <ul class="space-y-1">
              <li><span class="text-cottage-sage font-medium">&ge;1.25:</span> Strong - Qualifies for most loans</li>
              <li><span class="text-cottage-terracotta font-medium">1.0-1.25:</span> Marginal - May require higher rate</li>
              <li><span class="text-cyber-magenta font-medium">&lt;1.0:</span> Risky - Negative cash flow</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- What-If Scenarios -->
    <div v-if="activeTab === 'whatif'" class="card p-6">
      <h2 class="text-lg font-semibold text-cyber-navy mb-4">What-If Scenario Analysis</h2>

      <div class="mb-4 p-3 bg-gradient-to-r from-cyber-navy to-cyber-deepBlue rounded-lg">
        <p class="text-cyber-cyan text-sm">
          Current 30-Year Mortgage Rate (FRED): <span class="font-bold">{{ currentMortgageRate.toFixed(2) }}%</span>
        </p>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Inputs -->
        <div class="space-y-4">
          <div>
            <label class="label">Property Price</label>
            <div class="relative">
              <span class="absolute left-3 top-2 text-cottage-forest">$</span>
              <input
                v-model.number="basePrice"
                type="number"
                class="input pl-7"
                min="0"
                step="25000"
              />
            </div>
          </div>

          <div>
            <label class="label">Monthly Rent</label>
            <div class="relative">
              <span class="absolute left-3 top-2 text-cottage-forest">$</span>
              <input
                v-model.number="baseMonthlyRent"
                type="number"
                class="input pl-7"
                min="0"
                step="100"
              />
            </div>
          </div>

          <div>
            <label class="label">Rate Adjustment ({{ rateAdjustment >= 0 ? '+' : '' }}{{ rateAdjustment.toFixed(2) }}%)</label>
            <input
              v-model.number="rateAdjustment"
              type="range"
              class="w-full h-2 bg-cottage-sand rounded-lg appearance-none cursor-pointer"
              min="-2"
              max="2"
              step="0.25"
            />
            <div class="flex justify-between text-xs text-cottage-forest mt-1">
              <span>-2%</span>
              <span class="font-medium text-primary-500">{{ projectedRate.toFixed(2) }}%</span>
              <span>+2%</span>
            </div>
          </div>

          <div>
            <label class="label">Inventory Change ({{ inventoryChange >= 0 ? '+' : '' }}{{ inventoryChange }}%)</label>
            <input
              v-model.number="inventoryChange"
              type="range"
              class="w-full h-2 bg-cottage-sand rounded-lg appearance-none cursor-pointer"
              min="-20"
              max="20"
              step="5"
            />
            <div class="flex justify-between text-xs text-cottage-forest mt-1">
              <span>-20%</span>
              <span>0%</span>
              <span>+20%</span>
            </div>
          </div>
        </div>

        <!-- Results -->
        <div class="space-y-4">
          <div class="kpi-card p-4">
            <p class="kpi-label">Projected Monthly Payment</p>
            <p class="kpi-value text-xl">{{ formatCurrency(projectedPayment) }}</p>
            <p class="text-xs text-cottage-forest mt-1">20% down, 30-year fixed</p>
          </div>

          <div :class="[
            'kpi-card p-4',
            projectedCashFlow >= 0 ? 'bg-cottage-sage/10' : 'bg-cyber-magenta/10'
          ]">
            <p class="kpi-label">Monthly Cash Flow</p>
            <p :class="[
              'kpi-value text-xl',
              projectedCashFlow >= 0 ? 'text-cottage-sage' : 'text-cyber-magenta'
            ]">
              {{ formatCurrency(projectedCashFlow) }}
            </p>
          </div>

          <div class="kpi-card p-4 hover:shadow-glow-violet">
            <p class="kpi-label">Projected ROI</p>
            <p :class="[
              'kpi-value text-2xl',
              projectedROI >= 8 ? 'text-cottage-sage' : projectedROI >= 4 ? 'text-cottage-terracotta' : 'text-cyber-magenta'
            ]">
              {{ formatPercent(projectedROI) }}
            </p>
          </div>

          <div class="p-3 bg-cottage-cream rounded-lg text-xs text-cottage-forest">
            <p class="font-medium mb-1">Scenario Impact:</p>
            <p>Higher rates increase payments, reducing cash flow.</p>
            <p>Higher inventory may decrease rents due to competition.</p>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

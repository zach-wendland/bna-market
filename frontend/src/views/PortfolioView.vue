<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { usePortfoliosStore, type Portfolio } from '@/stores/portfolios'

const store = usePortfoliosStore()
const showNewPortfolioModal = ref(false)
const selectedPortfolio = ref<Portfolio | null>(null)

const portfolioForm = ref({
  name: '',
  description: '',
  targetReturn: 8.0
})

const propertyForm = ref({
  zpid: '',
  purchasePrice: 0,
  currentValue: 0,
  monthlyRent: 0,
  monthlyExpenses: 0,
  isVacant: false,
  notes: ''
})

onMounted(() => {
  store.fetchPortfolios()
})

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(value)
}

function openNewPortfolioModal() {
  portfolioForm.value = { name: '', description: '', targetReturn: 8.0 }
  showNewPortfolioModal.value = true
}

async function submitPortfolio() {
  try {
    await store.createPortfolio(portfolioForm.value)
    showNewPortfolioModal.value = false
  } catch (e) {
    console.error('Failed to create portfolio:', e)
  }
}

async function selectPortfolio(portfolio: Portfolio) {
  await store.fetchPortfolio(portfolio.id)
  selectedPortfolio.value = store.currentPortfolio
}

function closePortfolioDetail() {
  selectedPortfolio.value = null
  store.clearCurrentPortfolio()
}

async function removePortfolio(portfolioId: string, name: string) {
  if (confirm(`Delete portfolio "${name}" and all its properties?`)) {
    await store.deletePortfolio(portfolioId)
    if (selectedPortfolio.value?.id === portfolioId) {
      selectedPortfolio.value = null
    }
  }
}

const showAddPropertyModal = ref(false)

function openAddPropertyModal() {
  propertyForm.value = {
    zpid: '',
    purchasePrice: 0,
    currentValue: 0,
    monthlyRent: 0,
    monthlyExpenses: 0,
    isVacant: false,
    notes: ''
  }
  showAddPropertyModal.value = true
}

async function submitProperty() {
  if (!selectedPortfolio.value) return
  try {
    await store.addProperty(selectedPortfolio.value.id, propertyForm.value)
    showAddPropertyModal.value = false
    // Refresh the portfolio
    await store.fetchPortfolio(selectedPortfolio.value.id)
    selectedPortfolio.value = store.currentPortfolio
  } catch (e) {
    console.error('Failed to add property:', e)
  }
}
</script>

<template>
  <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <div class="flex items-center justify-between mb-6">
      <h1 class="section-heading flex items-center gap-2">
        <span class="w-1 h-6 bg-gradient-to-b from-primary-500 to-cottage-terracotta rounded-full"></span>
        Investment Portfolios
      </h1>
      <button @click="openNewPortfolioModal" class="btn btn-primary">
        + New Portfolio
      </button>
    </div>

    <!-- Summary Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
      <div class="kpi-card p-4">
        <p class="kpi-label">Total Portfolio Value</p>
        <p class="kpi-value">{{ formatCurrency(store.totalPortfolioValue) }}</p>
      </div>
      <div class="kpi-card p-4">
        <p class="kpi-label">Monthly Cash Flow</p>
        <p :class="['kpi-value', store.totalMonthlyCashFlow >= 0 ? 'text-cottage-sage' : 'text-cyber-magenta']">
          {{ formatCurrency(store.totalMonthlyCashFlow) }}
        </p>
      </div>
      <div class="kpi-card p-4">
        <p class="kpi-label">Total Properties</p>
        <p class="kpi-value">{{ store.totalProperties }}</p>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="store.isLoading && !store.portfolios.length" class="flex justify-center py-12">
      <div class="spinner-cyber w-8 h-8"></div>
    </div>

    <!-- Portfolio List -->
    <div v-else-if="!selectedPortfolio" class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div v-if="store.portfolios.length === 0" class="col-span-full card p-8 text-center">
        <p class="text-cottage-forest mb-4">No portfolios yet. Create one to track your investments.</p>
        <button @click="openNewPortfolioModal" class="btn btn-primary">Create First Portfolio</button>
      </div>

      <div
        v-for="portfolio in store.sortedPortfolios"
        :key="portfolio.id"
        @click="selectPortfolio(portfolio)"
        class="card p-4 cursor-pointer hover:shadow-glow-violet transition-all"
      >
        <div class="flex items-start justify-between mb-3">
          <h3 class="font-semibold text-cyber-navy">{{ portfolio.name }}</h3>
          <button
            @click.stop="removePortfolio(portfolio.id, portfolio.name)"
            class="text-cyber-magenta hover:underline text-xs"
          >
            Delete
          </button>
        </div>
        <p v-if="portfolio.description" class="text-sm text-cottage-forest mb-3">{{ portfolio.description }}</p>

        <div class="grid grid-cols-2 gap-2 text-sm">
          <div>
            <p class="text-cottage-wheat">Properties</p>
            <p class="font-semibold text-cyber-navy">{{ portfolio.propertyCount }}</p>
          </div>
          <div>
            <p class="text-cottage-wheat">Value</p>
            <p class="font-semibold text-cyber-navy">{{ formatCurrency(portfolio.totalValue) }}</p>
          </div>
          <div>
            <p class="text-cottage-wheat">Cash Flow</p>
            <p :class="['font-semibold', portfolio.monthlyCashFlow >= 0 ? 'text-cottage-sage' : 'text-cyber-magenta']">
              {{ formatCurrency(portfolio.monthlyCashFlow) }}/mo
            </p>
          </div>
          <div>
            <p class="text-cottage-wheat">Vacant</p>
            <p :class="['font-semibold', portfolio.vacantCount > 0 ? 'text-cyber-magenta' : 'text-cottage-sage']">
              {{ portfolio.vacantCount }}
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Portfolio Detail View -->
    <div v-else class="space-y-6">
      <div class="flex items-center gap-4">
        <button @click="closePortfolioDetail" class="btn btn-ghost">
          &larr; Back
        </button>
        <h2 class="text-xl font-semibold text-cyber-navy">{{ selectedPortfolio.name }}</h2>
      </div>

      <!-- Portfolio Stats -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div class="kpi-card p-3">
          <p class="kpi-label text-xs">Total Value</p>
          <p class="kpi-value text-lg">{{ formatCurrency(selectedPortfolio.totalValue) }}</p>
        </div>
        <div class="kpi-card p-3">
          <p class="kpi-label text-xs">Monthly Rent</p>
          <p class="kpi-value text-lg">{{ formatCurrency(selectedPortfolio.totalRent) }}</p>
        </div>
        <div class="kpi-card p-3">
          <p class="kpi-label text-xs">Monthly Expenses</p>
          <p class="kpi-value text-lg">{{ formatCurrency(selectedPortfolio.totalExpenses) }}</p>
        </div>
        <div class="kpi-card p-3">
          <p class="kpi-label text-xs">Cash Flow</p>
          <p :class="['kpi-value text-lg', selectedPortfolio.monthlyCashFlow >= 0 ? 'text-cottage-sage' : 'text-cyber-magenta']">
            {{ formatCurrency(selectedPortfolio.monthlyCashFlow) }}
          </p>
        </div>
      </div>

      <!-- Properties in Portfolio -->
      <div>
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-medium text-cyber-navy">Properties ({{ selectedPortfolio.properties?.length || 0 }})</h3>
          <button @click="openAddPropertyModal" class="btn btn-secondary text-sm">
            + Add Property
          </button>
        </div>

        <div v-if="!selectedPortfolio.properties?.length" class="card p-6 text-center text-cottage-forest">
          No properties in this portfolio yet.
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="prop in selectedPortfolio.properties"
            :key="prop.id"
            class="card p-4"
          >
            <div class="flex items-start justify-between">
              <div>
                <p class="font-mono text-sm text-cyber-navy mb-1">ZPID: {{ prop.zpid }}</p>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                  <div>
                    <p class="text-cottage-wheat">Purchase</p>
                    <p class="font-medium">{{ prop.purchasePrice ? formatCurrency(prop.purchasePrice) : '-' }}</p>
                  </div>
                  <div>
                    <p class="text-cottage-wheat">Current Value</p>
                    <p class="font-medium">{{ prop.currentValue ? formatCurrency(prop.currentValue) : '-' }}</p>
                  </div>
                  <div>
                    <p class="text-cottage-wheat">Rent</p>
                    <p class="font-medium">{{ prop.monthlyRent ? formatCurrency(prop.monthlyRent) : '-' }}/mo</p>
                  </div>
                  <div>
                    <p class="text-cottage-wheat">Status</p>
                    <p :class="['font-medium', prop.isVacant ? 'text-cyber-magenta' : 'text-cottage-sage']">
                      {{ prop.isVacant ? 'Vacant' : 'Occupied' }}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- New Portfolio Modal -->
    <div
      v-if="showNewPortfolioModal"
      class="fixed inset-0 bg-cyber-navy/50 flex items-center justify-center z-50"
      @click.self="showNewPortfolioModal = false"
    >
      <div class="card p-6 w-full max-w-md mx-4">
        <h2 class="text-lg font-semibold text-cyber-navy mb-4">New Portfolio</h2>
        <form @submit.prevent="submitPortfolio" class="space-y-4">
          <div>
            <label class="label">Portfolio Name</label>
            <input v-model="portfolioForm.name" type="text" class="input" placeholder="e.g., Nashville Rentals" required />
          </div>
          <div>
            <label class="label">Description</label>
            <textarea v-model="portfolioForm.description" class="input" rows="2" placeholder="Portfolio strategy..."></textarea>
          </div>
          <div>
            <label class="label">Target Return (%)</label>
            <input v-model.number="portfolioForm.targetReturn" type="number" class="input" min="0" max="100" step="0.5" />
          </div>
          <div class="flex gap-3 justify-end">
            <button type="button" @click="showNewPortfolioModal = false" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="store.isLoading">
              {{ store.isLoading ? 'Creating...' : 'Create Portfolio' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Add Property Modal -->
    <div
      v-if="showAddPropertyModal"
      class="fixed inset-0 bg-cyber-navy/50 flex items-center justify-center z-50"
      @click.self="showAddPropertyModal = false"
    >
      <div class="card p-6 w-full max-w-md mx-4 max-h-[90vh] overflow-y-auto">
        <h2 class="text-lg font-semibold text-cyber-navy mb-4">Add Property to Portfolio</h2>
        <form @submit.prevent="submitProperty" class="space-y-4">
          <div>
            <label class="label">Property ZPID</label>
            <input v-model="propertyForm.zpid" type="text" class="input" required />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label">Purchase Price</label>
              <input v-model.number="propertyForm.purchasePrice" type="number" class="input" min="0" />
            </div>
            <div>
              <label class="label">Current Value</label>
              <input v-model.number="propertyForm.currentValue" type="number" class="input" min="0" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label">Monthly Rent</label>
              <input v-model.number="propertyForm.monthlyRent" type="number" class="input" min="0" />
            </div>
            <div>
              <label class="label">Monthly Expenses</label>
              <input v-model.number="propertyForm.monthlyExpenses" type="number" class="input" min="0" />
            </div>
          </div>
          <div class="flex items-center gap-2">
            <input v-model="propertyForm.isVacant" type="checkbox" id="isVacant" class="w-4 h-4" />
            <label for="isVacant" class="text-sm text-cottage-bark">Currently Vacant</label>
          </div>
          <div>
            <label class="label">Notes</label>
            <textarea v-model="propertyForm.notes" class="input" rows="2"></textarea>
          </div>
          <div class="flex gap-3 justify-end">
            <button type="button" @click="showAddPropertyModal = false" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="store.isLoading">
              {{ store.isLoading ? 'Adding...' : 'Add Property' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </main>
</template>

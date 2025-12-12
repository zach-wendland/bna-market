import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/client'

export interface PortfolioProperty {
  id: string
  zpid: string
  purchasePrice?: number
  purchaseDate?: string
  currentValue?: number
  monthlyRent?: number
  monthlyExpenses?: number
  isVacant: boolean
  leaseEndDate?: string
  notes?: string
  createdAt: string
  updatedAt: string
}

export interface Portfolio {
  id: string
  name: string
  description?: string
  targetReturn?: number
  propertyCount: number
  totalValue: number
  totalRent: number
  totalExpenses: number
  monthlyCashFlow: number
  vacantCount: number
  properties?: PortfolioProperty[]
  createdAt: string
  updatedAt: string
}

export const usePortfoliosStore = defineStore('portfolios', () => {
  // State
  const portfolios = ref<Portfolio[]>([])
  const currentPortfolio = ref<Portfolio | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const totalPortfolioValue = computed(() =>
    portfolios.value.reduce((sum, p) => sum + (p.totalValue || 0), 0)
  )

  const totalMonthlyCashFlow = computed(() =>
    portfolios.value.reduce((sum, p) => sum + (p.monthlyCashFlow || 0), 0)
  )

  const totalProperties = computed(() =>
    portfolios.value.reduce((sum, p) => sum + (p.propertyCount || 0), 0)
  )

  const sortedPortfolios = computed(() =>
    [...portfolios.value].sort((a, b) =>
      new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    )
  )

  // Actions - Portfolios
  async function fetchPortfolios() {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get('/crm/portfolios')
      portfolios.value = response.data.portfolios
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to fetch portfolios'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function fetchPortfolio(portfolioId: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get(`/crm/portfolios/${portfolioId}`)
      currentPortfolio.value = response.data
      return response.data
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to fetch portfolio'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function createPortfolio(portfolio: {
    name: string
    description?: string
    targetReturn?: number
  }) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post('/crm/portfolios', portfolio)
      portfolios.value.unshift(response.data)
      return response.data
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to create portfolio'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function updatePortfolio(portfolioId: string, updates: {
    name?: string
    description?: string
    targetReturn?: number
  }) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.put(`/crm/portfolios/${portfolioId}`, updates)
      const index = portfolios.value.findIndex(p => p.id === portfolioId)
      if (index !== -1) {
        portfolios.value[index] = { ...portfolios.value[index], ...response.data }
      }
      if (currentPortfolio.value?.id === portfolioId) {
        currentPortfolio.value = { ...currentPortfolio.value, ...response.data }
      }
      return response.data
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to update portfolio'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function deletePortfolio(portfolioId: string) {
    isLoading.value = true
    error.value = null
    try {
      await api.delete(`/crm/portfolios/${portfolioId}`)
      portfolios.value = portfolios.value.filter(p => p.id !== portfolioId)
      if (currentPortfolio.value?.id === portfolioId) {
        currentPortfolio.value = null
      }
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to delete portfolio'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  // Actions - Portfolio Properties
  async function addProperty(portfolioId: string, property: {
    zpid: string
    purchasePrice?: number
    purchaseDate?: string
    currentValue?: number
    monthlyRent?: number
    monthlyExpenses?: number
    isVacant?: boolean
    leaseEndDate?: string
    notes?: string
  }) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post(
        `/crm/portfolios/${portfolioId}/properties`,
        property
      )
      if (currentPortfolio.value?.id === portfolioId && currentPortfolio.value.properties) {
        currentPortfolio.value.properties.unshift(response.data)
        currentPortfolio.value.propertyCount++
      }
      // Update portfolio summary in list
      const portfolio = portfolios.value.find(p => p.id === portfolioId)
      if (portfolio) {
        portfolio.propertyCount++
        if (property.currentValue) portfolio.totalValue += property.currentValue
        if (property.monthlyRent) portfolio.totalRent += property.monthlyRent
        if (property.monthlyExpenses) portfolio.totalExpenses += property.monthlyExpenses
        portfolio.monthlyCashFlow = portfolio.totalRent - portfolio.totalExpenses
      }
      return response.data
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to add property'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function updateProperty(portfolioId: string, propertyId: string, updates: Partial<PortfolioProperty>) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.put(
        `/crm/portfolios/${portfolioId}/properties/${propertyId}`,
        updates
      )
      if (currentPortfolio.value?.id === portfolioId && currentPortfolio.value.properties) {
        const index = currentPortfolio.value.properties.findIndex(p => p.id === propertyId)
        if (index !== -1) {
          currentPortfolio.value.properties[index] = {
            ...currentPortfolio.value.properties[index],
            ...response.data
          }
        }
      }
      return response.data
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to update property'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function removeProperty(portfolioId: string, propertyId: string) {
    isLoading.value = true
    error.value = null
    try {
      await api.delete(`/crm/portfolios/${portfolioId}/properties/${propertyId}`)
      if (currentPortfolio.value?.id === portfolioId && currentPortfolio.value.properties) {
        currentPortfolio.value.properties = currentPortfolio.value.properties.filter(
          p => p.id !== propertyId
        )
        currentPortfolio.value.propertyCount--
      }
      const portfolio = portfolios.value.find(p => p.id === portfolioId)
      if (portfolio) {
        portfolio.propertyCount--
      }
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to remove property'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  function clearCurrentPortfolio() {
    currentPortfolio.value = null
  }

  return {
    // State
    portfolios,
    currentPortfolio,
    isLoading,
    error,
    // Computed
    totalPortfolioValue,
    totalMonthlyCashFlow,
    totalProperties,
    sortedPortfolios,
    // Actions - Portfolios
    fetchPortfolios,
    fetchPortfolio,
    createPortfolio,
    updatePortfolio,
    deletePortfolio,
    // Actions - Properties
    addProperty,
    updateProperty,
    removeProperty,
    clearCurrentPortfolio
  }
})

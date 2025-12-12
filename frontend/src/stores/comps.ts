import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/client'

export interface PropertyComp {
  id: string
  name: string
  subjectZpid: string
  compZpids: string[]
  filters?: {
    maxDistance?: number
    maxPriceDiff?: number
    sameType?: boolean
  }
  notes?: string
  compCount: number
  createdAt: string
  updatedAt: string
}

export const useCompsStore = defineStore('comps', () => {
  // State
  const comps = ref<PropertyComp[]>([])
  const currentComp = ref<PropertyComp | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const sortedComps = computed(() =>
    [...comps.value].sort((a, b) =>
      new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    )
  )

  // Actions
  async function fetchComps() {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get('/crm/comps')
      comps.value = response.data.comps
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to fetch comps'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function fetchComp(compId: string) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get(`/crm/comps/${compId}`)
      currentComp.value = response.data
      return response.data
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to fetch comp'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function createComp(comp: {
    name: string
    subjectZpid: string
    compZpids: string[]
    filters?: object
    notes?: string
  }) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post('/crm/comps', comp)
      comps.value.unshift(response.data)
      return response.data
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to create comp'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function deleteComp(compId: string) {
    isLoading.value = true
    error.value = null
    try {
      await api.delete(`/crm/comps/${compId}`)
      comps.value = comps.value.filter(c => c.id !== compId)
      if (currentComp.value?.id === compId) {
        currentComp.value = null
      }
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to delete comp'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  function clearCurrentComp() {
    currentComp.value = null
  }

  return {
    // State
    comps,
    currentComp,
    isLoading,
    error,
    // Computed
    sortedComps,
    // Actions
    fetchComps,
    fetchComp,
    createComp,
    deleteComp,
    clearCurrentComp
  }
})

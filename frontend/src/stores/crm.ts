import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api/client'

export interface Lead {
  id: string
  propertyZpid: string
  name: string
  email: string
  phone?: string
  message?: string
  status: 'new' | 'contacted' | 'qualified' | 'converted' | 'lost'
  assignedTo?: string
  tags: string[]
  nextFollowUpDate?: string
  notes?: string
  createdAt: string
  updatedAt: string
}

export interface SearchAlert {
  id: string
  savedSearchId: string
  alertType: 'email' | 'sms' | 'both'
  enabled: boolean
  frequency: 'instant' | 'daily' | 'weekly'
  lastSentAt?: string
  createdAt: string
  updatedAt: string
  searchName?: string
}

export const useCrmStore = defineStore('crm', () => {
  // State
  const leads = ref<Lead[]>([])
  const alerts = ref<SearchAlert[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const newLeads = computed(() => leads.value.filter(l => l.status === 'new'))
  const activeLeads = computed(() => leads.value.filter(l => !['converted', 'lost'].includes(l.status)))
  const enabledAlerts = computed(() => alerts.value.filter(a => a.enabled))

  const leadsByStatus = computed(() => {
    const grouped: Record<string, Lead[]> = {
      new: [],
      contacted: [],
      qualified: [],
      converted: [],
      lost: []
    }
    leads.value.forEach(lead => {
      const group = grouped[lead.status]
      if (group) {
        group.push(lead)
      }
    })
    return grouped
  })

  // Actions - Leads
  async function fetchLeads(filters?: { status?: string; tag?: string }) {
    isLoading.value = true
    error.value = null
    try {
      const params = new URLSearchParams()
      if (filters?.status) params.append('status', filters.status)
      if (filters?.tag) params.append('tag', filters.tag)

      const response = await api.get(`/crm/leads?${params}`)
      leads.value = response.data.leads
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to fetch leads'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function createLead(lead: Omit<Lead, 'id' | 'status' | 'createdAt' | 'updatedAt'>) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post('/crm/leads', lead)
      leads.value.unshift(response.data)
      return response.data
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to create lead'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function updateLead(leadId: string, updates: Partial<Lead>) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.put(`/crm/leads/${leadId}`, updates)
      const index = leads.value.findIndex(l => l.id === leadId)
      if (index !== -1) {
        leads.value[index] = { ...leads.value[index], ...response.data }
      }
      return response.data
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to update lead'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function deleteLead(leadId: string) {
    isLoading.value = true
    error.value = null
    try {
      await api.delete(`/crm/leads/${leadId}`)
      leads.value = leads.value.filter(l => l.id !== leadId)
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to delete lead'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  // Actions - Alerts
  async function fetchAlerts() {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.get('/crm/alerts')
      alerts.value = response.data.alerts
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to fetch alerts'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function createAlert(alert: {
    savedSearchId: string
    alertType: 'email' | 'sms' | 'both'
    frequency?: 'instant' | 'daily' | 'weekly'
  }) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.post('/crm/alerts', alert)
      alerts.value.unshift(response.data)
      return response.data
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to create alert'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function updateAlert(alertId: string, updates: { enabled?: boolean; frequency?: string }) {
    isLoading.value = true
    error.value = null
    try {
      const response = await api.put(`/crm/alerts/${alertId}`, updates)
      const index = alerts.value.findIndex(a => a.id === alertId)
      if (index !== -1) {
        alerts.value[index] = { ...alerts.value[index], ...response.data }
      }
      return response.data
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to update alert'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  async function deleteAlert(alertId: string) {
    isLoading.value = true
    error.value = null
    try {
      await api.delete(`/crm/alerts/${alertId}`)
      alerts.value = alerts.value.filter(a => a.id !== alertId)
    } catch (e: any) {
      error.value = e.response?.data?.error || 'Failed to delete alert'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  return {
    // State
    leads,
    alerts,
    isLoading,
    error,
    // Computed
    newLeads,
    activeLeads,
    enabledAlerts,
    leadsByStatus,
    // Actions - Leads
    fetchLeads,
    createLead,
    updateLead,
    deleteLead,
    // Actions - Alerts
    fetchAlerts,
    createAlert,
    updateAlert,
    deleteAlert
  }
})

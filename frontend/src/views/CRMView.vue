<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useCrmStore, type Lead } from '@/stores/crm'

const store = useCrmStore()
const activeTab = ref<'leads' | 'alerts'>('leads')
const showLeadModal = ref(false)
const editingLead = ref<Lead | null>(null)

// Lead form
const leadForm = ref({
  propertyZpid: '',
  name: '',
  email: '',
  phone: '',
  message: '',
  tags: [] as string[]
})

onMounted(() => {
  store.fetchLeads()
  store.fetchAlerts()
})

function openNewLeadModal() {
  editingLead.value = null
  leadForm.value = { propertyZpid: '', name: '', email: '', phone: '', message: '', tags: [] }
  showLeadModal.value = true
}

async function submitLead() {
  try {
    await store.createLead(leadForm.value)
    showLeadModal.value = false
  } catch (e) {
    console.error('Failed to create lead:', e)
  }
}

async function updateLeadStatus(lead: Lead, status: Lead['status']) {
  try {
    await store.updateLead(lead.id, { status })
  } catch (e) {
    console.error('Failed to update lead:', e)
  }
}

async function removeLead(lead: Lead) {
  if (confirm(`Delete lead "${lead.name}"?`)) {
    await store.deleteLead(lead.id)
  }
}

function getStatusColor(status: string) {
  switch (status) {
    case 'new': return 'bg-cyber-cyan/20 text-cyber-cyan'
    case 'contacted': return 'bg-cottage-sage/20 text-cottage-sage'
    case 'qualified': return 'bg-primary-500/20 text-primary-500'
    case 'converted': return 'bg-cottage-sage/30 text-cottage-forest'
    case 'lost': return 'bg-cyber-magenta/20 text-cyber-magenta'
    default: return 'bg-cottage-sand text-cottage-bark'
  }
}
</script>

<template>
  <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <div class="flex items-center justify-between mb-6">
      <h1 class="section-heading flex items-center gap-2">
        <span class="w-1 h-6 bg-gradient-to-b from-cyber-magenta to-primary-500 rounded-full"></span>
        CRM Dashboard
      </h1>
      <button @click="openNewLeadModal" class="btn btn-primary">
        + New Lead
      </button>
    </div>

    <!-- Tab Navigation -->
    <div class="flex gap-2 mb-6 border-b border-cottage-sand pb-2">
      <button
        @click="activeTab = 'leads'"
        :class="[
          'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors',
          activeTab === 'leads'
            ? 'bg-gradient-to-r from-primary-500/10 to-cyber-cyan/10 text-primary-600 border-b-2 border-primary-500'
            : 'text-cottage-forest hover:text-cyber-navy'
        ]"
      >
        Leads ({{ store.leads.length }})
      </button>
      <button
        @click="activeTab = 'alerts'"
        :class="[
          'px-4 py-2 text-sm font-medium rounded-t-lg transition-colors',
          activeTab === 'alerts'
            ? 'bg-gradient-to-r from-primary-500/10 to-cyber-cyan/10 text-primary-600 border-b-2 border-primary-500'
            : 'text-cottage-forest hover:text-cyber-navy'
        ]"
      >
        Search Alerts ({{ store.enabledAlerts.length }})
      </button>
    </div>

    <!-- Loading -->
    <div v-if="store.isLoading" class="flex justify-center py-12">
      <div class="spinner-cyber w-8 h-8"></div>
    </div>

    <!-- Leads Tab -->
    <div v-else-if="activeTab === 'leads'">
      <div v-if="store.leads.length === 0" class="card p-8 text-center">
        <p class="text-cottage-forest mb-4">No leads yet. Start capturing leads from property listings.</p>
        <button @click="openNewLeadModal" class="btn btn-primary">Create First Lead</button>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="lead in store.leads"
          :key="lead.id"
          class="card p-4 hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex items-center gap-2 mb-1">
                <h3 class="font-medium text-cyber-navy truncate">{{ lead.name }}</h3>
                <span :class="['px-2 py-0.5 text-xs rounded-full', getStatusColor(lead.status)]">
                  {{ lead.status }}
                </span>
              </div>
              <p class="text-sm text-cottage-forest">{{ lead.email }}</p>
              <p v-if="lead.phone" class="text-sm text-cottage-forest">{{ lead.phone }}</p>
              <p v-if="lead.message" class="text-sm text-cottage-bark mt-2 line-clamp-2">{{ lead.message }}</p>
              <p class="text-xs text-cottage-wheat mt-2">Property: {{ lead.propertyZpid }}</p>
            </div>

            <div class="flex flex-col gap-1">
              <select
                :value="lead.status"
                @change="updateLeadStatus(lead, ($event.target as HTMLSelectElement).value as Lead['status'])"
                class="select text-xs py-1"
              >
                <option value="new">New</option>
                <option value="contacted">Contacted</option>
                <option value="qualified">Qualified</option>
                <option value="converted">Converted</option>
                <option value="lost">Lost</option>
              </select>
              <button
                @click="removeLead(lead)"
                class="text-xs text-cyber-magenta hover:underline"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Alerts Tab -->
    <div v-else-if="activeTab === 'alerts'">
      <div v-if="store.alerts.length === 0" class="card p-8 text-center">
        <p class="text-cottage-forest mb-4">No search alerts configured. Save a search and enable alerts to get notified.</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="alert in store.alerts"
          :key="alert.id"
          class="card p-4 flex items-center justify-between"
        >
          <div>
            <h3 class="font-medium text-cyber-navy">{{ alert.searchName || 'Unnamed Search' }}</h3>
            <p class="text-sm text-cottage-forest">
              {{ alert.alertType }} - {{ alert.frequency }}
            </p>
          </div>
          <label class="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              :checked="alert.enabled"
              @change="store.updateAlert(alert.id, { enabled: !alert.enabled })"
              class="sr-only peer"
            />
            <div class="w-11 h-6 bg-cottage-sand rounded-full peer peer-checked:bg-primary-500 transition-colors"></div>
          </label>
        </div>
      </div>
    </div>

    <!-- Lead Modal -->
    <div
      v-if="showLeadModal"
      class="fixed inset-0 bg-cyber-navy/50 flex items-center justify-center z-50"
      @click.self="showLeadModal = false"
    >
      <div class="card p-6 w-full max-w-md mx-4">
        <h2 class="text-lg font-semibold text-cyber-navy mb-4">New Lead</h2>
        <form @submit.prevent="submitLead" class="space-y-4">
          <div>
            <label class="label">Property ZPID</label>
            <input v-model="leadForm.propertyZpid" type="text" class="input" required />
          </div>
          <div>
            <label class="label">Name</label>
            <input v-model="leadForm.name" type="text" class="input" required />
          </div>
          <div>
            <label class="label">Email</label>
            <input v-model="leadForm.email" type="email" class="input" required />
          </div>
          <div>
            <label class="label">Phone</label>
            <input v-model="leadForm.phone" type="tel" class="input" />
          </div>
          <div>
            <label class="label">Message</label>
            <textarea v-model="leadForm.message" class="input" rows="3"></textarea>
          </div>
          <div class="flex gap-3 justify-end">
            <button type="button" @click="showLeadModal = false" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="store.isLoading">
              {{ store.isLoading ? 'Saving...' : 'Save Lead' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </main>
</template>

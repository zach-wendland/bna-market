<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useCompsStore } from '@/stores/comps'

const store = useCompsStore()
const showNewCompModal = ref(false)

const compForm = ref({
  name: '',
  subjectZpid: '',
  compZpids: '',
  notes: ''
})

onMounted(() => {
  store.fetchComps()
})

function openNewCompModal() {
  compForm.value = { name: '', subjectZpid: '', compZpids: '', notes: '' }
  showNewCompModal.value = true
}

async function submitComp() {
  try {
    const compZpidsArray = compForm.value.compZpids.split(',').map(s => s.trim()).filter(Boolean)
    await store.createComp({
      name: compForm.value.name,
      subjectZpid: compForm.value.subjectZpid,
      compZpids: compZpidsArray,
      notes: compForm.value.notes || undefined
    })
    showNewCompModal.value = false
  } catch (e) {
    console.error('Failed to create comp:', e)
  }
}

async function removeComp(compId: string, name: string) {
  if (confirm(`Delete comparison "${name}"?`)) {
    await store.deleteComp(compId)
  }
}
</script>

<template>
  <main class="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <div class="flex items-center justify-between mb-6">
      <h1 class="section-heading flex items-center gap-2">
        <span class="w-1 h-6 bg-gradient-to-b from-cyber-cyan to-cottage-sage rounded-full"></span>
        Property Comparisons
      </h1>
      <button @click="openNewCompModal" class="btn btn-primary">
        + New Comparison
      </button>
    </div>

    <!-- Loading -->
    <div v-if="store.isLoading" class="flex justify-center py-12">
      <div class="spinner-cyber w-8 h-8"></div>
    </div>

    <!-- Empty State -->
    <div v-else-if="store.comps.length === 0" class="card p-8 text-center">
      <div class="w-16 h-16 bg-cottage-sand rounded-full mx-auto mb-4 flex items-center justify-center">
        <svg class="w-8 h-8 text-cottage-forest" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      </div>
      <p class="text-cottage-forest mb-4">No property comparisons yet. Create one to compare similar properties.</p>
      <button @click="openNewCompModal" class="btn btn-primary">Create First Comparison</button>
    </div>

    <!-- Comp List -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="comp in store.sortedComps"
        :key="comp.id"
        class="card p-4 hover:shadow-glow-cyan transition-all"
      >
        <div class="flex items-start justify-between mb-2">
          <h3 class="font-semibold text-cyber-navy">{{ comp.name }}</h3>
          <button
            @click="removeComp(comp.id, comp.name)"
            class="text-cyber-magenta hover:underline text-xs"
          >
            Delete
          </button>
        </div>
        <p class="text-sm text-cottage-forest mb-2">
          Subject: <span class="font-mono text-cyber-navy">{{ comp.subjectZpid }}</span>
        </p>
        <p class="text-sm text-cottage-forest">
          <span class="font-medium">{{ comp.compCount }}</span> comparable properties
        </p>
        <p v-if="comp.notes" class="text-xs text-cottage-bark mt-2 line-clamp-2">{{ comp.notes }}</p>
        <p class="text-xs text-cottage-wheat mt-3">
          Updated {{ new Date(comp.updatedAt).toLocaleDateString() }}
        </p>
      </div>
    </div>

    <!-- New Comp Modal -->
    <div
      v-if="showNewCompModal"
      class="fixed inset-0 bg-cyber-navy/50 flex items-center justify-center z-50"
      @click.self="showNewCompModal = false"
    >
      <div class="card p-6 w-full max-w-md mx-4">
        <h2 class="text-lg font-semibold text-cyber-navy mb-4">New Property Comparison</h2>
        <form @submit.prevent="submitComp" class="space-y-4">
          <div>
            <label class="label">Comparison Name</label>
            <input v-model="compForm.name" type="text" class="input" placeholder="e.g., Downtown Condos" required />
          </div>
          <div>
            <label class="label">Subject Property ZPID</label>
            <input v-model="compForm.subjectZpid" type="text" class="input" placeholder="Main property to compare" required />
          </div>
          <div>
            <label class="label">Comparable ZPIDs</label>
            <input
              v-model="compForm.compZpids"
              type="text"
              class="input"
              placeholder="Comma-separated: 123, 456, 789"
              required
            />
            <p class="text-xs text-cottage-forest mt-1">Enter ZPIDs of similar properties to compare</p>
          </div>
          <div>
            <label class="label">Notes (optional)</label>
            <textarea v-model="compForm.notes" class="input" rows="2" placeholder="Analysis notes..."></textarea>
          </div>
          <div class="flex gap-3 justify-end">
            <button type="button" @click="showNewCompModal = false" class="btn btn-secondary">Cancel</button>
            <button type="submit" class="btn btn-primary" :disabled="store.isLoading">
              {{ store.isLoading ? 'Creating...' : 'Create Comparison' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </main>
</template>

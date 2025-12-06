<script setup lang="ts">
import { useDashboardStore } from '@/stores/dashboard';
import type { ViewMode } from '@/types';

const store = useDashboardStore();

const views: { mode: ViewMode; label: string; icon: string }[] = [
  { mode: 'table', label: 'Table', icon: 'table' },
  { mode: 'cards', label: 'Cards', icon: 'cards' },
  { mode: 'map', label: 'Map', icon: 'map' }
];

function setView(mode: ViewMode) {
  store.setViewMode(mode);
}
</script>

<template>
  <div class="inline-flex items-center gap-1 bg-gray-100 p-1 rounded-lg">
    <button
      v-for="view in views"
      :key="view.mode"
      @click="setView(view.mode)"
      :class="[
        'p-2 rounded-md transition-all duration-200',
        store.viewMode === view.mode
          ? 'bg-white shadow-sm text-primary-600'
          : 'text-gray-500 hover:text-gray-700'
      ]"
      :aria-label="`Switch to ${view.label} view`"
      :aria-pressed="store.viewMode === view.mode"
    >
      <!-- Table icon -->
      <svg v-if="view.icon === 'table'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
      </svg>

      <!-- Cards icon -->
      <svg v-else-if="view.icon === 'cards'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
      </svg>

      <!-- Map icon -->
      <svg v-else-if="view.icon === 'map'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
      </svg>
    </button>
  </div>
</template>

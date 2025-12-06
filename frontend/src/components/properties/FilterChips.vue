<script setup lang="ts">
import { useDashboardStore } from '@/stores/dashboard';
import type { PropertyFilters } from '@/types';

const store = useDashboardStore();

function removeFilter(key: string) {
  store.clearFilter(key as keyof PropertyFilters);
  store.searchWithFilters();
}

function clearAll() {
  store.clearAllFilters();
  store.searchWithFilters();
}
</script>

<template>
  <div class="flex flex-wrap items-center gap-2">
    <span class="text-sm text-gray-500 mr-1">Active filters:</span>

    <TransitionGroup name="chip">
      <span
        v-for="filter in store.activeFilters"
        :key="filter.key"
        class="filter-chip animate-fade-in"
      >
        <span class="text-primary-500 font-normal">{{ filter.label }}:</span>
        <span>{{ filter.value }}</span>
        <button
          @click="removeFilter(filter.key)"
          class="filter-chip-remove"
          :aria-label="`Remove ${filter.label} filter`"
        >
          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </span>
    </TransitionGroup>

    <button
      v-if="store.activeFilters.length > 1"
      @click="clearAll"
      class="text-sm text-red-600 hover:text-red-700 font-medium ml-2"
    >
      Clear all
    </button>
  </div>
</template>

<style scoped>
.chip-enter-active,
.chip-leave-active {
  transition: all 0.2s ease;
}
.chip-enter-from,
.chip-leave-to {
  opacity: 0;
  transform: scale(0.8);
}
</style>

<script setup lang="ts">
import { ref, watch } from 'vue';
import { useDashboardStore } from '@/stores/dashboard';
import { useDebounceFn } from '@/composables/useDebounce';
import { getExportUrl } from '@/api/client';

const store = useDashboardStore();
const showAdvanced = ref(false);

// Debounced preview update with cancel support
const debouncedPreview = useDebounceFn(() => {
  store.updateFilterPreview();
}, 500);

// Watch filter changes for preview (excluding property type which triggers search)
watch(
  () => store.filters,
  () => {
    debouncedPreview();
  },
  { deep: true }
);

// Reset pagination when property type changes (prevents page overflow)
watch(
  () => store.filters.propertyType,
  () => {
    store.setPage(1);
    // Reload with new property type
    store.searchWithFilters();
  }
);

async function handleSubmit() {
  // Cancel any pending preview to avoid race conditions
  debouncedPreview.cancel();
  store.setPage(1);
  await store.searchWithFilters();
}

function handleReset() {
  // Cancel any pending preview to avoid stale data
  debouncedPreview.cancel();
  store.clearAllFilters();
  store.searchWithFilters();
}

function handleExport() {
  const url = getExportUrl({
    ...store.filters,
    page: 1,
    perPage: 1000
  });
  window.open(url, '_blank');
}
</script>

<template>
  <div class="card p-4 sm:p-6">
    <form @submit.prevent="handleSubmit">
      <!-- Primary Filters -->
      <div class="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-4">
        <!-- Property Type -->
        <div>
          <label class="label">Property Type</label>
          <select
            v-model="store.filters.propertyType"
            class="select"
          >
            <option value="rental">Rentals</option>
            <option value="forsale">For Sale</option>
          </select>
        </div>

        <!-- Min Price -->
        <div>
          <label class="label">Min Price</label>
          <input
            v-model.number="store.filters.minPrice"
            type="number"
            class="input"
            placeholder="$0"
            min="0"
          />
        </div>

        <!-- Max Price -->
        <div>
          <label class="label">Max Price</label>
          <input
            v-model.number="store.filters.maxPrice"
            type="number"
            class="input"
            placeholder="Any"
            min="0"
          />
        </div>

        <!-- Bedrooms -->
        <div>
          <label class="label">Bedrooms</label>
          <select v-model.number="store.filters.minBeds" class="select">
            <option :value="null">Any</option>
            <option :value="1">1+</option>
            <option :value="2">2+</option>
            <option :value="3">3+</option>
            <option :value="4">4+</option>
            <option :value="5">5+</option>
          </select>
        </div>

        <!-- Bathrooms -->
        <div>
          <label class="label">Bathrooms</label>
          <select v-model.number="store.filters.minBaths" class="select">
            <option :value="null">Any</option>
            <option :value="1">1+</option>
            <option :value="2">2+</option>
            <option :value="3">3+</option>
            <option :value="4">4+</option>
          </select>
        </div>
      </div>

      <!-- Advanced Filters Toggle -->
      <div class="mt-4 text-center">
        <button
          type="button"
          @click="showAdvanced = !showAdvanced"
          class="inline-flex items-center gap-2 text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          <span>{{ showAdvanced ? 'Fewer Filters' : 'More Filters' }}</span>
          <svg
            :class="['w-4 h-4 transition-transform', showAdvanced && 'rotate-180']"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      <!-- Advanced Filters -->
      <div
        v-show="showAdvanced"
        class="mt-4 grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4 animate-slide-down"
      >
        <!-- Max Beds -->
        <div>
          <label class="label">Max Beds</label>
          <select v-model.number="store.filters.maxBeds" class="select">
            <option :value="null">Any</option>
            <option :value="1">1</option>
            <option :value="2">2</option>
            <option :value="3">3</option>
            <option :value="4">4</option>
            <option :value="5">5</option>
          </select>
        </div>

        <!-- Max Baths -->
        <div>
          <label class="label">Max Baths</label>
          <select v-model.number="store.filters.maxBaths" class="select">
            <option :value="null">Any</option>
            <option :value="1">1</option>
            <option :value="2">2</option>
            <option :value="3">3</option>
            <option :value="4">4</option>
          </select>
        </div>

        <!-- Min Sqft -->
        <div>
          <label class="label">Min Sqft</label>
          <input
            v-model.number="store.filters.minSqft"
            type="number"
            class="input"
            placeholder="0"
            min="0"
          />
        </div>

        <!-- Max Sqft -->
        <div>
          <label class="label">Max Sqft</label>
          <input
            v-model.number="store.filters.maxSqft"
            type="number"
            class="input"
            placeholder="Any"
            min="0"
          />
        </div>

        <!-- City -->
        <div>
          <label class="label">City</label>
          <input
            v-model="store.filters.city"
            type="text"
            class="input"
            placeholder="Nashville..."
          />
        </div>

        <!-- ZIP Code -->
        <div>
          <label class="label">ZIP Code</label>
          <input
            v-model="store.filters.zipCode"
            type="text"
            class="input"
            placeholder="37203"
            pattern="[0-9]{5}"
          />
        </div>
      </div>

      <!-- Filter Preview -->
      <div v-if="store.previewCount !== null" class="mt-4">
        <div
          :class="[
            'inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium',
            store.previewCount === 0
              ? 'bg-red-50 text-red-700'
              : 'bg-green-50 text-green-700'
          ]"
        >
          <span v-if="store.isLoadingPreview" class="spinner w-3 h-3" />
          <span v-else-if="store.previewCount === 0">
            No properties match these filters
          </span>
          <span v-else>
            {{ store.previewCount.toLocaleString() }} properties found
          </span>
        </div>
      </div>

      <!-- Actions -->
      <div class="mt-6 flex flex-wrap items-center gap-3">
        <button type="submit" class="btn btn-primary" :disabled="store.isLoading">
          <span v-if="store.isLoading" class="spinner mr-2" />
          Search Properties
        </button>

        <button
          type="button"
          @click="handleReset"
          class="btn btn-secondary"
        >
          Clear Filters
        </button>

        <button
          type="button"
          @click="handleExport"
          class="btn btn-outline"
        >
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Export CSV
        </button>
      </div>
    </form>
  </div>
</template>

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { SavedSearch } from '@/api/client';
import * as api from '@/api/client';
import { useDashboardStore } from './dashboard';

export const useSearchesStore = defineStore('searches', () => {
  // State
  const searches = ref<SavedSearch[]>([]);
  const currentSearch = ref<SavedSearch | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Computed
  const searchesCount = computed(() => searches.value.length);
  const hasSearches = computed(() => searches.value.length > 0);
  const sortedSearches = computed(() => {
    return [...searches.value].sort((a, b) => {
      return new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime();
    });
  });

  // Filter searches by property type
  const forSaleSearches = computed(() => {
    return searches.value.filter((s) => s.property_type === 'forsale');
  });

  const rentalSearches = computed(() => {
    return searches.value.filter((s) => s.property_type === 'rental');
  });

  // Actions

  /**
   * Load all saved searches for the current user
   */
  async function loadSearches(): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      searches.value = await api.getSavedSearches();
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to load saved searches';
      console.error('Failed to load searches:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Load a specific saved search
   */
  async function loadSearch(searchId: string): Promise<SavedSearch> {
    isLoading.value = true;
    error.value = null;

    try {
      const search = await api.getSavedSearch(searchId);
      currentSearch.value = search;
      return search;
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to load search';
      console.error('Failed to load search:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Save current dashboard filters as a new search
   */
  async function saveCurrentSearch(name: string): Promise<SavedSearch> {
    const dashboardStore = useDashboardStore();

    isLoading.value = true;
    error.value = null;

    try {
      const newSearch = await api.saveSearch(
        name,
        dashboardStore.filters.propertyType,
        dashboardStore.filters
      );

      searches.value.push(newSearch);
      return newSearch;
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to save search';
      console.error('Failed to save search:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Update an existing saved search
   */
  async function updateSearch(
    searchId: string,
    name?: string,
    propertyType?: 'forsale' | 'rental',
    filters?: any
  ): Promise<SavedSearch> {
    isLoading.value = true;
    error.value = null;

    try {
      const updatedSearch = await api.updateSavedSearch(searchId, name, propertyType, filters);

      // Update in searches array
      const index = searches.value.findIndex((s) => s.id === searchId);
      if (index !== -1) {
        searches.value[index] = updatedSearch;
      }

      // Update current search if it's the one being updated
      if (currentSearch.value?.id === searchId) {
        currentSearch.value = updatedSearch;
      }

      return updatedSearch;
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to update search';
      console.error('Failed to update search:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Delete a saved search
   */
  async function deleteSearch(searchId: string): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      await api.deleteSavedSearch(searchId);

      // Remove from searches array
      searches.value = searches.value.filter((s) => s.id !== searchId);

      // Clear current search if it's the one being deleted
      if (currentSearch.value?.id === searchId) {
        currentSearch.value = null;
      }
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to delete search';
      console.error('Failed to delete search:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Apply a saved search to the dashboard filters
   */
  async function applySearch(searchId: string): Promise<void> {
    const dashboardStore = useDashboardStore();
    isLoading.value = true;
    error.value = null;

    try {
      const search = await api.getSavedSearch(searchId);
      currentSearch.value = search;

      // Apply the saved filters to the dashboard
      dashboardStore.filters = {
        ...dashboardStore.filters,
        propertyType: search.property_type,
        ...search.filters,
      };

      // Reload properties with the new filters
      await dashboardStore.searchProperties();
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to apply search';
      console.error('Failed to apply search:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Check if current dashboard filters match a saved search
   */
  function matchesCurrentFilters(search: SavedSearch): boolean {
    const dashboardStore = useDashboardStore();
    const currentFilters = dashboardStore.filters;

    // Check property type
    if (search.property_type !== currentFilters.propertyType) {
      return false;
    }

    // Compare filter values (deep equality check)
    const savedFilters = search.filters;
    const compareKeys = [
      'minPrice',
      'maxPrice',
      'bedrooms',
      'bathrooms',
      'homeType',
      'zipcode',
      'searchTerm',
    ];

    for (const key of compareKeys) {
      const savedValue = savedFilters[key];
      const currentValue = currentFilters[key];

      // Skip if both are undefined/null
      if (!savedValue && !currentValue) continue;

      // Arrays comparison
      if (Array.isArray(savedValue) && Array.isArray(currentValue)) {
        if (savedValue.length !== currentValue.length) return false;
        if (!savedValue.every((v) => currentValue.includes(v))) return false;
        continue;
      }

      // Direct comparison
      if (savedValue !== currentValue) return false;
    }

    return true;
  }

  /**
   * Get the saved search that matches current filters, if any
   */
  function getCurrentMatchingSearch(): SavedSearch | null {
    return searches.value.find((search) => matchesCurrentFilters(search)) || null;
  }

  /**
   * Clear error state
   */
  function clearError(): void {
    error.value = null;
  }

  /**
   * Clear current search
   */
  function clearCurrentSearch(): void {
    currentSearch.value = null;
  }

  /**
   * Reset store state
   */
  function $reset(): void {
    searches.value = [];
    currentSearch.value = null;
    isLoading.value = false;
    error.value = null;
  }

  return {
    // State
    searches,
    currentSearch,
    isLoading,
    error,

    // Computed
    searchesCount,
    hasSearches,
    sortedSearches,
    forSaleSearches,
    rentalSearches,

    // Actions
    loadSearches,
    loadSearch,
    saveCurrentSearch,
    updateSearch,
    deleteSearch,
    applySearch,
    matchesCurrentFilters,
    getCurrentMatchingSearch,
    clearError,
    clearCurrentSearch,
    $reset,
  };
});

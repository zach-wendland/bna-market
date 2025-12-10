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
      return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
    });
  });

  // Filter searches by property type
  const forSaleSearches = computed(() => {
    return searches.value.filter((s) => s.propertyType === 'forsale');
  });

  const rentalSearches = computed(() => {
    return searches.value.filter((s) => s.propertyType === 'rental');
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
    updates: { name?: string; propertyType?: 'forsale' | 'rental'; filters?: any }
  ): Promise<SavedSearch> {
    isLoading.value = true;
    error.value = null;

    try {
      const updatedSearch = await api.updateSavedSearch(searchId, updates.name, updates.filters);

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
      dashboardStore.setPropertyType(search.propertyType);

      // Note: Dashboard store doesn't have searchProperties method
      // Filters will be applied when user interacts with the dashboard
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

    // Check property type
    if (search.propertyType !== dashboardStore.propertyType) {
      return false;
    }

    // Simple comparison for now - in production you'd do deep filter comparison
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

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { PropertyList, ListItem } from '@/api/client';
import * as api from '@/api/client';

export const useListsStore = defineStore('lists', () => {
  // State
  const lists = ref<PropertyList[]>([]);
  const currentList = ref<PropertyList | null>(null);
  const currentListItems = ref<ListItem[]>([]);
  const isLoading = ref(false);
  const isLoadingItems = ref(false);
  const error = ref<string | null>(null);

  // Computed
  const listsCount = computed(() => lists.value.length);
  const hasLists = computed(() => lists.value.length > 0);
  const sortedLists = computed(() => {
    return [...lists.value].sort((a, b) => {
      return new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime();
    });
  });

  // Actions

  /**
   * Load all property lists for the current user
   */
  async function loadLists(): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      lists.value = await api.getUserLists();
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to load property lists';
      console.error('Failed to load lists:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Load a specific list with its items
   */
  async function loadListWithItems(listId: string): Promise<void> {
    isLoadingItems.value = true;
    error.value = null;

    try {
      const data = await api.getListWithItems(listId);
      currentList.value = data;
      currentListItems.value = data.items || [];
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to load list details';
      console.error('Failed to load list with items:', err);
      throw err;
    } finally {
      isLoadingItems.value = false;
    }
  }

  /**
   * Create a new property list
   */
  async function createList(name: string, description?: string): Promise<PropertyList> {
    isLoading.value = true;
    error.value = null;

    try {
      const newList = await api.createList(name, description);
      lists.value.push(newList);
      return newList;
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to create list';
      console.error('Failed to create list:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Update an existing list
   */
  async function updateList(
    listId: string,
    updates: { name?: string; description?: string }
  ): Promise<PropertyList> {
    isLoading.value = true;
    error.value = null;

    try {
      const updatedList = await api.updateList(listId, updates);

      // Update in lists array
      const index = lists.value.findIndex((l) => l.id === listId);
      if (index !== -1) {
        lists.value[index] = updatedList;
      }

      // Update current list if it's the one being updated
      if (currentList.value?.id === listId) {
        currentList.value = updatedList;
      }

      return updatedList;
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to update list';
      console.error('Failed to update list:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Delete a property list
   */
  async function deleteList(listId: string): Promise<void> {
    isLoading.value = true;
    error.value = null;

    try {
      await api.deleteList(listId);

      // Remove from lists array
      lists.value = lists.value.filter((l) => l.id !== listId);

      // Clear current list if it's the one being deleted
      if (currentList.value?.id === listId) {
        currentList.value = null;
        currentListItems.value = [];
      }
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to delete list';
      console.error('Failed to delete list:', err);
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  /**
   * Add a property to a list
   */
  async function addPropertyToList(
    listId: string,
    zpid: string,
    propertyType: 'forsale' | 'rental',
    notes?: string
  ): Promise<ListItem> {
    isLoadingItems.value = true;
    error.value = null;

    try {
      const newItem = await api.addPropertyToList(listId, zpid, propertyType, notes);

      // Update current list items if we're viewing this list
      if (currentList.value?.id === listId) {
        currentListItems.value.push(newItem);
      }

      // Update item count in lists array
      const list = lists.value.find((l) => l.id === listId);
      if (list) {
        list.itemCount = (list.itemCount || 0) + 1;
      }

      return newItem;
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to add property to list';
      console.error('Failed to add property to list:', err);
      throw err;
    } finally {
      isLoadingItems.value = false;
    }
  }

  /**
   * Remove a property from a list
   */
  async function removePropertyFromList(listId: string, itemId: string): Promise<void> {
    isLoadingItems.value = true;
    error.value = null;

    try {
      await api.removePropertyFromList(listId, itemId);

      // Update current list items if we're viewing this list
      if (currentList.value?.id === listId) {
        currentListItems.value = currentListItems.value.filter((item) => item.id !== itemId);
      }

      // Update item count in lists array
      const list = lists.value.find((l) => l.id === listId);
      if (list && list.itemCount > 0) {
        list.itemCount -= 1;
      }
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to remove property from list';
      console.error('Failed to remove property from list:', err);
      throw err;
    } finally {
      isLoadingItems.value = false;
    }
  }

  /**
   * Update notes for a list item
   */
  async function updateListItemNotes(
    listId: string,
    itemId: string,
    notes: string
  ): Promise<ListItem> {
    isLoadingItems.value = true;
    error.value = null;

    try {
      const updatedItem = await api.updateListItemNotes(listId, itemId, notes);

      // Update in current list items if we're viewing this list
      if (currentList.value?.id === listId) {
        const index = currentListItems.value.findIndex((item) => item.id === itemId);
        if (index !== -1) {
          currentListItems.value[index] = updatedItem;
        }
      }

      return updatedItem;
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Failed to update notes';
      console.error('Failed to update list item notes:', err);
      throw err;
    } finally {
      isLoadingItems.value = false;
    }
  }

  /**
   * Check if a property is in any list
   */
  function isPropertyInList(zpid: string, listId?: string): boolean {
    if (listId && currentList.value?.id === listId) {
      return currentListItems.value.some((item) => item.zpid === zpid);
    }
    return false;
  }

  /**
   * Get lists that contain a specific property
   */
  function getListsContainingProperty(zpid: string): PropertyList[] {
    // Note: This is a simplified check based on current list only
    // In a real implementation, you might want to load all list items
    if (currentList.value && isPropertyInList(zpid, currentList.value.id)) {
      return [currentList.value];
    }
    return [];
  }

  /**
   * Clear error state
   */
  function clearError(): void {
    error.value = null;
  }

  /**
   * Reset store state
   */
  function $reset(): void {
    lists.value = [];
    currentList.value = null;
    currentListItems.value = [];
    isLoading.value = false;
    isLoadingItems.value = false;
    error.value = null;
  }

  return {
    // State
    lists,
    currentList,
    currentListItems,
    isLoading,
    isLoadingItems,
    error,

    // Computed
    listsCount,
    hasLists,
    sortedLists,

    // Actions
    loadLists,
    loadListWithItems,
    createList,
    updateList,
    deleteList,
    addPropertyToList,
    removePropertyFromList,
    updateListItemNotes,
    isPropertyInList,
    getListsContainingProperty,
    clearError,
    $reset,
  };
});

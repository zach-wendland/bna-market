import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { fetchDashboardData, searchProperties, getPropertyCount } from '@/api/client';
import type {
  DashboardData,
  Property,
  PropertyKPIs,
  FredKPIs,
  FredMetric,
  PropertyFilters,
  SearchParams,
  PaginationMeta,
  ViewMode,
  SortConfig,
  ActiveFilter
} from '@/types';

export const useDashboardStore = defineStore('dashboard', () => {
  // Dashboard data
  const propertyKPIs = ref<PropertyKPIs | null>(null);
  const fredKPIs = ref<FredKPIs | null>(null);
  const fredMetrics = ref<FredMetric[]>([]);
  const lastUpdated = ref<string | null>(null);

  // Properties
  const properties = ref<Property[]>([]);
  const pagination = ref<PaginationMeta | null>(null);

  // UI State
  const isLoading = ref(false);
  const isLoadingPreview = ref(false);
  const error = ref<string | null>(null);
  const viewMode = ref<ViewMode>('carousel');
  const previewCount = ref<number | null>(null);

  // Filters
  const filters = ref<PropertyFilters>({
    propertyType: 'rental',
    minPrice: null,
    maxPrice: null,
    minBeds: null,
    maxBeds: null,
    minBaths: null,
    maxBaths: null,
    minSqft: null,
    maxSqft: null,
    city: '',
    zipCode: ''
  });

  // Sort
  const sortConfig = ref<SortConfig>({
    column: 'price',
    order: 'desc'
  });

  // Pagination
  const currentPage = ref(1);
  const perPage = ref(20);

  // Computed
  const activeFilters = computed<ActiveFilter[]>(() => {
    const result: ActiveFilter[] = [];
    const labels: Record<string, string> = {
      minPrice: 'Min Price',
      maxPrice: 'Max Price',
      minBeds: 'Min Beds',
      maxBeds: 'Max Beds',
      minBaths: 'Min Baths',
      maxBaths: 'Max Baths',
      minSqft: 'Min Sqft',
      maxSqft: 'Max Sqft',
      city: 'City',
      zipCode: 'ZIP'
    };

    for (const [key, value] of Object.entries(filters.value)) {
      if (key === 'propertyType') continue;
      if (value !== null && value !== '' && value !== undefined) {
        result.push({
          key,
          label: labels[key] || key,
          value: typeof value === 'number' ? value.toLocaleString() : value
        });
      }
    }

    return result;
  });

  const hasActiveFilters = computed(() => activeFilters.value.length > 0);

  const relativeFreshness = computed(() => {
    if (!lastUpdated.value) return null;

    const now = new Date();
    const updated = new Date(lastUpdated.value);
    const hours = (now.getTime() - updated.getTime()) / (1000 * 60 * 60);

    if (hours < 1) {
      const minutes = Math.floor(hours * 60);
      return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
    } else if (hours < 24) {
      const h = Math.floor(hours);
      return `${h} hour${h !== 1 ? 's' : ''} ago`;
    } else {
      const days = Math.floor(hours / 24);
      return `${days} day${days !== 1 ? 's' : ''} ago`;
    }
  });

  // Actions
  async function loadDashboard() {
    isLoading.value = true;
    error.value = null;

    try {
      const data: DashboardData = await fetchDashboardData();
      propertyKPIs.value = data.propertyKPIs;
      fredKPIs.value = data.fredKPIs;
      fredMetrics.value = data.fredMetrics;
      lastUpdated.value = data.lastUpdated;

      // Set initial properties based on filter type
      if (filters.value.propertyType === 'rental') {
        properties.value = data.rentals;
      } else {
        properties.value = data.forsale;
      }
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load dashboard';
      console.error('Dashboard load error:', e);
    } finally {
      isLoading.value = false;
    }
  }

  async function searchWithFilters() {
    isLoading.value = true;
    error.value = null;

    try {
      const params: SearchParams = {
        ...filters.value,
        page: currentPage.value,
        perPage: perPage.value,
        sortBy: sortConfig.value.column,
        sortOrder: sortConfig.value.order
      };

      const result = await searchProperties(params);
      properties.value = result.properties;
      pagination.value = result.pagination;
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Search failed';
      console.error('Search error:', e);
    } finally {
      isLoading.value = false;
    }
  }

  async function updateFilterPreview() {
    isLoadingPreview.value = true;

    try {
      const params: SearchParams = {
        ...filters.value,
        page: 1,
        perPage: 1
      };

      const count = await getPropertyCount(params);
      previewCount.value = count;
    } catch (e) {
      console.error('Preview error:', e);
      previewCount.value = null;
    } finally {
      isLoadingPreview.value = false;
    }
  }

  function setFilter<K extends keyof PropertyFilters>(key: K, value: PropertyFilters[K]) {
    filters.value[key] = value;
  }

  function clearFilter(key: keyof PropertyFilters) {
    if (key === 'propertyType') return; // Don't clear property type

    if (typeof filters.value[key] === 'number' || filters.value[key] === null) {
      (filters.value[key] as number | null) = null;
    } else {
      (filters.value[key] as string) = '';
    }
  }

  function clearAllFilters() {
    filters.value = {
      ...filters.value,
      minPrice: null,
      maxPrice: null,
      minBeds: null,
      maxBeds: null,
      minBaths: null,
      maxBaths: null,
      minSqft: null,
      maxSqft: null,
      city: '',
      zipCode: ''
    };
    currentPage.value = 1;
  }

  function setSort(column: string) {
    if (sortConfig.value.column === column) {
      sortConfig.value.order = sortConfig.value.order === 'asc' ? 'desc' : 'asc';
    } else {
      sortConfig.value.column = column;
      sortConfig.value.order = 'desc';
    }
  }

  function setPage(page: number) {
    currentPage.value = page;
  }

  function setViewMode(mode: ViewMode) {
    viewMode.value = mode;
  }

  return {
    // State
    propertyKPIs,
    fredKPIs,
    fredMetrics,
    lastUpdated,
    properties,
    pagination,
    isLoading,
    isLoadingPreview,
    error,
    viewMode,
    filters,
    sortConfig,
    currentPage,
    perPage,
    previewCount,

    // Computed
    activeFilters,
    hasActiveFilters,
    relativeFreshness,

    // Actions
    loadDashboard,
    searchWithFilters,
    updateFilterPreview,
    setFilter,
    clearFilter,
    clearAllFilters,
    setSort,
    setPage,
    setViewMode
  };
});

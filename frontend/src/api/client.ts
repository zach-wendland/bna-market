import axios from 'axios';
import type {
  DashboardData,
  PropertiesSearchResponse,
  FredMetricsResponse,
  SearchParams
} from '@/types';

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging and auth headers
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);

    // Add auth token if available
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('[API Error]', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Dashboard API
export async function fetchDashboardData(): Promise<DashboardData> {
  const response = await api.get<DashboardData>('/dashboard');
  return response.data;
}

// Properties API
export async function searchProperties(params: SearchParams): Promise<PropertiesSearchResponse> {
  const queryParams = new URLSearchParams();

  queryParams.set('property_type', params.propertyType);
  queryParams.set('page', String(params.page));
  queryParams.set('per_page', String(params.perPage));

  if (params.minPrice) queryParams.set('min_price', String(params.minPrice));
  if (params.maxPrice) queryParams.set('max_price', String(params.maxPrice));
  if (params.minBeds) queryParams.set('min_beds', String(params.minBeds));
  if (params.maxBeds) queryParams.set('max_beds', String(params.maxBeds));
  if (params.minBaths) queryParams.set('min_baths', String(params.minBaths));
  if (params.maxBaths) queryParams.set('max_baths', String(params.maxBaths));
  if (params.minSqft) queryParams.set('min_sqft', String(params.minSqft));
  if (params.maxSqft) queryParams.set('max_sqft', String(params.maxSqft));
  if (params.city) queryParams.set('city', params.city);
  if (params.zipCode) queryParams.set('zip_code', params.zipCode);
  if (params.sortBy) queryParams.set('sort_by', params.sortBy);
  if (params.sortOrder) queryParams.set('sort_order', params.sortOrder);

  const response = await api.get<PropertiesSearchResponse>(`/properties/search?${queryParams.toString()}`);
  return response.data;
}

// Get count only (for filter preview)
export async function getPropertyCount(params: SearchParams): Promise<number> {
  const result = await searchProperties({ ...params, page: 1, perPage: 1 });
  return result.pagination.totalCount;
}

// Export CSV
export function getExportUrl(params: SearchParams): string {
  const queryParams = new URLSearchParams();
  queryParams.set('property_type', params.propertyType);

  if (params.minPrice) queryParams.set('min_price', String(params.minPrice));
  if (params.maxPrice) queryParams.set('max_price', String(params.maxPrice));
  if (params.minBeds) queryParams.set('min_beds', String(params.minBeds));
  if (params.maxBeds) queryParams.set('max_beds', String(params.maxBeds));
  if (params.minBaths) queryParams.set('min_baths', String(params.minBaths));
  if (params.maxBaths) queryParams.set('max_baths', String(params.maxBaths));
  if (params.minSqft) queryParams.set('min_sqft', String(params.minSqft));
  if (params.maxSqft) queryParams.set('max_sqft', String(params.maxSqft));
  if (params.city) queryParams.set('city', params.city);
  if (params.zipCode) queryParams.set('zip_code', params.zipCode);

  return `/api/properties/export?${queryParams.toString()}`;
}

// FRED Metrics API
export async function fetchFredMetrics(filters?: {
  metricName?: string;
  startDate?: string;
  endDate?: string;
}): Promise<FredMetricsResponse> {
  const queryParams = new URLSearchParams();

  if (filters?.metricName) queryParams.set('metric_name', filters.metricName);
  if (filters?.startDate) queryParams.set('start_date', filters.startDate);
  if (filters?.endDate) queryParams.set('end_date', filters.endDate);

  const url = queryParams.toString() ? `/metrics/fred?${queryParams.toString()}` : '/metrics/fred';
  const response = await api.get<FredMetricsResponse>(url);
  return response.data;
}

// Health check
export async function checkHealth(): Promise<{ status: string; database: { connected: boolean } }> {
  const response = await api.get('/health');
  return response.data;
}

// ====================================================================
// Property Lists API
// ====================================================================

export interface PropertyList {
  id: string;
  name: string;
  description?: string;
  itemCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface ListItem {
  id: string;
  listId: string;
  zpid: string;
  propertyType: 'rental' | 'forsale';
  notes?: string;
  addedAt: string;
}

export async function getUserLists(): Promise<PropertyList[]> {
  const response = await api.get<{ lists: PropertyList[] }>('/lists');
  return response.data.lists;
}

export async function createList(name: string, description?: string): Promise<PropertyList> {
  const response = await api.post<PropertyList>('/lists', { name, description });
  return response.data;
}

export async function getListWithItems(listId: string): Promise<PropertyList & { items: ListItem[] }> {
  const response = await api.get<PropertyList & { items: ListItem[] }>(`/lists/${listId}`);
  return response.data;
}

export async function updateList(listId: string, updates: { name?: string; description?: string }): Promise<PropertyList> {
  const response = await api.put<PropertyList>(`/lists/${listId}`, updates);
  return response.data;
}

export async function deleteList(listId: string): Promise<void> {
  await api.delete(`/lists/${listId}`);
}

export async function addPropertyToList(
  listId: string,
  zpid: string,
  propertyType: 'rental' | 'forsale',
  notes?: string
): Promise<ListItem> {
  const response = await api.post<ListItem>(`/lists/${listId}/items`, { zpid, propertyType, notes });
  return response.data;
}

export async function removePropertyFromList(listId: string, itemId: string): Promise<void> {
  await api.delete(`/lists/${listId}/items/${itemId}`);
}

export async function updateListItemNotes(listId: string, itemId: string, notes: string): Promise<ListItem> {
  const response = await api.put<ListItem>(`/lists/${listId}/items/${itemId}`, { notes });
  return response.data;
}

// ====================================================================
// Saved Searches API
// ====================================================================

export interface SavedSearch {
  id: string;
  name: string;
  propertyType: 'rental' | 'forsale';
  filters: Record<string, any>;
  createdAt: string;
  updatedAt: string;
}

export async function getSavedSearches(): Promise<SavedSearch[]> {
  const response = await api.get<{ searches: SavedSearch[] }>('/searches');
  return response.data.searches;
}

export async function saveSearch(
  name: string,
  propertyType: 'rental' | 'forsale',
  filters: Record<string, any>
): Promise<SavedSearch> {
  const response = await api.post<SavedSearch>('/searches', { name, propertyType, filters });
  return response.data;
}

export async function getSavedSearch(searchId: string): Promise<SavedSearch> {
  const response = await api.get<SavedSearch>(`/searches/${searchId}`);
  return response.data;
}

export async function updateSavedSearch(
  searchId: string,
  updates: { name?: string; filters?: Record<string, any> }
): Promise<SavedSearch> {
  const response = await api.put<SavedSearch>(`/searches/${searchId}`, updates);
  return response.data;
}

export async function deleteSavedSearch(searchId: string): Promise<void> {
  await api.delete(`/searches/${searchId}`);
}

export default api;

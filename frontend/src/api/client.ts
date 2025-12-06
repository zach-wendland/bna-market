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

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
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

export default api;

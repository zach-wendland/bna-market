// Property types
export interface Property {
  zpid: string;
  address: string | null;
  price: number | null;
  bedrooms: number | null;
  bathrooms: number | null;
  livingArea: number | null;
  propertyType: string | null;
  latitude: number | null;
  longitude: number | null;
  imgSrc: string | null;
  detailUrl: string | null;
  daysOnZillow: number | null;
  listingStatus: string | null;
  pricePerSqft?: number | null;
}

export interface PaginationMeta {
  page: number;
  perPage: number;
  totalCount: number;
  totalPages: number;
  hasNext: boolean;
  hasPrev: boolean;
}

export interface PropertiesSearchResponse {
  properties: Property[];
  pagination: PaginationMeta;
}

// Filter types
export interface PropertyFilters {
  propertyType: 'forsale' | 'rental';
  minPrice?: number | null;
  maxPrice?: number | null;
  minBeds?: number | null;
  maxBeds?: number | null;
  minBaths?: number | null;
  maxBaths?: number | null;
  minSqft?: number | null;
  maxSqft?: number | null;
  city?: string;
  zipCode?: string;
}

export interface SearchParams extends PropertyFilters {
  page: number;
  perPage: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

// FRED Metrics types
export interface FredMetric {
  date: string;
  metricName: string;
  seriesId: string;
  value: number;
}

export interface FredMetricsResponse {
  metrics: FredMetric[];
  count: number;
}

// KPI types
export interface PropertyKPIs {
  totalRentalListings: number;
  avgRentalPrice: number | null;
  totalForSaleListings: number;
  avgSalePrice: number | null;
}

export interface FredKPIs {
  medianPrice?: number;
  activeListings?: number;
  medianDaysOnMarket?: number;
  nonFarmEmployment?: number;
  msaPopulation?: number;
  perCapitaIncome?: number;
}

export interface DashboardData {
  propertyKPIs: PropertyKPIs;
  fredKPIs: FredKPIs;
  rentals: Property[];
  forsale: Property[];
  fredMetrics: FredMetric[];
  lastUpdated: string | null;
}

// View mode
export type ViewMode = 'table' | 'cards' | 'map';

// Sort config
export interface SortConfig {
  column: string;
  order: 'asc' | 'desc';
}

// Active filter for chips
export interface ActiveFilter {
  key: string;
  label: string;
  value: string | number;
}

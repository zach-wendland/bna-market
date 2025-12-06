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
  minPrice?: number;
  maxPrice?: number;
  minBeds?: number;
  maxBeds?: number;
  minBaths?: number;
  maxBaths?: number;
  minSqft?: number;
  maxSqft?: number;
  city?: string;
  zipCode?: string;
  page?: number;
  perPage?: number;
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

// Health check types
export interface HealthResponse {
  status: 'healthy' | 'unhealthy';
  apiVersion: string;
  endpoints: string[];
  database: {
    connected: boolean;
    tables: string[];
  };
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

// Table name mapping for security
export const PROPERTY_TYPE_TABLE_MAP: Record<string, string> = {
  forsale: 'BNA_FORSALE',
  rental: 'BNA_RENTALS'
} as const;

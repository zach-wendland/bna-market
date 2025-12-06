import { Router, Request, Response } from 'express';
import { query, getLastModified } from '../services/database.js';
import type { Property, FredMetric, DashboardData, PropertyKPIs, FredKPIs } from '../types/index.js';

const router = Router();

// Helper to fix Zillow URLs (stored as relative paths)
function fixZillowUrl(detailUrl: string | null): string | null {
  if (!detailUrl) return null;
  if (detailUrl.startsWith('http')) return detailUrl;
  return `https://www.zillow.com${detailUrl}`;
}

// GET /api/dashboard - Get all dashboard data in one call
router.get('/', async (_req: Request, res: Response) => {
  try {
    // Get KPI aggregates from FULL database (not limited)
    let rentalKpiData = { count: 0, avgPrice: null as number | null };
    let forsaleKpiData = { count: 0, avgPrice: null as number | null };

    try {
      const rentalStats = await query<{ count: number; avg_price: number | null }>(`
        SELECT COUNT(*) as count, AVG(price) as avg_price
        FROM BNA_RENTALS
        WHERE price IS NOT NULL AND price > 0
      `);
      if (rentalStats.length > 0) {
        rentalKpiData = {
          count: rentalStats[0].count,
          avgPrice: rentalStats[0].avg_price ? Math.round(rentalStats[0].avg_price) : null
        };
      }
    } catch (e) {
      console.warn('Could not get rental KPIs:', e);
    }

    try {
      const forsaleStats = await query<{ count: number; avg_price: number | null }>(`
        SELECT COUNT(*) as count, AVG(price) as avg_price
        FROM BNA_FORSALE
        WHERE price IS NOT NULL AND price > 0
      `);
      if (forsaleStats.length > 0) {
        forsaleKpiData = {
          count: forsaleStats[0].count,
          avgPrice: forsaleStats[0].avg_price ? Math.round(forsaleStats[0].avg_price) : null
        };
      }
    } catch (e) {
      console.warn('Could not get forsale KPIs:', e);
    }

    // Get rentals (limited for display)
    let rentals: Property[] = [];
    try {
      const rentalRows = await query<Property>(`
        SELECT zpid, address, price, bedrooms, bathrooms, livingArea,
               propertyType, latitude, longitude, imgSrc, detailUrl,
               daysOnZillow, listingStatus
        FROM BNA_RENTALS
        ORDER BY price DESC
        LIMIT 100
      `);

      rentals = rentalRows.map(row => ({
        ...row,
        detailUrl: fixZillowUrl(row.detailUrl),
        pricePerSqft: row.price && row.livingArea && row.livingArea > 0
          ? Math.round((row.price / row.livingArea) * 100) / 100
          : null
      }));
    } catch (e) {
      console.warn('Could not read BNA_RENTALS:', e);
    }

    // Get for-sale (limited for display)
    let forsale: Property[] = [];
    try {
      const forsaleRows = await query<Property>(`
        SELECT zpid, address, price, bedrooms, bathrooms, livingArea,
               propertyType, latitude, longitude, imgSrc, detailUrl,
               daysOnZillow, listingStatus
        FROM BNA_FORSALE
        ORDER BY price DESC
        LIMIT 100
      `);

      forsale = forsaleRows.map(row => ({
        ...row,
        detailUrl: fixZillowUrl(row.detailUrl),
        pricePerSqft: row.price && row.livingArea && row.livingArea > 0
          ? Math.round((row.price / row.livingArea) * 100) / 100
          : null
      }));
    } catch (e) {
      console.warn('Could not read BNA_FORSALE:', e);
    }

    // Get FRED metrics
    let fredMetrics: FredMetric[] = [];
    try {
      fredMetrics = await query<FredMetric>(`
        SELECT date, metric_name as metricName, series_id as seriesId, value
        FROM BNA_FRED_METRICS
        ORDER BY date DESC
      `);
    } catch (e) {
      console.warn('Could not read BNA_FRED_METRICS:', e);
    }

    // Use pre-computed KPIs from full database
    const propertyKPIs: PropertyKPIs = {
      totalRentalListings: rentalKpiData.count,
      avgRentalPrice: rentalKpiData.avgPrice,
      totalForSaleListings: forsaleKpiData.count,
      avgSalePrice: forsaleKpiData.avgPrice
    };

    // Calculate FRED KPIs (latest values)
    const fredKPIs: FredKPIs = {};
    const metricMap: Record<string, keyof FredKPIs> = {
      'median_price': 'medianPrice',
      'active_listings': 'activeListings',
      'median_dom': 'medianDaysOnMarket',
      'employment_non_farm': 'nonFarmEmployment',
      'msa_population': 'msaPopulation',
      'msa_per_capita_income': 'perCapitaIncome'
    };

    // Group by metric and get latest
    const latestByMetric = new Map<string, FredMetric>();
    for (const metric of fredMetrics) {
      const existing = latestByMetric.get(metric.metricName);
      if (!existing || metric.date > existing.date) {
        latestByMetric.set(metric.metricName, metric);
      }
    }

    for (const [dbName, kpiName] of Object.entries(metricMap)) {
      const metric = latestByMetric.get(dbName);
      if (metric) {
        fredKPIs[kpiName] = metric.value;
      }
    }

    // Get database last modified time
    const lastUpdated = getLastModified();

    const response: DashboardData = {
      propertyKPIs,
      fredKPIs,
      rentals,
      forsale,
      fredMetrics,
      lastUpdated
    };

    res.json(response);
  } catch (error) {
    console.error('Dashboard error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;

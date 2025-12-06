import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { query, queryScalar } from '../services/database.js';
import { PROPERTY_TYPE_TABLE_MAP, type Property, type PropertiesSearchResponse } from '../types/index.js';

const router = Router();

// Helper to fix Zillow URLs (stored as relative paths)
function fixZillowUrl(detailUrl: string | null): string | null {
  if (!detailUrl) return null;
  if (detailUrl.startsWith('http')) return detailUrl;
  return `https://www.zillow.com${detailUrl}`;
}

// Validation schema for search params
const searchSchema = z.object({
  property_type: z.enum(['forsale', 'rental']),
  min_price: z.coerce.number().optional(),
  max_price: z.coerce.number().optional(),
  min_beds: z.coerce.number().int().optional(),
  max_beds: z.coerce.number().int().optional(),
  min_baths: z.coerce.number().optional(),
  max_baths: z.coerce.number().optional(),
  min_sqft: z.coerce.number().int().optional(),
  max_sqft: z.coerce.number().int().optional(),
  city: z.string().optional(),
  zip_code: z.string().optional(),
  page: z.coerce.number().int().min(1).default(1),
  per_page: z.coerce.number().int().min(1).max(100).default(20),
  sort_by: z.enum(['price', 'bedrooms', 'bathrooms', 'livingArea', 'daysOnZillow', 'address', 'price_per_sqft']).optional(),
  sort_order: z.enum(['asc', 'desc']).default('desc')
});

// GET /api/properties/search
router.get('/search', async (req: Request, res: Response) => {
  try {
    // Validate query params
    const result = searchSchema.safeParse(req.query);
    if (!result.success) {
      return res.status(400).json({
        error: 'Validation error',
        details: result.error.issues
      });
    }

    const params = result.data;
    const tableName = PROPERTY_TYPE_TABLE_MAP[params.property_type];
    if (!tableName) {
      return res.status(400).json({ error: 'Invalid property type' });
    }

    // Build WHERE conditions
    const conditions: string[] = [];
    const values: (string | number | null)[] = [];

    if (params.min_price !== undefined) {
      conditions.push('price >= ?');
      values.push(params.min_price);
    }
    if (params.max_price !== undefined) {
      conditions.push('price <= ?');
      values.push(params.max_price);
    }
    if (params.min_beds !== undefined) {
      conditions.push('bedrooms >= ?');
      values.push(params.min_beds);
    }
    if (params.max_beds !== undefined) {
      conditions.push('bedrooms <= ?');
      values.push(params.max_beds);
    }
    if (params.min_baths !== undefined) {
      conditions.push('bathrooms >= ?');
      values.push(params.min_baths);
    }
    if (params.max_baths !== undefined) {
      conditions.push('bathrooms <= ?');
      values.push(params.max_baths);
    }
    if (params.min_sqft !== undefined) {
      conditions.push('livingArea >= ?');
      values.push(params.min_sqft);
    }
    if (params.max_sqft !== undefined) {
      conditions.push('livingArea <= ?');
      values.push(params.max_sqft);
    }
    if (params.city) {
      conditions.push('LOWER(address) LIKE ?');
      values.push(`%${params.city.toLowerCase()}%`);
    }
    if (params.zip_code) {
      conditions.push('address LIKE ?');
      values.push(`%${params.zip_code}%`);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

    // Determine sort column (use safe mapping)
    const sortColumnMap: Record<string, string> = {
      price: 'price',
      bedrooms: 'bedrooms',
      bathrooms: 'bathrooms',
      livingArea: 'livingArea',
      daysOnZillow: 'daysOnZillow',
      address: 'address',
      price_per_sqft: 'CAST(price AS REAL) / NULLIF(livingArea, 0)'
    };
    const sortColumn = params.sort_by ? sortColumnMap[params.sort_by] || 'price' : 'price';
    const sortOrder = params.sort_order.toUpperCase();

    // Get total count
    const totalCount = await queryScalar<number>(
      `SELECT COUNT(*) FROM ${tableName} ${whereClause}`,
      values
    ) || 0;

    // Calculate pagination
    const offset = (params.page - 1) * params.per_page;
    const totalPages = Math.ceil(totalCount / params.per_page);

    // Get paginated results
    const dataQuery = `
      SELECT zpid, address, price, bedrooms, bathrooms, livingArea,
             propertyType, latitude, longitude, imgSrc, detailUrl,
             daysOnZillow, listingStatus
      FROM ${tableName}
      ${whereClause}
      ORDER BY ${sortColumn} ${sortOrder}
      LIMIT ? OFFSET ?
    `;

    const rows = await query<Property>(dataQuery, [...values, params.per_page, offset]);

    // Add price per sqft calculation and fix Zillow URLs
    const properties: Property[] = rows.map(row => ({
      ...row,
      detailUrl: fixZillowUrl(row.detailUrl),
      pricePerSqft: row.price && row.livingArea && row.livingArea > 0
        ? Math.round((row.price / row.livingArea) * 100) / 100
        : null
    }));

    const response: PropertiesSearchResponse = {
      properties,
      pagination: {
        page: params.page,
        perPage: params.per_page,
        totalCount,
        totalPages,
        hasNext: params.page < totalPages,
        hasPrev: params.page > 1
      }
    };

    res.json(response);
  } catch (error) {
    console.error('Search error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// GET /api/properties/export
router.get('/export', async (req: Request, res: Response) => {
  try {
    const propertyType = req.query.property_type as string;

    if (!propertyType || !['forsale', 'rental'].includes(propertyType)) {
      return res.status(400).json({ error: 'property_type must be "forsale" or "rental"' });
    }

    const tableName = PROPERTY_TYPE_TABLE_MAP[propertyType];

    // Build WHERE conditions (same as search)
    const conditions: string[] = [];
    const values: (string | number | null)[] = [];

    const minPrice = req.query.min_price ? Number(req.query.min_price) : undefined;
    const maxPrice = req.query.max_price ? Number(req.query.max_price) : undefined;
    const minBeds = req.query.min_beds ? Number(req.query.min_beds) : undefined;
    const maxBeds = req.query.max_beds ? Number(req.query.max_beds) : undefined;
    const minBaths = req.query.min_baths ? Number(req.query.min_baths) : undefined;
    const maxBaths = req.query.max_baths ? Number(req.query.max_baths) : undefined;
    const minSqft = req.query.min_sqft ? Number(req.query.min_sqft) : undefined;
    const maxSqft = req.query.max_sqft ? Number(req.query.max_sqft) : undefined;
    const city = req.query.city as string | undefined;
    const zipCode = req.query.zip_code as string | undefined;

    if (minPrice !== undefined) { conditions.push('price >= ?'); values.push(minPrice); }
    if (maxPrice !== undefined) { conditions.push('price <= ?'); values.push(maxPrice); }
    if (minBeds !== undefined) { conditions.push('bedrooms >= ?'); values.push(minBeds); }
    if (maxBeds !== undefined) { conditions.push('bedrooms <= ?'); values.push(maxBeds); }
    if (minBaths !== undefined) { conditions.push('bathrooms >= ?'); values.push(minBaths); }
    if (maxBaths !== undefined) { conditions.push('bathrooms <= ?'); values.push(maxBaths); }
    if (minSqft !== undefined) { conditions.push('livingArea >= ?'); values.push(minSqft); }
    if (maxSqft !== undefined) { conditions.push('livingArea <= ?'); values.push(maxSqft); }
    if (city) { conditions.push('LOWER(address) LIKE ?'); values.push(`%${city.toLowerCase()}%`); }
    if (zipCode) { conditions.push('address LIKE ?'); values.push(`%${zipCode}%`); }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

    const sqlQuery = `
      SELECT zpid, address, price, bedrooms, bathrooms, livingArea,
             propertyType, latitude, longitude, daysOnZillow,
             listingStatus, detailUrl
      FROM ${tableName}
      ${whereClause}
      ORDER BY price DESC
    `;

    const rows = await query<Property>(sqlQuery, values);

    // Fix Zillow URLs for export
    const properties = rows.map(row => ({
      ...row,
      detailUrl: fixZillowUrl(row.detailUrl)
    }));

    // Build CSV
    const headers = ['zpid', 'address', 'price', 'bedrooms', 'bathrooms', 'livingArea',
                     'propertyType', 'latitude', 'longitude', 'daysOnZillow', 'listingStatus', 'detailUrl'];

    const csvRows = [headers.join(',')];
    for (const row of properties) {
      const csvValues = headers.map(h => {
        const val = row[h as keyof Property];
        if (val === null || val === undefined) return '';
        if (typeof val === 'string' && (val.includes(',') || val.includes('"'))) {
          return `"${val.replace(/"/g, '""')}"`;
        }
        return String(val);
      });
      csvRows.push(csvValues.join(','));
    }

    const csv = csvRows.join('\n');

    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', `attachment; filename=bna_${propertyType}_export.csv`);
    res.send(csv);
  } catch (error) {
    console.error('Export error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;

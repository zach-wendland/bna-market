-- Historical Snapshot Tracking for BNA Market
-- Enables time-series analysis of property metrics

-- ============================================
-- Phase 1: Add snapshot_date columns
-- ============================================

-- Add snapshot_date to bna_forsale
ALTER TABLE bna_forsale
ADD COLUMN IF NOT EXISTS snapshot_date DATE DEFAULT CURRENT_DATE;

-- Add snapshot_date to bna_rentals
ALTER TABLE bna_rentals
ADD COLUMN IF NOT EXISTS snapshot_date DATE DEFAULT CURRENT_DATE;

-- ============================================
-- Phase 2: Update unique constraints
-- ============================================

-- Drop existing unique constraint on zpid (if exists)
-- Note: Supabase may have created this differently, adjust as needed
DROP INDEX IF EXISTS bna_forsale_zpid_key;
DROP INDEX IF EXISTS bna_rentals_zpid_key;

-- Create new composite unique constraint (zpid + snapshot_date)
-- This allows the same property to appear on different days
CREATE UNIQUE INDEX IF NOT EXISTS bna_forsale_zpid_snapshot_key
ON bna_forsale(zpid, snapshot_date);

CREATE UNIQUE INDEX IF NOT EXISTS bna_rentals_zpid_snapshot_key
ON bna_rentals(zpid, snapshot_date);

-- ============================================
-- Phase 3: Create indexes for time-series queries
-- ============================================

CREATE INDEX IF NOT EXISTS idx_forsale_snapshot_date
ON bna_forsale(snapshot_date);

CREATE INDEX IF NOT EXISTS idx_rentals_snapshot_date
ON bna_rentals(snapshot_date);

-- Composite index for efficient aggregations
CREATE INDEX IF NOT EXISTS idx_forsale_snapshot_price
ON bna_forsale(snapshot_date, price) WHERE price > 0;

CREATE INDEX IF NOT EXISTS idx_rentals_snapshot_price
ON bna_rentals(snapshot_date, price) WHERE price > 0;

-- ============================================
-- Phase 4: Create aggregation views
-- ============================================

-- Monthly for-sale statistics
CREATE OR REPLACE VIEW monthly_forsale_stats AS
SELECT
    DATE_TRUNC('month', snapshot_date)::DATE as month,
    ROUND(AVG(price)::numeric, 0) as avg_price,
    ROUND(AVG(days_on_zillow)::numeric, 1) as avg_dom,
    COUNT(*) as listing_count,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) as median_price,
    MIN(price) as min_price,
    MAX(price) as max_price
FROM bna_forsale
WHERE price > 0 AND price < 10000000  -- Filter outliers
GROUP BY DATE_TRUNC('month', snapshot_date)
ORDER BY month DESC;

-- Monthly rental statistics
CREATE OR REPLACE VIEW monthly_rental_stats AS
SELECT
    DATE_TRUNC('month', snapshot_date)::DATE as month,
    ROUND(AVG(price)::numeric, 0) as avg_price,
    ROUND(AVG(days_on_zillow)::numeric, 1) as avg_dom,
    COUNT(*) as listing_count,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) as median_price,
    MIN(price) as min_price,
    MAX(price) as max_price
FROM bna_rentals
WHERE price > 0 AND price < 100000  -- Filter outliers (monthly rent)
GROUP BY DATE_TRUNC('month', snapshot_date)
ORDER BY month DESC;

-- Daily snapshot counts (for monitoring ETL runs)
CREATE OR REPLACE VIEW daily_snapshot_counts AS
SELECT
    snapshot_date,
    'forsale' as property_type,
    COUNT(*) as count,
    ROUND(AVG(price)::numeric, 0) as avg_price
FROM bna_forsale
GROUP BY snapshot_date
UNION ALL
SELECT
    snapshot_date,
    'rental' as property_type,
    COUNT(*) as count,
    ROUND(AVG(price)::numeric, 0) as avg_price
FROM bna_rentals
GROUP BY snapshot_date
ORDER BY snapshot_date DESC, property_type;

-- ============================================
-- Phase 5: Grant access to views (if needed)
-- ============================================

-- Views inherit table permissions, but explicit grants ensure access
GRANT SELECT ON monthly_forsale_stats TO anon, authenticated;
GRANT SELECT ON monthly_rental_stats TO anon, authenticated;
GRANT SELECT ON daily_snapshot_counts TO anon, authenticated;

-- ============================================
-- Notes for future data management:
-- ============================================
--
-- To prevent unbounded growth, consider adding a cleanup job:
--
-- DELETE FROM bna_forsale
-- WHERE snapshot_date < CURRENT_DATE - INTERVAL '1 year';
--
-- DELETE FROM bna_rentals
-- WHERE snapshot_date < CURRENT_DATE - INTERVAL '1 year';
--
-- Run this monthly to keep only 1 year of history.

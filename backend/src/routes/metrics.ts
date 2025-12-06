import { Router, Request, Response } from 'express';
import { query } from '../services/database.js';
import type { FredMetric, FredMetricsResponse } from '../types/index.js';

const router = Router();

// GET /api/metrics/fred
router.get('/fred', async (req: Request, res: Response) => {
  try {
    const conditions: string[] = [];
    const values: (string | number | null)[] = [];

    // Optional filters
    const metricName = req.query.metric_name as string | undefined;
    const seriesId = req.query.series_id as string | undefined;
    const startDate = req.query.start_date as string | undefined;
    const endDate = req.query.end_date as string | undefined;

    if (metricName) {
      conditions.push('metric_name = ?');
      values.push(metricName);
    }
    if (seriesId) {
      conditions.push('series_id = ?');
      values.push(seriesId);
    }
    if (startDate) {
      conditions.push('date >= ?');
      values.push(startDate);
    }
    if (endDate) {
      conditions.push('date <= ?');
      values.push(endDate);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

    const sqlQuery = `
      SELECT date, metric_name as metricName, series_id as seriesId, value
      FROM BNA_FRED_METRICS
      ${whereClause}
      ORDER BY date DESC, metric_name
    `;

    const rows = await query<FredMetric>(sqlQuery, values);

    const response: FredMetricsResponse = {
      metrics: rows,
      count: rows.length
    };

    res.json(response);
  } catch (error) {
    console.error('FRED metrics error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

export default router;

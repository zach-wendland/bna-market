import { Router, Request, Response } from 'express';
import { checkDatabaseHealth } from '../services/database.js';
import type { HealthResponse } from '../types/index.js';

const router = Router();

router.get('/', async (_req: Request, res: Response) => {
  const dbHealth = await checkDatabaseHealth();

  const response: HealthResponse = {
    status: dbHealth.connected ? 'healthy' : 'unhealthy',
    apiVersion: '2.0',
    endpoints: [
      '/api/health',
      '/api/properties/search',
      '/api/properties/export',
      '/api/metrics/fred',
      '/api/dashboard'
    ],
    database: dbHealth
  };

  const statusCode = dbHealth.connected ? 200 : 503;
  res.status(statusCode).json(response);
});

export default router;

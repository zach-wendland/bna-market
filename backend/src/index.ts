import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import morgan from 'morgan';
import path from 'path';
import { fileURLToPath } from 'url';

import healthRouter from './routes/health.js';
import propertiesRouter from './routes/properties.js';
import metricsRouter from './routes/metrics.js';
import dashboardRouter from './routes/dashboard.js';
import { closeDatabase } from './services/database.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(helmet({
  contentSecurityPolicy: false // Allow inline scripts for dev
}));
app.use(cors({
  origin: process.env.NODE_ENV === 'production'
    ? false // Same origin in production
    : ['http://localhost:5173', 'http://localhost:3000'] // Vite dev server
}));
app.use(morgan('dev'));
app.use(express.json());

// API Routes
app.use('/api/health', healthRouter);
app.use('/api/properties', propertiesRouter);
app.use('/api/metrics', metricsRouter);
app.use('/api/dashboard', dashboardRouter);

// Serve static frontend in production
const frontendDist = path.join(__dirname, '..', '..', 'frontend', 'dist');
app.use(express.static(frontendDist));

// SPA fallback - serve index.html for all non-API routes
app.get('*', (req, res) => {
  if (!req.path.startsWith('/api')) {
    res.sendFile(path.join(frontendDist, 'index.html'));
  } else {
    res.status(404).json({ error: 'Not found' });
  }
});

// Error handler
app.use((err: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\nShutting down...');
  closeDatabase();
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\nShutting down...');
  closeDatabase();
  process.exit(0);
});

// Start server
app.listen(PORT, () => {
  console.log(`
  ╔════════════════════════════════════════════════════╗
  ║                                                    ║
  ║   BNA Market API Server                            ║
  ║   Running on http://localhost:${PORT}                 ║
  ║                                                    ║
  ║   Endpoints:                                       ║
  ║   - GET /api/health                                ║
  ║   - GET /api/dashboard                             ║
  ║   - GET /api/properties/search                     ║
  ║   - GET /api/properties/export                     ║
  ║   - GET /api/metrics/fred                          ║
  ║                                                    ║
  ╚════════════════════════════════════════════════════╝
  `);
});

export default app;

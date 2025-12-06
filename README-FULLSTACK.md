# BNA Market - Full Stack Application

A modern Nashville Real Estate Market Analytics dashboard built with:

- **Backend**: Express.js + TypeScript + better-sqlite3
- **Frontend**: Vue 3 + Vite + Tailwind CSS + Pinia
- **Database**: SQLite (existing BNASFR02.DB)

## Features

- **Interactive Map View** - Leaflet.js with clustered markers, color-coded by price
- **Real-time Filter Preview** - See matching count as you type
- **Sortable Data Tables** - Click column headers to sort
- **Price per Square Foot** - Calculated and displayed everywhere
- **Active Filter Chips** - Visual indicators with one-click removal
- **Responsive Design** - Mobile-first with Tailwind CSS
- **Charts & Analytics** - ApexCharts for price distribution and trends
- **CSV Export** - Download filtered results

## Quick Start

### Prerequisites

- Node.js >= 18.0.0
- npm >= 9.0.0
- Existing SQLite database (BNASFR02.DB in project root)

### Installation

```bash
# Install root dependencies
npm install

# Install all workspace dependencies
npm run install:all
```

### Development

```bash
# Start both backend and frontend dev servers
npm run dev

# Backend runs on http://localhost:3001
# Frontend runs on http://localhost:5173 (proxies API calls to backend)
```

### Production Build

```bash
# Build both projects
npm run build

# Start production server (serves frontend static files)
npm start

# App runs on http://localhost:3001
```

## Project Structure

```
bna-market/
├── backend/                  # Express.js API server
│   ├── src/
│   │   ├── index.ts         # Server entry point
│   │   ├── routes/          # API route handlers
│   │   │   ├── health.ts
│   │   │   ├── properties.ts
│   │   │   ├── metrics.ts
│   │   │   └── dashboard.ts
│   │   ├── services/
│   │   │   └── database.ts  # SQLite connection
│   │   └── types/
│   │       └── index.ts     # TypeScript interfaces
│   ├── package.json
│   └── tsconfig.json
│
├── frontend/                 # Vue 3 SPA
│   ├── src/
│   │   ├── main.ts          # Vue app entry
│   │   ├── App.vue          # Root component
│   │   ├── api/             # API client (axios)
│   │   ├── stores/          # Pinia state management
│   │   ├── composables/     # Vue composables
│   │   └── components/
│   │       ├── layout/      # Header, Footer
│   │       ├── dashboard/   # KPIs, Charts
│   │       ├── properties/  # Table, Cards, Map, Filters
│   │       └── ui/          # Shared UI components
│   ├── package.json
│   ├── vite.config.ts
│   └── tailwind.config.js
│
├── BNASFR02.DB              # SQLite database
├── package.json             # Root monorepo config
└── README-FULLSTACK.md      # This file
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check with database status |
| `/api/dashboard` | GET | All dashboard data in one call |
| `/api/properties/search` | GET | Search properties with filters |
| `/api/properties/export` | GET | Export filtered properties as CSV |
| `/api/metrics/fred` | GET | FRED economic metrics |

### Search Parameters

```
property_type: 'forsale' | 'rental' (required)
min_price, max_price: number
min_beds, max_beds: number
min_baths, max_baths: number
min_sqft, max_sqft: number
city: string (partial match)
zip_code: string
page: number (default: 1)
per_page: number (default: 20, max: 100)
sort_by: 'price' | 'bedrooms' | 'bathrooms' | 'livingArea' | 'daysOnZillow'
sort_order: 'asc' | 'desc'
```

## Tech Stack Details

### Backend
- **Express.js** - Minimal, fast Node.js framework
- **TypeScript** - Type safety
- **better-sqlite3** - Synchronous SQLite for simplicity
- **Zod** - Runtime validation
- **Helmet** - Security headers
- **Morgan** - Request logging

### Frontend
- **Vue 3** - Composition API with `<script setup>`
- **Pinia** - State management
- **Tailwind CSS** - Utility-first styling
- **Vite** - Fast dev server and build
- **ApexCharts** - Interactive charts
- **Leaflet** - Interactive maps
- **Axios** - HTTP client

## Development Notes

### Adding a New API Route

1. Create route file in `backend/src/routes/`
2. Register in `backend/src/index.ts`
3. Add types in `backend/src/types/index.ts`

### Adding a New Vue Component

1. Create `.vue` file in appropriate `frontend/src/components/` folder
2. Import and use in parent component
3. Add types in `frontend/src/types/index.ts` if needed

### Database

The existing SQLite database (`BNASFR02.DB`) is read-only by the backend. Tables:
- `BNA_FORSALE` - For-sale property listings
- `BNA_RENTALS` - Rental property listings
- `BNA_FRED_METRICS` - FRED economic indicators

## Migration from Flask

This replaces the original Flask + Jinja2 stack. Key changes:
- Server-side rendering → Client-side SPA
- Python → TypeScript/JavaScript
- Jinja2 templates → Vue components
- Plotly → ApexCharts
- Manual DOM manipulation → Reactive state

The original Python ETL pipelines (`bna_market/`) are preserved for data collection.

## License

MIT

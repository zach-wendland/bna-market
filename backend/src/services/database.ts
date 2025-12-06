import initSqlJs, { Database as SqlJsDatabase } from 'sql.js';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Database path - relative to backend folder (goes up to project root)
const DEFAULT_DB_PATH = path.resolve(__dirname, '..', '..', '..', 'BNASFR02.DB');
const DB_PATH = process.env.DATABASE_PATH || DEFAULT_DB_PATH;

let db: SqlJsDatabase | null = null;
let sqlPromise: Promise<typeof import('sql.js')> | null = null;

async function initSQL() {
  if (!sqlPromise) {
    sqlPromise = initSqlJs();
  }
  return sqlPromise;
}

export async function getDatabase(): Promise<SqlJsDatabase> {
  if (!db) {
    console.log('Database path resolved to:', DB_PATH);

    const SQL = await initSQL();

    if (!fs.existsSync(DB_PATH)) {
      throw new Error(`Database file not found: ${DB_PATH}`);
    }

    const fileBuffer = fs.readFileSync(DB_PATH);
    db = new SQL.Database(fileBuffer);
    console.log(`Connected to database: ${DB_PATH}`);
  }
  return db;
}

export function closeDatabase(): void {
  if (db) {
    db.close();
    db = null;
    console.log('Database connection closed');
  }
}

// Check if database and tables exist
export async function checkDatabaseHealth(): Promise<{ connected: boolean; tables: string[] }> {
  try {
    const database = await getDatabase();
    const result = database.exec("SELECT name FROM sqlite_master WHERE type='table'");

    const tables = result.length > 0 && result[0]
      ? result[0].values.map(row => String(row[0]))
      : [];

    return {
      connected: true,
      tables
    };
  } catch (error) {
    console.error('Database health check failed:', error);
    return {
      connected: false,
      tables: []
    };
  }
}

// Get database file modification time for freshness indicator
export function getLastModified(): string | null {
  try {
    const stats = fs.statSync(DB_PATH);
    return stats.mtime.toISOString();
  } catch {
    return null;
  }
}

// Helper function to execute SELECT queries and return results as array of objects
export async function query<T = Record<string, unknown>>(
  sql: string,
  params: (string | number | null)[] = []
): Promise<T[]> {
  const database = await getDatabase();

  // Prepare and bind parameters
  const stmt = database.prepare(sql);
  stmt.bind(params);

  const results: T[] = [];
  while (stmt.step()) {
    const row = stmt.getAsObject() as T;
    results.push(row);
  }
  stmt.free();

  return results;
}

// Helper to get single value
export async function queryScalar<T = number>(
  sql: string,
  params: (string | number | null)[] = []
): Promise<T | null> {
  const database = await getDatabase();
  const stmt = database.prepare(sql);
  stmt.bind(params);

  if (stmt.step()) {
    const row = stmt.get();
    stmt.free();
    return row[0] as T;
  }
  stmt.free();
  return null;
}

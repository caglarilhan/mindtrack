/**
 * Database query optimization utilities
 * Helps optimize Supabase queries
 */

/**
 * Batch operations helper
 * Executes multiple operations in parallel with concurrency limit
 */
export async function batchOperation<T, R>(
  items: T[],
  operation: (item: T) => Promise<R>,
  concurrency: number = 5
): Promise<R[]> {
  const results: R[] = [];
  
  for (let i = 0; i < items.length; i += concurrency) {
    const batch = items.slice(i, i + concurrency);
    const batchResults = await Promise.all(
      batch.map(item => operation(item))
    );
    results.push(...batchResults);
  }
  
  return results;
}

/**
 * Query with retry logic
 */
export async function queryWithRetry<T>(
  queryFn: () => Promise<T>,
  maxRetries: number = 3,
  retryDelay: number = 1000
): Promise<T> {
  let lastError: Error | null = null;
  
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await queryFn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      
      if (attempt < maxRetries) {
        await new Promise(resolve => setTimeout(resolve, retryDelay * (attempt + 1)));
        continue;
      }
    }
  }
  
  throw lastError || new Error("Query failed");
}

/**
 * Cache query result helper
 * Simple in-memory cache for query results
 */
const queryCache = new Map<string, { data: unknown; timestamp: number; ttl: number }>();

export function getCachedQuery<T>(key: string): T | null {
  const cached = queryCache.get(key);
  if (!cached) return null;
  
  if (Date.now() - cached.timestamp > cached.ttl) {
    queryCache.delete(key);
    return null;
  }
  
  return cached.data as T;
}

export function setCachedQuery<T>(key: string, data: T, ttl: number = 5 * 60 * 1000): void {
  queryCache.set(key, {
    data,
    timestamp: Date.now(),
    ttl,
  });
}

export function clearQueryCache(pattern?: string): void {
  if (pattern) {
    const regex = new RegExp(pattern);
    for (const key of queryCache.keys()) {
      if (regex.test(key)) {
        queryCache.delete(key);
      }
    }
  } else {
    queryCache.clear();
  }
}

/**
 * Optimize Supabase query with select only needed fields
 */
export function optimizeSelect(fields: string[]): string {
  // Supabase select optimization
  return fields.join(", ");
}

/**
 * Common optimized select patterns
 */
export const OPTIMIZED_SELECTS = {
  noteList: "id, client_id, type, created_at, owner_id",
  noteDetail: "id, client_id, type, content_encrypted, created_at, updated_at, owner_id, metadata",
  clientList: "id, name, status, email, phone",
  clientDetail: "id, name, status, email, phone, created_at, updated_at",
  sessionList: "id, client_id, status, created_at, updated_at",
  sessionDetail: "id, client_id, status, created_at, updated_at, notes",
} as const;






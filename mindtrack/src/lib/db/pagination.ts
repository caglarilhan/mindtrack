/**
 * Database pagination utilities
 * Helps with efficient pagination queries
 */

export interface PaginationParams {
  page: number;
  pageSize: number;
}

export interface PaginatedResult<T> {
  data: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
  hasMore: boolean;
}

/**
 * Calculate pagination offset
 */
export function getPaginationOffset(page: number, pageSize: number): number {
  return (page - 1) * pageSize;
}

/**
 * Calculate total pages
 */
export function getTotalPages(total: number, pageSize: number): number {
  return Math.ceil(total / pageSize);
}

/**
 * Create pagination metadata
 */
export function createPaginationMeta<T>(
  data: T[],
  total: number,
  page: number,
  pageSize: number
): PaginatedResult<T> {
  return {
    data,
    total,
    page,
    pageSize,
    totalPages: getTotalPages(total, pageSize),
    hasMore: page * pageSize < total,
  };
}

/**
 * Default pagination values
 */
export const DEFAULT_PAGINATION = {
  page: 1,
  pageSize: 20,
} as const;






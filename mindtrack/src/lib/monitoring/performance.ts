/**
 * Performance Monitoring
 * Track API performance, database queries, and application metrics
 */

import { captureMessage, setTag } from "./sentry";

export interface PerformanceMetric {
  name: string;
  duration: number;
  metadata?: Record<string, unknown>;
}

class PerformanceMonitor {
  private metrics: Map<string, PerformanceMetric[]> = new Map();
  private readonly maxMetrics = 1000; // Keep last 1000 metrics

  /**
   * Track a performance metric
   */
  track(metric: PerformanceMetric): void {
    const existing = this.metrics.get(metric.name) || [];
    existing.push(metric);
    
    // Keep only last maxMetrics
    if (existing.length > this.maxMetrics) {
      existing.shift();
    }
    
    this.metrics.set(metric.name, existing);

    // Log slow operations to Sentry
    if (metric.duration > 5000) { // 5 seconds
      captureMessage(`Slow operation detected: ${metric.name} took ${metric.duration}ms`, "warning");
      setTag("performance.slow", "true");
    }
  }

  /**
   * Get metrics for a specific operation
   */
  getMetrics(name: string): PerformanceMetric[] {
    return this.metrics.get(name) || [];
  }

  /**
   * Get average duration for an operation
   */
  getAverageDuration(name: string): number {
    const metrics = this.getMetrics(name);
    if (metrics.length === 0) return 0;
    
    const sum = metrics.reduce((acc, m) => acc + m.duration, 0);
    return sum / metrics.length;
  }

  /**
   * Get all metrics
   */
  getAllMetrics(): Map<string, PerformanceMetric[]> {
    return new Map(this.metrics);
  }

  /**
   * Clear metrics
   */
  clear(): void {
    this.metrics.clear();
  }
}

export const performanceMonitor = new PerformanceMonitor();

/**
 * Performance decorator for async functions
 */
export function trackPerformance(name: string) {
  return function (target: unknown, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: unknown[]) {
      const start = Date.now();
      try {
        const result = await originalMethod.apply(this, args);
        const duration = Date.now() - start;
        
        performanceMonitor.track({
          name: `${name}.${propertyKey}`,
          duration,
          metadata: {
            args: args.length,
          },
        });
        
        return result;
      } catch (error) {
        const duration = Date.now() - start;
        
        performanceMonitor.track({
          name: `${name}.${propertyKey}`,
          duration,
          metadata: {
            error: error instanceof Error ? error.message : "Unknown error",
          },
        });
        
        throw error;
      }
    };

    return descriptor;
  };
}

/**
 * Track API route performance
 */
export async function trackAPIPerformance<T>(
  routeName: string,
  handler: () => Promise<T>
): Promise<T> {
  const start = Date.now();
  try {
    const result = await handler();
    const duration = Date.now() - start;
    
    performanceMonitor.track({
      name: `api.${routeName}`,
      duration,
      metadata: {
        success: true,
      },
    });
    
    return result;
  } catch (error) {
    const duration = Date.now() - start;
    
    performanceMonitor.track({
      name: `api.${routeName}`,
      duration,
      metadata: {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      },
    });
    
    throw error;
  }
}

/**
 * Track database query performance
 */
export async function trackDBQuery<T>(
  queryName: string,
  query: () => Promise<T>
): Promise<T> {
  const start = Date.now();
  try {
    const result = await query();
    const duration = Date.now() - start;
    
    performanceMonitor.track({
      name: `db.${queryName}`,
      duration,
      metadata: {
        success: true,
      },
    });
    
    return result;
  } catch (error) {
    const duration = Date.now() - start;
    
    performanceMonitor.track({
      name: `db.${queryName}`,
      duration,
      metadata: {
        success: false,
        error: error instanceof Error ? error.message : "Unknown error",
      },
    });
    
    throw error;
  }
}






/**
 * Sentry Error Tracking Configuration
 * Centralized error tracking setup
 */

import * as Sentry from "@sentry/nextjs";

export interface SentryConfig {
  dsn?: string;
  environment?: string;
  tracesSampleRate?: number;
  enabled?: boolean;
}

/**
 * Initialize Sentry for server-side
 */
export function initSentryServer(config?: SentryConfig): void {
  if (!config?.enabled || !config?.dsn) {
    console.log("Sentry disabled or DSN not configured");
    return;
  }

  Sentry.init({
    dsn: config.dsn,
    environment: config.environment || process.env.NODE_ENV || "development",
    tracesSampleRate: config.tracesSampleRate || 0.1,
    enabled: config.enabled,
    
    // Performance monitoring
    integrations: [
      new Sentry.Integrations.Http({ tracing: true }),
    ],

    // Filter out health checks and other noise
    ignoreErrors: [
      "ResizeObserver loop limit exceeded",
      "Non-Error promise rejection captured",
    ],

    // Set sample rate for transactions
    beforeSend(event, hint) {
      // Don't send events in development unless explicitly enabled
      if (process.env.NODE_ENV === "development" && !process.env.SENTRY_DEBUG) {
        return null;
      }
      return event;
    },
  });
}

/**
 * Initialize Sentry for client-side
 */
export function initSentryClient(config?: SentryConfig): void {
  if (!config?.enabled || !config?.dsn) {
    console.log("Sentry disabled or DSN not configured");
    return;
  }

  Sentry.init({
    dsn: config.dsn,
    environment: config.environment || process.env.NODE_ENV || "development",
    tracesSampleRate: config.tracesSampleRate || 0.1,
    enabled: config.enabled,

    // React integration
    integrations: [
      new Sentry.BrowserTracing(),
      new Sentry.Replay({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],

    // Filter out noise
    ignoreErrors: [
      "ResizeObserver loop limit exceeded",
      "Non-Error promise rejection captured",
      "NetworkError",
    ],

    beforeSend(event, hint) {
      // Don't send events in development unless explicitly enabled
      if (process.env.NODE_ENV === "development" && !process.env.SENTRY_DEBUG) {
        return null;
      }
      return event;
    },
  });
}

/**
 * Capture exception manually
 */
export function captureException(error: Error, context?: Record<string, unknown>): void {
  if (context) {
    Sentry.withScope((scope) => {
      Object.entries(context).forEach(([key, value]) => {
        scope.setContext(key, value as Record<string, unknown>);
      });
      Sentry.captureException(error);
    });
  } else {
    Sentry.captureException(error);
  }
}

/**
 * Capture message manually
 */
export function captureMessage(message: string, level: Sentry.SeverityLevel = "info"): void {
  Sentry.captureMessage(message, level);
}

/**
 * Set user context
 */
export function setUserContext(userId: string, email?: string, username?: string): void {
  Sentry.setUser({
    id: userId,
    email,
    username,
  });
}

/**
 * Clear user context
 */
export function clearUserContext(): void {
  Sentry.setUser(null);
}

/**
 * Add breadcrumb
 */
export function addBreadcrumb(message: string, category?: string, level?: Sentry.SeverityLevel, data?: Record<string, unknown>): void {
  Sentry.addBreadcrumb({
    message,
    category,
    level,
    data,
  });
}

/**
 * Set tag
 */
export function setTag(key: string, value: string): void {
  Sentry.setTag(key, value);
}

/**
 * Set context
 */
export function setContext(key: string, context: Record<string, unknown>): void {
  Sentry.setContext(key, context);
}






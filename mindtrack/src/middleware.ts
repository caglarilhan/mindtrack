/**
 * Next.js Middleware
 * Handles security headers, rate limiting, and monitoring
 */

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { hipaaMiddleware } from "./middleware-hipaa";

// Simple in-memory rate limiter (for production, use Redis)
const rateLimitMap = new Map<string, { count: number; resetAt: number }>();

function getRateLimitKey(request: NextRequest): string {
  const ip = request.ip || request.headers.get("x-forwarded-for") || "unknown";
  const path = request.nextUrl.pathname;
  return `${ip}:${path}`;
}

function checkRateLimit(key: string, limit: number, windowMs: number): boolean {
  const now = Date.now();
  const record = rateLimitMap.get(key);

  if (!record || now > record.resetAt) {
    rateLimitMap.set(key, {
      count: 1,
      resetAt: now + windowMs,
    });
    return true;
  }

  if (record.count >= limit) {
    return false;
  }

  record.count++;
  return true;
}

// Clean up old entries periodically
setInterval(() => {
  const now = Date.now();
  for (const [key, record] of rateLimitMap.entries()) {
    if (now > record.resetAt) {
      rateLimitMap.delete(key);
    }
  }
}, 60000); // Clean up every minute

export function middleware(request: NextRequest) {
  // Apply HIPAA middleware first
  const response = hipaaMiddleware(request);
  
  // If HIPAA middleware returned a redirect, return it
  if (response.status === 301 || response.status === 302) {
    return response;
  }

  // Security headers
  response.headers.set("X-DNS-Prefetch-Control", "on");
  response.headers.set("Strict-Transport-Security", "max-age=63072000; includeSubDomains; preload");
  response.headers.set("X-Frame-Options", "SAMEORIGIN");
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("X-XSS-Protection", "1; mode=block");
  response.headers.set("Referrer-Policy", "origin-when-cross-origin");
  response.headers.set("Permissions-Policy", "camera=(), microphone=(), geolocation=()");

  // API rate limiting
  if (request.nextUrl.pathname.startsWith("/api/")) {
    const rateLimitKey = getRateLimitKey(request);
    
    // Different limits for different endpoints
    let limit = 100; // Default: 100 requests
    let windowMs = 60000; // Per minute

    if (request.nextUrl.pathname.startsWith("/api/ai/")) {
      limit = 20; // AI endpoints: 20 requests per minute
    } else if (request.nextUrl.pathname.startsWith("/api/email/")) {
      limit = 30; // Email endpoints: 30 requests per minute
    } else if (request.nextUrl.pathname.startsWith("/api/telehealth/")) {
      limit = 50; // Telehealth endpoints: 50 requests per minute
    }

    if (!checkRateLimit(rateLimitKey, limit, windowMs)) {
      return NextResponse.json(
        { error: "Too many requests. Please try again later." },
        { status: 429 }
      );
    }

    // Add rate limit headers
    const record = rateLimitMap.get(rateLimitKey);
    if (record) {
      response.headers.set("X-RateLimit-Limit", limit.toString());
      response.headers.set("X-RateLimit-Remaining", Math.max(0, limit - record.count).toString());
      response.headers.set("X-RateLimit-Reset", Math.ceil(record.resetAt / 1000).toString());
    }
  }

  return response;
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    "/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)",
  ],
};


/**
 * HIPAA-Compliant Middleware
 * Adds security headers and enforces HTTPS
 */

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function hipaaMiddleware(request: NextRequest) {
  const response = NextResponse.next();

  // Force HTTPS in production
  if (process.env.NODE_ENV === "production") {
    const protocol = request.headers.get("x-forwarded-proto");
    if (protocol !== "https") {
      return NextResponse.redirect(
        `https://${request.headers.get("host")}${request.nextUrl.pathname}`,
        301
      );
    }
  }

  // HIPAA Security Headers
  response.headers.set("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload");
  response.headers.set("X-Content-Type-Options", "nosniff");
  response.headers.set("X-Frame-Options", "DENY");
  response.headers.set("X-XSS-Protection", "1; mode=block");
  response.headers.set("Referrer-Policy", "no-referrer");
  response.headers.set("Permissions-Policy", "geolocation=(), microphone=(), camera=()");
  
  // Content Security Policy
  const csp = [
    "default-src 'self'",
    "script-src 'self' 'unsafe-eval' 'unsafe-inline'",
    "style-src 'self' 'unsafe-inline'",
    "img-src 'self' data: https:",
    "font-src 'self' data:",
    "connect-src 'self' https://*.supabase.co https://*.openai.com https://*.googleapis.com",
    "frame-ancestors 'none'",
    "base-uri 'self'",
    "form-action 'self'",
  ].join("; ");

  response.headers.set("Content-Security-Policy", csp);

  return response;
}






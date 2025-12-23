/**
 * Health check endpoint
 * Returns application health status
 */

import { NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";
import { performanceMonitor } from "@/lib/monitoring/performance";

export async function GET() {
  const startTime = Date.now();
  const health: {
    status: "healthy" | "degraded" | "unhealthy";
    timestamp: string;
    uptime: number;
    services: {
      database: "healthy" | "degraded" | "unhealthy";
      api: "healthy" | "degraded" | "unhealthy";
    };
    metrics?: {
      averageResponseTime: number;
      totalRequests: number;
    };
  } = {
    status: "healthy",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    services: {
      database: "healthy",
      api: "healthy",
    },
  };

  try {
    // Check database connection
    const supabase = await createClient();
    const { error: dbError } = await supabase.from("profiles").select("id").limit(1);

    if (dbError) {
      health.services.database = "unhealthy";
      health.status = "degraded";
    }

    // Get performance metrics
    const allMetrics = performanceMonitor.getAllMetrics();
    let totalRequests = 0;
    let totalDuration = 0;

    for (const metrics of allMetrics.values()) {
      totalRequests += metrics.length;
      totalDuration += metrics.reduce((sum, m) => sum + m.duration, 0);
    }

    health.metrics = {
      averageResponseTime: totalRequests > 0 ? totalDuration / totalRequests : 0,
      totalRequests,
    };

    // Check if response time is too high
    if (health.metrics.averageResponseTime > 5000) {
      health.services.api = "degraded";
      health.status = "degraded";
    }

    const responseTime = Date.now() - startTime;
    
    return NextResponse.json(health, {
      status: health.status === "unhealthy" ? 503 : health.status === "degraded" ? 200 : 200,
      headers: {
        "X-Response-Time": `${responseTime}ms`,
      },
    });
  } catch (error) {
    health.status = "unhealthy";
    health.services.database = "unhealthy";
    health.services.api = "unhealthy";

    return NextResponse.json(health, { status: 503 });
  }
}






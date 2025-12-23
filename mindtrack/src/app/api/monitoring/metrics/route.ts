/**
 * Metrics endpoint
 * Returns application performance metrics
 */

import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";
import { performanceMonitor } from "@/lib/monitoring/performance";

export async function GET(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Check if user is admin (you may want to add an admin check here)
    // For now, allow all authenticated users

    const { searchParams } = new URL(request.url);
    const metricName = searchParams.get("name");

    const allMetrics = performanceMonitor.getAllMetrics();

    if (metricName) {
      const metrics = performanceMonitor.getMetrics(metricName);
      const average = performanceMonitor.getAverageDuration(metricName);

      return NextResponse.json({
        success: true,
        metric: metricName,
        data: {
          count: metrics.length,
          averageDuration: average,
          metrics: metrics.slice(-100), // Last 100 metrics
        },
      });
    }

    // Return summary of all metrics
    const summary: Record<string, { count: number; averageDuration: number }> = {};

    for (const [name, metrics] of allMetrics.entries()) {
      summary[name] = {
        count: metrics.length,
        averageDuration: performanceMonitor.getAverageDuration(name),
      };
    }

    return NextResponse.json({
      success: true,
      summary,
      totalMetrics: Array.from(allMetrics.values()).reduce((sum, m) => sum + m.length, 0),
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Get metrics error:", error);
    return NextResponse.json({
      error: errorMessage,
    }, { status: 500 });
  }
}






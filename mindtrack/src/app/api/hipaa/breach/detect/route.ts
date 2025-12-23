/**
 * Breach Detection API
 * Automated breach detection from audit logs
 */

import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";
import { detectPotentialBreaches, assessBreach, createBreachRecord } from "@/lib/hipaa/breach-detection";
import { isAdmin } from "@/lib/hipaa/access-control";
import { logDataAccess } from "@/lib/hipaa/audit-log";

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Only admins can trigger breach detection
    const userIsAdmin = await isAdmin(user.id);
    if (!userIsAdmin) {
      return NextResponse.json({ error: "Forbidden - Admin access required" }, { status: 403 });
    }

    const body = await request.json();
    const { timeWindowHours = 24 } = body;

    const ipAddress = request.headers.get("x-forwarded-for") || undefined;
    const userAgent = request.headers.get("user-agent") || undefined;

    // Log access
    await logDataAccess(user.id, "breach_detection", "system", ipAddress, userAgent, true);

    // Detect potential breaches
    const breaches = await detectPotentialBreaches(timeWindowHours);

    // Assess and create breach records
    const results = await Promise.all(
      breaches.map(async (breach) => {
        const assessment = assessBreach(breach);
        const createResult = await createBreachRecord(breach);

        return {
          breach,
          assessment,
          created: createResult.success,
          breachId: createResult.breachId,
        };
      })
    );

    return NextResponse.json({
      success: true,
      detectedBreaches: breaches.length,
      breaches: results,
      timestamp: new Date().toISOString(),
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Breach detection API error:", error);
    return NextResponse.json(
      {
        error: "Failed to detect breaches",
        details: errorMessage,
      },
      { status: 500 }
    );
  }
}






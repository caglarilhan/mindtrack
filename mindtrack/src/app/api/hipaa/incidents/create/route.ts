/**
 * Create Security Incident API
 */

import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";
import { createSecurityIncident } from "@/lib/hipaa/incident-response";
import { logDataAccess } from "@/lib/hipaa/audit-log";

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { type, severity, title, description, affectedSystems, affectedUsers, impact, metadata } = body;

    if (!type || !severity || !title || !description) {
      return NextResponse.json(
        { error: "Missing required fields: type, severity, title, description" },
        { status: 400 }
      );
    }

    const ipAddress = request.headers.get("x-forwarded-for") || undefined;
    const userAgent = request.headers.get("user-agent") || undefined;

    // Log access
    await logDataAccess(user.id, "incident_create", "system", ipAddress, userAgent, true);

    const result = await createSecurityIncident(
      {
        type,
        severity,
        title,
        description,
        affectedSystems,
        affectedUsers,
        impact,
        metadata,
      },
      user.id
    );

    if (!result.success) {
      return NextResponse.json(
        { error: result.error || "Failed to create security incident" },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      incidentId: result.incidentId,
      message: "Security incident created successfully",
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Create incident API error:", error);
    return NextResponse.json(
      {
        error: "Failed to create security incident",
        details: errorMessage,
      },
      { status: 500 }
    );
  }
}






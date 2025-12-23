/**
 * Create Consent Form API
 */

import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";
import { createConsentForm } from "@/lib/hipaa/consent-management";
import { logDataAccess } from "@/lib/hipaa/audit-log";

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { patientId, consentType, description, expiresInDays } = body;

    if (!patientId || !consentType || !description) {
      return NextResponse.json(
        { error: "Missing required fields: patientId, consentType, description" },
        { status: 400 }
      );
    }

    const ipAddress = request.headers.get("x-forwarded-for") || undefined;
    const userAgent = request.headers.get("user-agent") || undefined;

    // Log access
    await logDataAccess(user.id, "consent_create", patientId, ipAddress, userAgent, true);

    const result = await createConsentForm(
      {
        patientId,
        consentType,
        description,
        expiresInDays,
      },
      user.id
    );

    if (!result.success) {
      return NextResponse.json(
        { error: result.error || "Failed to create consent form" },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      consentId: result.consentId,
      message: "Consent form created successfully",
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Create consent API error:", error);
    return NextResponse.json(
      {
        error: "Failed to create consent form",
        details: errorMessage,
      },
      { status: 500 }
    );
  }
}






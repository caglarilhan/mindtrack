/**
 * Sign Consent Form API
 */

import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";
import { signConsentForm } from "@/lib/hipaa/consent-management";

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { consentId, signature, patientId } = body;

    if (!consentId || !signature || !patientId) {
      return NextResponse.json(
        { error: "Missing required fields: consentId, signature, patientId" },
        { status: 400 }
      );
    }

    if (!signature.name || !signature.signatureData) {
      return NextResponse.json(
        { error: "Signature must include name and signatureData" },
        { status: 400 }
      );
    }

    const ipAddress = request.headers.get("x-forwarded-for") || undefined;
    const userAgent = request.headers.get("user-agent") || undefined;

    const result = await signConsentForm(
      consentId,
      {
        ...signature,
        ipAddress,
        userAgent,
      },
      patientId
    );

    if (!result.success) {
      return NextResponse.json(
        { error: result.error || "Failed to sign consent form" },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      message: "Consent form signed successfully",
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Sign consent API error:", error);
    return NextResponse.json(
      {
        error: "Failed to sign consent form",
        details: errorMessage,
      },
      { status: 500 }
    );
  }
}






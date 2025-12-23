/**
 * MFA Verification API
 * Verify MFA code and enable MFA
 */

import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";
import { verifyMFA, enableMFA } from "@/lib/auth/mfa";

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { method, code, methodId, enableAfterVerify = false } = body;

    if (!method || !code) {
      return NextResponse.json(
        { error: "method and code are required" },
        { status: 400 }
      );
    }

    if (!["totp", "sms", "email", "backup"].includes(method)) {
      return NextResponse.json(
        { error: "Invalid method" },
        { status: 400 }
      );
    }

    const ipAddress = request.headers.get("x-forwarded-for") || undefined;
    const userAgent = request.headers.get("user-agent") || undefined;

    // Verify MFA code
    const verification = await verifyMFA(user.id, method, code, ipAddress, userAgent);

    if (!verification.success) {
      return NextResponse.json(
        { error: verification.error || "Verification failed" },
        { status: 400 }
      );
    }

    if (!verification.verified) {
      return NextResponse.json(
        { error: "Invalid code" },
        { status: 401 }
      );
    }

    // Enable MFA if requested
    if (enableAfterVerify && methodId) {
      const enableResult = await enableMFA(user.id, methodId);
      if (!enableResult.success) {
        return NextResponse.json(
          { error: enableResult.error || "Failed to enable MFA" },
          { status: 500 }
        );
      }
    }

    return NextResponse.json({
      success: true,
      verified: true,
      message: "MFA verification successful",
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("MFA verification API error:", error);
    return NextResponse.json(
      {
        error: "Failed to verify MFA",
        details: errorMessage,
      },
      { status: 500 }
    );
  }
}






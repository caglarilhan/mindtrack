/**
 * MFA Setup API
 * Setup multi-factor authentication for user
 */

import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";
import { setupMFA } from "@/lib/auth/mfa";
import { logDataAccess } from "@/lib/hipaa/audit-log";

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { method, contactInfo } = body;

    if (!method || !["totp", "sms", "email"].includes(method)) {
      return NextResponse.json(
        { error: "Invalid method. Must be 'totp', 'sms', or 'email'" },
        { status: 400 }
      );
    }

    if ((method === "sms" || method === "email") && !contactInfo) {
      return NextResponse.json(
        { error: "contactInfo is required for SMS/Email method" },
        { status: 400 }
      );
    }

    const ipAddress = request.headers.get("x-forwarded-for") || undefined;
    const userAgent = request.headers.get("user-agent") || undefined;

    // Log access
    await logDataAccess(user.id, "mfa_setup", user.id, ipAddress, userAgent, true);

    const result = await setupMFA(user.id, method, contactInfo);

    if (!result.success) {
      return NextResponse.json(
        { error: result.error || "Failed to setup MFA" },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      method,
      secret: result.secret, // Only for TOTP
      qrCodeUrl: result.qrCodeUrl, // Only for TOTP
      backupCodes: result.backupCodes, // Only for TOTP
      message: "MFA setup successful. Please verify to enable.",
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("MFA setup API error:", error);
    return NextResponse.json(
      {
        error: "Failed to setup MFA",
        details: errorMessage,
      },
      { status: 500 }
    );
  }
}






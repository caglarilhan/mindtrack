/**
 * Send OTP Code API
 * Send OTP code via SMS or Email
 */

import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";
import { generateOTPCode } from "@/lib/auth/mfa";
import { sendEmail } from "@/lib/email";
import { logDataModification } from "@/lib/hipaa/audit-log";

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { method, contactInfo } = body;

    if (!method || !["sms", "email"].includes(method)) {
      return NextResponse.json(
        { error: "Invalid method. Must be 'sms' or 'email'" },
        { status: 400 }
      );
    }

    if (!contactInfo) {
      return NextResponse.json(
        { error: "contactInfo is required" },
        { status: 400 }
      );
    }

    // Generate OTP code
    const otpCode = generateOTPCode(6);
    const expiresAt = new Date(Date.now() + 10 * 60 * 1000); // 10 minutes

    // Store OTP code
    const { error: storeError } = await supabase.from("mfa_otp_codes").insert({
      user_id: user.id,
      method,
      code: otpCode,
      contact_info: contactInfo,
      expires_at: expiresAt.toISOString(),
    });

    if (storeError) {
      throw new Error(`Failed to store OTP: ${storeError.message}`);
    }

    // Send OTP
    if (method === "email") {
      const emailResult = await sendEmail({
        to: contactInfo,
        subject: "MindTrack - MFA Verification Code",
        html: `
          <div style="font-family: Arial, sans-serif; padding: 20px;">
            <h2>MFA Verification Code</h2>
            <p>Your verification code is:</p>
            <div style="font-size: 32px; font-weight: bold; color: #4f46e5; padding: 20px; text-align: center; background-color: #f3f4f6; border-radius: 8px; margin: 20px 0;">
              ${otpCode}
            </div>
            <p style="color: #6b7280; font-size: 14px;">This code will expire in 10 minutes.</p>
            <p style="color: #6b7280; font-size: 14px;">If you didn't request this code, please ignore this email.</p>
          </div>
        `,
        text: `Your MFA verification code is: ${otpCode}. This code will expire in 10 minutes.`,
      });

      if (!emailResult.success) {
        return NextResponse.json(
          { error: "Failed to send email" },
          { status: 500 }
        );
      }
    } else if (method === "sms") {
      // TODO: Implement SMS sending (Twilio, etc.)
      // For now, return code in response (NOT for production!)
      console.log(`SMS OTP for ${contactInfo}: ${otpCode}`);
    }

    // Log OTP send
    await logDataModification(
      user.id,
      "create",
      "mfa_otp_send",
      user.id,
      undefined,
      undefined,
      true,
      { method, contactInfo: method === "sms" ? "***" : contactInfo }
    );

    return NextResponse.json({
      success: true,
      message: method === "email" ? "OTP code sent to email" : "OTP code generated",
      // In production, don't return code for SMS
      ...(method === "sms" ? { code: otpCode } : {}), // REMOVE IN PRODUCTION!
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Send OTP API error:", error);
    return NextResponse.json(
      {
        error: "Failed to send OTP",
        details: errorMessage,
      },
      { status: 500 }
    );
  }
}






/**
 * Email test endpoint
 * Test email service configuration
 */

import { NextRequest, NextResponse } from "next/server";
import { sendEmail } from "@/lib/email";
import { isEmailConfigured } from "@/lib/email/config";

export async function GET(request: NextRequest) {
  try {
    const configured = isEmailConfigured();
    
    if (!configured) {
      return NextResponse.json({
        success: false,
        error: "Email service not configured",
        message: "Set EMAIL_PROVIDER and required API keys in environment variables",
      }, { status: 400 });
    }

    return NextResponse.json({
      success: true,
      message: "Email service is configured",
      configured: true,
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json({
      success: false,
      error: errorMessage,
    }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const { to, subject, html } = await request.json();

    if (!to || !subject || !html) {
      return NextResponse.json({
        success: false,
        error: "Missing required fields: to, subject, html",
      }, { status: 400 });
    }

    const result = await sendEmail({
      to,
      subject,
      html,
    });

    if (!result.success) {
      return NextResponse.json({
        success: false,
        error: result.error,
      }, { status: 500 });
    }

    return NextResponse.json({
      success: true,
      messageId: result.messageId,
      message: "Email sent successfully",
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json({
      success: false,
      error: errorMessage,
    }, { status: 500 });
  }
}






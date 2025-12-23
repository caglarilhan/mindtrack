/**
 * Email status API endpoint
 * Update email status (webhook handler for email providers)
 */

import { NextRequest, NextResponse } from "next/server";
import { updateEmailStatus } from "@/lib/email/history";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { messageId, status, errorMessage, deliveredAt, openedAt, clickedAt } = body;

    if (!messageId || !status) {
      return NextResponse.json({
        error: "Missing required fields: messageId, status",
      }, { status: 400 });
    }

    await updateEmailStatus(messageId, status, {
      errorMessage,
      deliveredAt,
      openedAt,
      clickedAt,
    });

    return NextResponse.json({
      success: true,
      message: "Email status updated",
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Update email status error:", error);
    return NextResponse.json({
      error: errorMessage,
    }, { status: 500 });
  }
}






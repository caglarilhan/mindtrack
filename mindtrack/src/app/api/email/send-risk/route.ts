/**
 * Send risk alert via email
 */

import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";
import { sendEmail } from "@/lib/email";
import { EMAIL_TEMPLATES } from "@/lib/email/templates";

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { riskLogId, recipientEmails } = await request.json();

    if (!riskLogId || !recipientEmails || !Array.isArray(recipientEmails) || recipientEmails.length === 0) {
      return NextResponse.json({
        error: "Missing required fields: riskLogId, recipientEmails",
      }, { status: 400 });
    }

    // Fetch risk log
    const { data: riskLog, error: riskError } = await supabase
      .from("risk_logs")
      .select("*, clients(name)")
      .eq("id", riskLogId)
      .single();

    if (riskError || !riskLog) {
      return NextResponse.json({
        error: "Risk log not found",
      }, { status: 404 });
    }

    // Prepare email data
    const emailData = EMAIL_TEMPLATES.riskAlert({
      clientName: (riskLog.clients as { name: string })?.name || "Danışan",
      riskLevel: riskLog.risk_level as "low" | "medium" | "high" | "critical",
      detectedKeywords: riskLog.detected_keywords || [],
      contextSnippet: riskLog.context_snippet || undefined,
      sessionDate: riskLog.logged_at,
      recommendedActions: riskLog.risk_level === "critical" || riskLog.risk_level === "high"
        ? [
            "Acil durum protokolünü aktifleştirin",
            "Danışanla iletişime geçin",
            "Gerekirse acil servisleri arayın",
            "Durumu dokümente edin",
          ]
        : [
            "Durumu değerlendirin",
            "Sonraki seansta konuyu ele alın",
            "Danışanla iletişim kurun",
          ],
    });

    // Send email with history tracking
    const result = await sendEmail({
      to: recipientEmails,
      subject: emailData.subject,
      html: emailData.html,
      text: emailData.text,
    }, {
      trackHistory: true,
      userId: user.id,
      emailType: "risk",
      relatedId: riskLogId,
      relatedType: "risk_log",
    });

    if (!result.success) {
      return NextResponse.json({
        error: result.error || "Failed to send email",
      }, { status: 500 });
    }

    return NextResponse.json({
      success: true,
      messageId: result.messageId,
      message: "Risk alert email sent successfully",
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Send risk email error:", error);
    return NextResponse.json({
      error: errorMessage,
    }, { status: 500 });
  }
}


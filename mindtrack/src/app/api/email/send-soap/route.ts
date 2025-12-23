/**
 * Send SOAP note via email
 */

import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";
import { sendEmail } from "@/lib/email";
import { EMAIL_TEMPLATES } from "@/lib/email/templates";
import { decryptNote } from "@/lib/crypto";
import { generateSOAPPDF } from "@/lib/pdf/soap-pdf";

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { noteId, recipientEmails, includePDF } = await request.json();

    if (!noteId || !recipientEmails || !Array.isArray(recipientEmails) || recipientEmails.length === 0) {
      return NextResponse.json({
        error: "Missing required fields: noteId, recipientEmails",
      }, { status: 400 });
    }

    // Fetch SOAP note
    const { data: note, error: noteError } = await supabase
      .from("notes")
      .select("*, clients(name)")
      .eq("id", noteId)
      .eq("type", "SOAP")
      .single();

    if (noteError || !note) {
      return NextResponse.json({
        error: "SOAP note not found",
      }, { status: 404 });
    }

    // Decrypt note content
    const decryptedContent = await decryptNote(note.content_encrypted);
    
    // Parse SOAP sections
    const subjective = decryptedContent.match(/S:\s*([\s\S]*?)(?=\n\nO:|$)/)?.[1]?.trim() || "";
    const objective = decryptedContent.match(/O:\s*([\s\S]*?)(?=\n\nA:|$)/)?.[1]?.trim() || "";
    const assessment = decryptedContent.match(/A:\s*([\s\S]*?)(?=\n\nP:|$)/)?.[1]?.trim() || "";
    const plan = decryptedContent.match(/P:\s*([\s\S]*?)(?=$)/)?.[1]?.trim() || "";

    // Get risk level from metadata
    const riskLevel = (note.metadata as Record<string, unknown>)?.riskLevel as "low" | "medium" | "high" | "critical" | undefined;

    // Prepare email data
    const emailData = EMAIL_TEMPLATES.soapNote({
      clientName: (note.clients as { name: string })?.name || "Danışan",
      date: note.created_at,
      soap: {
        subjective,
        objective,
        assessment,
        plan,
      },
      riskLevel,
    });

    // Generate PDF if includePDF is true
    let attachments = undefined;
    if (includePDF) {
      try {
        const pdfBuffer = await generateSOAPPDF({
          clientName: (note.clients as { name: string })?.name || "Danışan",
          date: note.created_at,
          soap: {
            subjective,
            objective,
            assessment,
            plan,
          },
          riskLevel,
        });

        attachments = [
          {
            filename: `SOAP-${(note.clients as { name: string })?.name || "Danışan"}-${new Date(note.created_at).toISOString().split("T")[0]}.pdf`,
            content: pdfBuffer,
            contentType: "application/pdf",
          },
        ];
      } catch (pdfError) {
        console.error("PDF generation error:", pdfError);
        // Continue without PDF attachment
      }
    }

    // Send email with history tracking
    const result = await sendEmail({
      to: recipientEmails,
      subject: emailData.subject,
      html: emailData.html,
      text: emailData.text,
      attachments,
    }, {
      trackHistory: true,
      userId: user.id,
      emailType: "soap",
      relatedId: noteId,
      relatedType: "soap_note",
    });

    if (!result.success) {
      return NextResponse.json({
        error: result.error || "Failed to send email",
      }, { status: 500 });
    }

    return NextResponse.json({
      success: true,
      messageId: result.messageId,
      message: "SOAP note email sent successfully",
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Send SOAP email error:", error);
    return NextResponse.json({
      error: errorMessage,
    }, { status: 500 });
  }
}


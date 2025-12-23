/**
 * Transactional email notifications
 * Integrated with Resend, SendGrid, or SMTP
 */

import { sendEmail, type EmailMessage } from "@/lib/email";

export interface EmailOptions {
  to: string | string[];
  subject: string;
  html: string;
  text?: string;
  from?: string;
  cc?: string | string[];
  bcc?: string | string[];
  attachments?: Array<{
    filename: string;
    content: Buffer | string;
    contentType?: string;
  }>;
}

export async function sendTransactionalEmail(options: EmailOptions): Promise<{ success: boolean; message?: string; messageId?: string }> {
  try {
    const message: EmailMessage = {
      to: options.to,
      subject: options.subject,
      html: options.html,
      text: options.text,
      cc: options.cc,
      bcc: options.bcc,
      attachments: options.attachments,
    };

    const result = await sendEmail(message);
    
    if (!result.success) {
      console.error("[Notifications] Email send failed:", result.error);
      return { 
        success: false, 
        message: result.error || "Email send failed" 
      };
    }

    return { 
      success: true, 
      message: "Email sent", 
      messageId: result.messageId 
    };
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Email send failed";
    console.error("[Notifications] Email error:", error);
    return { 
      success: false, 
      message: errorMessage 
    };
  }
}

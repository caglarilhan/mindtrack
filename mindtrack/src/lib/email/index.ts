/**
 * Email service factory
 * Automatically selects the best available email provider
 */

import { getEmailConfig, isEmailConfigured, type EmailConfig } from "./config";
import { ResendEmailService } from "./resend-service";
import { SendGridEmailService } from "./sendgrid-service";
import { SMTPEmailService } from "./smtp-service";
import type { EmailMessage } from "./resend-service";

// Re-export history functions
export { createEmailHistory, updateEmailStatus, getEmailHistory, getEmailStats } from "./history";
export type { EmailHistoryEntry } from "./history";

export type { EmailMessage } from "./resend-service";

export interface EmailService {
  sendEmail(message: EmailMessage): Promise<{ success: boolean; messageId?: string; error?: string }>;
}

/**
 * Get email service instance based on configuration
 */
export function getEmailService(): EmailService | null {
  if (!isEmailConfigured()) {
    console.warn("⚠️ Email service not configured. Set EMAIL_PROVIDER and required API keys.");
    return null;
  }

  const config = getEmailConfig();

  switch (config.provider) {
    case "resend":
      return new ResendEmailService(config);
    case "sendgrid":
      return new SendGridEmailService(config);
    case "smtp":
      return new SMTPEmailService(config);
    default:
      console.warn(`⚠️ Unknown email provider: ${config.provider}`);
      return null;
  }
}

/**
 * Send email using the configured provider
 * Optionally tracks email history
 */
export async function sendEmail(
  message: EmailMessage,
  options?: {
    trackHistory?: boolean;
    userId?: string;
    emailType?: "soap" | "risk" | "appointment" | "share" | "other";
    relatedId?: string;
    relatedType?: "soap_note" | "risk_log" | "appointment" | "share_link";
  }
): Promise<{ success: boolean; messageId?: string; error?: string }> {
  const service = getEmailService();
  
  if (!service) {
    return {
      success: false,
      error: "Email service not configured",
    };
  }

  const config = getEmailConfig();
  const result = await service.sendEmail(message);

  // Track email history if enabled
  if (options?.trackHistory && options?.userId && result.success && result.messageId) {
    try {
      const { createEmailHistory } = await import("./history");
      await createEmailHistory({
        userId: options.userId,
        recipientEmails: Array.isArray(message.to) ? message.to : [message.to],
        subject: message.subject,
        emailType: options.emailType || "other",
        relatedId: options.relatedId,
        relatedType: options.relatedType,
        provider: config.provider,
        messageId: result.messageId,
        status: "sent",
      });
    } catch (historyError) {
      console.error("Failed to track email history:", historyError);
      // Don't fail the email send if history tracking fails
    }
  }

  return result;
}


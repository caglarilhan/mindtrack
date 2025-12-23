/**
 * Resend email service implementation
 * https://resend.com
 */

import { Resend } from "resend";
import type { EmailConfig } from "./config";

export interface EmailMessage {
  to: string | string[];
  subject: string;
  html: string;
  text?: string;
  attachments?: Array<{
    filename: string;
    content: Buffer | string;
    contentType?: string;
  }>;
  cc?: string | string[];
  bcc?: string | string[];
  replyTo?: string;
}

export class ResendEmailService {
  private client: Resend | null = null;
  private config: EmailConfig;

  constructor(config: EmailConfig) {
    this.config = config;
    
    if (config.apiKey) {
      try {
        this.client = new Resend(config.apiKey);
      } catch (error) {
        console.error("Failed to initialize Resend client:", error);
      }
    }
  }

  async sendEmail(message: EmailMessage): Promise<{ success: boolean; messageId?: string; error?: string }> {
    if (!this.client) {
      return {
        success: false,
        error: "Resend client not initialized. Check RESEND_API_KEY environment variable.",
      };
    }

    try {
      const recipients = Array.isArray(message.to) ? message.to : [message.to];
      
      const result = await this.client.emails.send({
        from: `${this.config.fromName || "MindTrack"} <${this.config.fromEmail || "noreply@mindtrack.app"}>`,
        to: recipients,
        subject: message.subject,
        html: message.html,
        text: message.text,
        cc: message.cc ? (Array.isArray(message.cc) ? message.cc : [message.cc]) : undefined,
        bcc: message.bcc ? (Array.isArray(message.bcc) ? message.bcc : [message.bcc]) : undefined,
        reply_to: message.replyTo,
        attachments: message.attachments?.map(att => ({
          filename: att.filename,
          content: typeof att.content === "string" ? Buffer.from(att.content) : att.content,
          contentType: att.contentType,
        })),
      });

      return {
        success: true,
        messageId: result.id,
      };
    } catch (error: unknown) {
      console.error("Resend email error:", error);
      const errorMessage = error instanceof Error ? error.message : "Failed to send email via Resend";
      return {
        success: false,
        error: errorMessage,
      };
    }
  }
}


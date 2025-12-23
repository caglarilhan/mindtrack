/**
 * SendGrid email service implementation
 * https://sendgrid.com
 */

import sgMail from "@sendgrid/mail";
import type { EmailConfig } from "./config";
import type { EmailMessage } from "./resend-service";

export class SendGridEmailService {
  private config: EmailConfig;
  private initialized = false;

  constructor(config: EmailConfig) {
    this.config = config;
    
    if (config.apiKey) {
      try {
        sgMail.setApiKey(config.apiKey);
        this.initialized = true;
      } catch (error) {
        console.error("Failed to initialize SendGrid client:", error);
      }
    }
  }

  async sendEmail(message: EmailMessage): Promise<{ success: boolean; messageId?: string; error?: string }> {
    if (!this.initialized) {
      return {
        success: false,
        error: "SendGrid client not initialized. Check SENDGRID_API_KEY environment variable.",
      };
    }

    try {
      const recipients = Array.isArray(message.to) ? message.to : [message.to];
      
      const msg = {
        to: recipients,
        from: {
          email: this.config.fromEmail || "noreply@mindtrack.app",
          name: this.config.fromName || "MindTrack",
        },
        subject: message.subject,
        html: message.html,
        text: message.text,
        cc: message.cc ? (Array.isArray(message.cc) ? message.cc : [message.cc]) : undefined,
        bcc: message.bcc ? (Array.isArray(message.bcc) ? message.bcc : [message.bcc]) : undefined,
        replyTo: message.replyTo,
        attachments: message.attachments?.map(att => ({
          filename: att.filename,
          content: typeof att.content === "string" ? att.content : att.content.toString("base64"),
          type: att.contentType,
          disposition: "attachment",
        })),
      };

      const [result] = await sgMail.send(msg);

      return {
        success: true,
        messageId: result.headers["x-message-id"] as string,
      };
    } catch (error: unknown) {
      console.error("SendGrid email error:", error);
      const errorMessage = error instanceof Error ? error.message : "Failed to send email via SendGrid";
      return {
        success: false,
        error: errorMessage,
      };
    }
  }
}


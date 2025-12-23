/**
 * SMTP email service implementation
 * Uses nodemailer for SMTP
 */

import nodemailer from "nodemailer";
import type { EmailConfig } from "./config";
import type { EmailMessage } from "./resend-service";

export class SMTPEmailService {
  private transporter: nodemailer.Transporter | null = null;
  private config: EmailConfig;

  constructor(config: EmailConfig) {
    this.config = config;
    
    if (config.smtpHost && config.smtpUser && config.smtpPassword) {
      try {
        this.transporter = nodemailer.createTransport({
          host: config.smtpHost,
          port: config.smtpPort || 587,
          secure: config.smtpPort === 465,
          auth: {
            user: config.smtpUser,
            pass: config.smtpPassword,
          },
        });
      } catch (error) {
        console.error("Failed to initialize SMTP transporter:", error);
      }
    }
  }

  async sendEmail(message: EmailMessage): Promise<{ success: boolean; messageId?: string; error?: string }> {
    if (!this.transporter) {
      return {
        success: false,
        error: "SMTP transporter not initialized. Check SMTP configuration environment variables.",
      };
    }

    try {
      const recipients = Array.isArray(message.to) ? message.to : [message.to];
      
      const mailOptions = {
        from: `"${this.config.fromName || "MindTrack"}" <${this.config.fromEmail || "noreply@mindtrack.app"}>`,
        to: recipients.join(", "),
        subject: message.subject,
        html: message.html,
        text: message.text,
        cc: message.cc ? (Array.isArray(message.cc) ? message.cc.join(", ") : message.cc) : undefined,
        bcc: message.bcc ? (Array.isArray(message.bcc) ? message.bcc.join(", ") : message.bcc) : undefined,
        replyTo: message.replyTo,
        attachments: message.attachments?.map(att => ({
          filename: att.filename,
          content: typeof att.content === "string" ? att.content : att.content,
          contentType: att.contentType,
        })),
      };

      const result = await this.transporter.sendMail(mailOptions);

      return {
        success: true,
        messageId: result.messageId,
      };
    } catch (error: unknown) {
      console.error("SMTP email error:", error);
      const errorMessage = error instanceof Error ? error.message : "Failed to send email via SMTP";
      return {
        success: false,
        error: errorMessage,
      };
    }
  }
}


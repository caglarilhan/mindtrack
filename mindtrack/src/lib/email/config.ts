/**
 * Email service configuration
 * Supports multiple providers: Resend, SendGrid, SMTP
 */

export type EmailProvider = "resend" | "sendgrid" | "smtp";

export interface EmailConfig {
  provider: EmailProvider;
  apiKey?: string;
  fromEmail?: string;
  fromName?: string;
  smtpHost?: string;
  smtpPort?: number;
  smtpUser?: string;
  smtpPassword?: string;
}

/**
 * Get email configuration from environment variables
 */
export function getEmailConfig(): EmailConfig {
  const provider = (process.env.EMAIL_PROVIDER || "resend") as EmailProvider;
  
  return {
    provider,
    apiKey: process.env.RESEND_API_KEY || process.env.SENDGRID_API_KEY,
    fromEmail: process.env.EMAIL_FROM || "noreply@mindtrack.app",
    fromName: process.env.EMAIL_FROM_NAME || "MindTrack",
    smtpHost: process.env.SMTP_HOST,
    smtpPort: parseInt(process.env.SMTP_PORT || "587", 10),
    smtpUser: process.env.SMTP_USER,
    smtpPassword: process.env.SMTP_PASSWORD,
  };
}

/**
 * Check if email is configured
 */
export function isEmailConfigured(): boolean {
  const config = getEmailConfig();
  
  if (config.provider === "resend" || config.provider === "sendgrid") {
    return !!config.apiKey;
  }
  
  if (config.provider === "smtp") {
    return !!(config.smtpHost && config.smtpUser && config.smtpPassword);
  }
  
  return false;
}






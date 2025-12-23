/**
 * Email history tracking
 * Logs all sent emails for audit and monitoring
 */

import { createClient } from "@/utils/supabase/server";

export interface EmailHistoryEntry {
  id: string;
  user_id: string;
  recipient_emails: string[];
  subject: string;
  email_type: "soap" | "risk" | "appointment" | "share" | "other";
  related_id?: string;
  related_type?: "soap_note" | "risk_log" | "appointment" | "share_link";
  provider: "resend" | "sendgrid" | "smtp";
  message_id?: string;
  status: "pending" | "sent" | "delivered" | "bounced" | "failed" | "opened" | "clicked";
  error_message?: string;
  sent_at?: string;
  delivered_at?: string;
  opened_at?: string;
  clicked_at?: string;
  created_at: string;
  updated_at: string;
}

export interface CreateEmailHistoryParams {
  userId: string;
  recipientEmails: string[];
  subject: string;
  emailType: EmailHistoryEntry["email_type"];
  relatedId?: string;
  relatedType?: EmailHistoryEntry["related_type"];
  provider: EmailHistoryEntry["provider"];
  messageId?: string;
  status?: EmailHistoryEntry["status"];
}

/**
 * Create email history entry
 */
export async function createEmailHistory(params: CreateEmailHistoryParams): Promise<EmailHistoryEntry> {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("email_history")
    .insert({
      user_id: params.userId,
      recipient_emails: params.recipientEmails,
      subject: params.subject,
      email_type: params.emailType,
      related_id: params.relatedId || null,
      related_type: params.relatedType || null,
      provider: params.provider,
      message_id: params.messageId || null,
      status: params.status || "pending",
      sent_at: params.status === "sent" ? new Date().toISOString() : null,
    })
    .select()
    .single();

  if (error) {
    throw new Error(`Failed to create email history: ${error.message}`);
  }

  return data as EmailHistoryEntry;
}

/**
 * Update email status
 */
export async function updateEmailStatus(
  messageId: string,
  status: EmailHistoryEntry["status"],
  additionalData?: {
    errorMessage?: string;
    deliveredAt?: string;
    openedAt?: string;
    clickedAt?: string;
  }
): Promise<void> {
  const supabase = await createClient();

  const updateData: Record<string, unknown> = {
    status,
    updated_at: new Date().toISOString(),
  };

  if (status === "sent" && !additionalData?.deliveredAt) {
    updateData.sent_at = new Date().toISOString();
  }

  if (additionalData?.errorMessage) {
    updateData.error_message = additionalData.errorMessage;
  }

  if (additionalData?.deliveredAt) {
    updateData.delivered_at = additionalData.deliveredAt;
  }

  if (additionalData?.openedAt) {
    updateData.opened_at = additionalData.openedAt;
  }

  if (additionalData?.clickedAt) {
    updateData.clicked_at = additionalData.clickedAt;
  }

  const { error } = await supabase
    .from("email_history")
    .update(updateData)
    .eq("message_id", messageId);

  if (error) {
    throw new Error(`Failed to update email status: ${error.message}`);
  }
}

/**
 * Get email history for a user
 */
export async function getEmailHistory(
  userId: string,
  options?: {
    limit?: number;
    offset?: number;
    emailType?: EmailHistoryEntry["email_type"];
    status?: EmailHistoryEntry["status"];
    relatedId?: string;
  }
): Promise<{ data: EmailHistoryEntry[]; total: number }> {
  const supabase = await createClient();

  let query = supabase
    .from("email_history")
    .select("*", { count: "exact" })
    .eq("user_id", userId)
    .order("created_at", { ascending: false });

  if (options?.emailType) {
    query = query.eq("email_type", options.emailType);
  }

  if (options?.status) {
    query = query.eq("status", options.status);
  }

  if (options?.relatedId) {
    query = query.eq("related_id", options.relatedId);
  }

  if (options?.limit) {
    query = query.limit(options.limit);
  }

  if (options?.offset) {
    query = query.range(options.offset, options.offset + (options.limit || 20) - 1);
  }

  const { data, error, count } = await query;

  if (error) {
    throw new Error(`Failed to get email history: ${error.message}`);
  }

  return {
    data: (data || []) as EmailHistoryEntry[],
    total: count || 0,
  };
}

/**
 * Get email statistics
 */
export async function getEmailStats(userId: string): Promise<{
  total: number;
  sent: number;
  delivered: number;
  failed: number;
  opened: number;
  clicked: number;
  byType: Record<string, number>;
}> {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("email_history")
    .select("status, email_type")
    .eq("user_id", userId);

  if (error) {
    throw new Error(`Failed to get email stats: ${error.message}`);
  }

  const stats = {
    total: data?.length || 0,
    sent: 0,
    delivered: 0,
    failed: 0,
    opened: 0,
    clicked: 0,
    byType: {} as Record<string, number>,
  };

  data?.forEach((entry) => {
    if (entry.status === "sent" || entry.status === "delivered" || entry.status === "opened" || entry.status === "clicked") {
      stats.sent++;
    }
    if (entry.status === "delivered" || entry.status === "opened" || entry.status === "clicked") {
      stats.delivered++;
    }
    if (entry.status === "failed" || entry.status === "bounced") {
      stats.failed++;
    }
    if (entry.status === "opened" || entry.status === "clicked") {
      stats.opened++;
    }
    if (entry.status === "clicked") {
      stats.clicked++;
    }

    const type = entry.email_type as string;
    stats.byType[type] = (stats.byType[type] || 0) + 1;
  });

  return stats;
}






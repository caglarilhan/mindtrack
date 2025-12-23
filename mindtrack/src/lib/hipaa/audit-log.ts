/**
 * HIPAA-Compliant Audit Logging
 * Comprehensive audit trail for all PHI access and modifications
 */

import { createClient } from "@/utils/supabase/server";

export type AuditAction =
  | "login"
  | "logout"
  | "read"
  | "create"
  | "update"
  | "delete"
  | "export"
  | "download"
  | "access_denied"
  | "failed_login"
  | "password_change"
  | "role_change";

export interface AuditLogEntry {
  user_id: string;
  action: AuditAction;
  resource_type: string;
  resource_id?: string;
  ip_address?: string;
  user_agent?: string;
  success: boolean;
  error_message?: string;
  metadata?: Record<string, unknown>;
}

/**
 * Create audit log entry
 * HIPAA Requirement: §164.312(b) - Audit Controls
 */
export async function createAuditLog(entry: AuditLogEntry): Promise<void> {
  const supabase = await createClient();

  try {
    const { error } = await supabase.from("audit_logs").insert({
      user_id: entry.user_id,
      action: entry.action,
      resource_type: entry.resource_type,
      resource_id: entry.resource_id || null,
      ip_address: entry.ip_address || null,
      user_agent: entry.user_agent || null,
      success: entry.success,
      error_message: entry.error_message || null,
      metadata: entry.metadata || null,
      created_at: new Date().toISOString(),
    });

    if (error) {
      console.error("Failed to create audit log:", error);
      // Don't throw - audit logging failure shouldn't break the application
      // But log it for monitoring
    }
  } catch (error) {
    console.error("Audit log creation error:", error);
    // Don't throw - audit logging failure shouldn't break the application
  }
}

/**
 * Log user login
 */
export async function logLogin(
  userId: string,
  ipAddress?: string,
  userAgent?: string,
  success: boolean = true,
  errorMessage?: string
): Promise<void> {
  await createAuditLog({
    user_id: userId,
    action: success ? "login" : "failed_login",
    resource_type: "authentication",
    ip_address: ipAddress,
    user_agent: userAgent,
    success,
    error_message: errorMessage,
  });
}

/**
 * Log user logout
 */
export async function logLogout(
  userId: string,
  ipAddress?: string,
  userAgent?: string
): Promise<void> {
  await createAuditLog({
    user_id: userId,
    action: "logout",
    resource_type: "authentication",
    ip_address: ipAddress,
    user_agent: userAgent,
    success: true,
  });
}

/**
 * Log data access (read)
 */
export async function logDataAccess(
  userId: string,
  resourceType: string,
  resourceId?: string,
  ipAddress?: string,
  userAgent?: string,
  success: boolean = true
): Promise<void> {
  await createAuditLog({
    user_id: userId,
    action: "read",
    resource_type: resourceType,
    resource_id: resourceId,
    ip_address: ipAddress,
    user_agent: userAgent,
    success,
  });
}

/**
 * Log data modification (create, update, delete)
 */
export async function logDataModification(
  userId: string,
  action: "create" | "update" | "delete",
  resourceType: string,
  resourceId?: string,
  ipAddress?: string,
  userAgent?: string,
  success: boolean = true,
  metadata?: Record<string, unknown>
): Promise<void> {
  await createAuditLog({
    user_id: userId,
    action,
    resource_type: resourceType,
    resource_id: resourceId,
    ip_address: ipAddress,
    user_agent: userAgent,
    success,
    metadata,
  });
}

/**
 * Log data export/download
 */
export async function logDataExport(
  userId: string,
  resourceType: string,
  resourceId?: string,
  format?: string,
  ipAddress?: string,
  userAgent?: string
): Promise<void> {
  await createAuditLog({
    user_id: userId,
    action: "export",
    resource_type: resourceType,
    resource_id: resourceId,
    ip_address: ipAddress,
    user_agent: userAgent,
    success: true,
    metadata: {
      format,
    },
  });
}

/**
 * Log access denied
 */
export async function logAccessDenied(
  userId: string,
  resourceType: string,
  resourceId?: string,
  reason?: string,
  ipAddress?: string,
  userAgent?: string
): Promise<void> {
  await createAuditLog({
    user_id: userId,
    action: "access_denied",
    resource_type: resourceType,
    resource_id: resourceId,
    ip_address: ipAddress,
    user_agent: userAgent,
    success: false,
    error_message: reason,
  });
}

/**
 * Get audit logs for a user
 */
export async function getAuditLogs(
  userId?: string,
  resourceType?: string,
  startDate?: Date,
  endDate?: Date,
  limit: number = 100
): Promise<AuditLogEntry[]> {
  const supabase = await createClient();

  let query = supabase.from("audit_logs").select("*").order("created_at", { ascending: false }).limit(limit);

  if (userId) {
    query = query.eq("user_id", userId);
  }

  if (resourceType) {
    query = query.eq("resource_type", resourceType);
  }

  if (startDate) {
    query = query.gte("created_at", startDate.toISOString());
  }

  if (endDate) {
    query = query.lte("created_at", endDate.toISOString());
  }

  const { data, error } = await query;

  if (error) {
    console.error("Failed to get audit logs:", error);
    return [];
  }

  return (data || []) as AuditLogEntry[];
}

/**
 * Search audit logs
 */
export async function searchAuditLogs(
  searchTerm: string,
  limit: number = 100
): Promise<AuditLogEntry[]> {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("audit_logs")
    .select("*")
    .or(`action.ilike.%${searchTerm}%,resource_type.ilike.%${searchTerm}%,error_message.ilike.%${searchTerm}%`)
    .order("created_at", { ascending: false })
    .limit(limit);

  if (error) {
    console.error("Failed to search audit logs:", error);
    return [];
  }

  return (data || []) as AuditLogEntry[];
}






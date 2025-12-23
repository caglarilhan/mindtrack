/**
 * HIPAA-Compliant Data Backup & Recovery
 * Automated backups with encryption
 */

import { createClient } from "@/utils/supabase/server";
import { encryptPHI } from "./encryption";

export interface BackupConfig {
  retentionDays: number; // Default: 7 years (2555 days) for HIPAA
  encryptionEnabled: boolean;
  backupLocation: "supabase" | "s3" | "local";
}

const DEFAULT_CONFIG: BackupConfig = {
  retentionDays: 2555, // 7 years
  encryptionEnabled: true,
  backupLocation: "supabase",
};

/**
 * Create encrypted backup of PHI data
 */
export async function createBackup(
  tableName: string,
  config: Partial<BackupConfig> = {}
): Promise<{ success: boolean; backupId?: string; error?: string }> {
  const finalConfig = { ...DEFAULT_CONFIG, ...config };
  const supabase = await createClient();

  try {
    // Get all data from table
    const { data, error } = await supabase.from(tableName).select("*");

    if (error) {
      throw new Error(`Failed to fetch data: ${error.message}`);
    }

    if (!data || data.length === 0) {
      return { success: true, backupId: undefined }; // No data to backup
    }

    // Serialize data
    const serializedData = JSON.stringify(data);

    // Encrypt if enabled
    const backupData = finalConfig.encryptionEnabled
      ? encryptPHI(serializedData)
      : serializedData;

    // Store backup metadata
    const { data: backupRecord, error: backupError } = await supabase
      .from("backups")
      .insert({
        table_name: tableName,
        backup_data: backupData,
        encrypted: finalConfig.encryptionEnabled,
        record_count: data.length,
        created_at: new Date().toISOString(),
        expires_at: new Date(
          Date.now() + finalConfig.retentionDays * 24 * 60 * 60 * 1000
        ).toISOString(),
      })
      .select("id")
      .single();

    if (backupError) {
      throw new Error(`Failed to store backup: ${backupError.message}`);
    }

    return {
      success: true,
      backupId: backupRecord.id,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Backup creation error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Restore data from backup
 */
export async function restoreBackup(
  backupId: string
): Promise<{ success: boolean; restoredCount?: number; error?: string }> {
  const supabase = await createClient();

  try {
    // Get backup record
    const { data: backup, error: backupError } = await supabase
      .from("backups")
      .select("*")
      .eq("id", backupId)
      .single();

    if (backupError || !backup) {
      throw new Error("Backup not found");
    }

    // Decrypt if encrypted
    let backupData: string;
    if (backup.encrypted) {
      const { decryptPHI } = await import("./encryption");
      backupData = decryptPHI(backup.backup_data);
    } else {
      backupData = backup.backup_data;
    }

    // Parse data
    const data = JSON.parse(backupData);

    // Restore to table
    const { error: restoreError } = await supabase
      .from(backup.table_name)
      .upsert(data, { onConflict: "id" });

    if (restoreError) {
      throw new Error(`Failed to restore: ${restoreError.message}`);
    }

    return {
      success: true,
      restoredCount: data.length,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Backup restoration error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Clean up expired backups
 */
export async function cleanupExpiredBackups(): Promise<number> {
  const supabase = await createClient();

  const { data, error } = await supabase
    .from("backups")
    .delete()
    .lt("expires_at", new Date().toISOString())
    .select("id");

  if (error) {
    console.error("Failed to cleanup expired backups:", error);
    return 0;
  }

  return data?.length || 0;
}

/**
 * List all backups
 */
export async function listBackups(
  tableName?: string,
  limit: number = 100
): Promise<Array<{
  id: string;
  table_name: string;
  record_count: number;
  encrypted: boolean;
  created_at: string;
  expires_at: string;
}>> {
  const supabase = await createClient();

  let query = supabase
    .from("backups")
    .select("id, table_name, record_count, encrypted, created_at, expires_at")
    .order("created_at", { ascending: false })
    .limit(limit);

  if (tableName) {
    query = query.eq("table_name", tableName);
  }

  const { data, error } = await query;

  if (error) {
    console.error("Failed to list backups:", error);
    return [];
  }

  return (data || []) as Array<{
    id: string;
    table_name: string;
    record_count: number;
    encrypted: boolean;
    created_at: string;
    expires_at: string;
  }>;
}






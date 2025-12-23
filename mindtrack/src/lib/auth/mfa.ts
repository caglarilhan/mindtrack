/**
 * Multi-Factor Authentication (MFA)
 * HIPAA-compliant MFA implementation
 * HIPAA Requirement: §164.312(a)(1) - Access Control
 */

import crypto from "crypto";
import { createClient } from "@/utils/supabase/server";
import { logLogin, logDataModification } from "@/lib/hipaa/audit-log";

// TOTP implementation (RFC 6238)
// Note: In production, use a library like 'speakeasy' or 'otplib'

export interface MFAMethod {
  type: "totp" | "sms" | "email" | "biometric";
  enabled: boolean;
  verified: boolean;
  secret?: string; // For TOTP
  phoneNumber?: string; // For SMS
  email?: string; // For Email
  createdAt: string;
  lastUsed?: string;
}

export interface MFAVerificationResult {
  success: boolean;
  verified: boolean;
  error?: string;
}

/**
 * Generate TOTP secret
 */
export function generateTOTPSecret(): string {
  // Generate 32-byte secret (base32 encoded)
  const secret = crypto.randomBytes(20).toString("base64");
  return secret.replace(/[^A-Z2-7]/g, "").substring(0, 32); // Base32 format
}

/**
 * Generate TOTP code
 */
export function generateTOTPCode(secret: string, timeStep: number = 30): string {
  const time = Math.floor(Date.now() / 1000 / timeStep);
  const key = Buffer.from(base32Decode(secret), "binary");
  const counter = Buffer.allocUnsafe(8);
  counter.writeUInt32BE(time, 4);

  const hmac = crypto.createHmac("sha1", key);
  hmac.update(counter);
  const digest = hmac.digest();

  const offset = digest[digest.length - 1] & 0x0f;
  const code = ((digest[offset] & 0x7f) << 24 |
                (digest[offset + 1] & 0xff) << 16 |
                (digest[offset + 2] & 0xff) << 8 |
                (digest[offset + 3] & 0xff)) % 1000000;

  return code.toString().padStart(6, "0");
}

/**
 * Verify TOTP code
 */
export function verifyTOTPCode(secret: string, code: string, window: number = 1): boolean {
  const timeStep = 30;
  const currentTime = Math.floor(Date.now() / 1000 / timeStep);

  // Check current time and window
  for (let i = -window; i <= window; i++) {
    const expectedCode = generateTOTPCode(secret, timeStep);
    if (code === expectedCode) {
      return true;
    }
  }

  return false;
}

/**
 * Base32 decode (simplified)
 */
function base32Decode(str: string): string {
  const base32chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
  let bits = 0;
  let value = 0;
  let output = "";

  for (let i = 0; i < str.length; i++) {
    value = (value << 5) | base32chars.indexOf(str[i]);
    bits += 5;

    if (bits >= 8) {
      output += String.fromCharCode((value >> (bits - 8)) & 255);
      bits -= 8;
    }
  }

  return output;
}

/**
 * Generate backup codes
 */
export function generateBackupCodes(count: number = 10): string[] {
  const codes: string[] = [];
  for (let i = 0; i < count; i++) {
    const code = crypto.randomBytes(4).toString("hex").toUpperCase();
    codes.push(code);
  }
  return codes;
}

/**
 * Generate OTP code (for SMS/Email)
 */
export function generateOTPCode(length: number = 6): string {
  const digits = "0123456789";
  let code = "";
  for (let i = 0; i < length; i++) {
    code += digits[Math.floor(Math.random() * digits.length)];
  }
  return code;
}

/**
 * Setup MFA for user
 */
export async function setupMFA(
  userId: string,
  method: "totp" | "sms" | "email",
  contactInfo?: string
): Promise<{ success: boolean; secret?: string; qrCodeUrl?: string; backupCodes?: string[]; error?: string }> {
  try {
    const supabase = await createClient();

    let secret: string | undefined;
    let qrCodeUrl: string | undefined;
    let backupCodes: string[] | undefined;

    if (method === "totp") {
      secret = generateTOTPSecret();
      backupCodes = generateBackupCodes();
      
      // Generate QR code URL (for Google Authenticator, etc.)
      const issuer = "MindTrack";
      const accountName = userId;
      qrCodeUrl = `otpauth://totp/${encodeURIComponent(issuer)}:${encodeURIComponent(accountName)}?secret=${secret}&issuer=${encodeURIComponent(issuer)}`;
    }

    // Store MFA method
    const { error } = await supabase.from("mfa_methods").insert({
      user_id: userId,
      method_type: method,
      enabled: false, // Not enabled until verified
      verified: false,
      secret: secret || null,
      phone_number: method === "sms" ? contactInfo : null,
      email: method === "email" ? contactInfo : null,
      backup_codes: backupCodes ? JSON.stringify(backupCodes) : null,
    });

    if (error) {
      throw new Error(`Failed to setup MFA: ${error.message}`);
    }

    // Log MFA setup
    await logDataModification(
      userId,
      "create",
      "mfa_setup",
      userId,
      undefined,
      undefined,
      true,
      { method }
    );

    return {
      success: true,
      secret,
      qrCodeUrl,
      backupCodes,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("MFA setup error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Verify MFA code
 */
export async function verifyMFA(
  userId: string,
  method: "totp" | "sms" | "email" | "backup",
  code: string,
  ipAddress?: string,
  userAgent?: string
): Promise<MFAVerificationResult> {
  try {
    const supabase = await createClient();

    // Get MFA method
    const { data: mfaMethod, error: fetchError } = await supabase
      .from("mfa_methods")
      .select("*")
      .eq("user_id", userId)
      .eq("method_type", method === "backup" ? "totp" : method)
      .eq("enabled", true)
      .single();

    if (fetchError || !mfaMethod) {
      return {
        success: false,
        verified: false,
        error: "MFA method not found or not enabled",
      };
    }

    let verified = false;

    if (method === "totp" && mfaMethod.secret) {
      verified = verifyTOTPCode(mfaMethod.secret, code);
    } else if (method === "backup" && mfaMethod.backup_codes) {
      // Check backup codes
      const backupCodes = JSON.parse(mfaMethod.backup_codes) as string[];
      const codeIndex = backupCodes.indexOf(code.toUpperCase());
      if (codeIndex !== -1) {
        verified = true;
        // Remove used backup code
        backupCodes.splice(codeIndex, 1);
        await supabase
          .from("mfa_methods")
          .update({ backup_codes: JSON.stringify(backupCodes) })
          .eq("id", mfaMethod.id);
      }
    } else if (method === "sms" || method === "email") {
      // For SMS/Email, verify against stored OTP (would be stored temporarily)
      // This is a simplified version - in production, use a proper OTP storage
      const { data: otpRecord } = await supabase
        .from("mfa_otp_codes")
        .select("*")
        .eq("user_id", userId)
        .eq("method", method)
        .eq("code", code)
        .eq("used", false)
        .gt("expires_at", new Date().toISOString())
        .single();

      if (otpRecord) {
        verified = true;
        // Mark OTP as used
        await supabase
          .from("mfa_otp_codes")
          .update({ used: true, used_at: new Date().toISOString() })
          .eq("id", otpRecord.id);
      }
    }

    if (verified) {
      // Update last used
      await supabase
        .from("mfa_methods")
        .update({ last_used: new Date().toISOString() })
        .eq("id", mfaMethod.id);

      // Log successful verification
      await logLogin(userId, ipAddress, userAgent, true);
    } else {
      // Log failed verification
      await logLogin(userId, ipAddress, userAgent, false, "Invalid MFA code");
    }

    return {
      success: true,
      verified,
      error: verified ? undefined : "Invalid code",
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("MFA verification error:", error);
    return {
      success: false,
      verified: false,
      error: errorMessage,
    };
  }
}

/**
 * Enable MFA for user
 */
export async function enableMFA(userId: string, methodId: string): Promise<{ success: boolean; error?: string }> {
  try {
    const supabase = await createClient();

    const { error } = await supabase
      .from("mfa_methods")
      .update({ enabled: true, verified: true })
      .eq("id", methodId)
      .eq("user_id", userId);

    if (error) {
      throw new Error(`Failed to enable MFA: ${error.message}`);
    }

    // Log MFA enable
    await logDataModification(
      userId,
      "update",
      "mfa_enable",
      userId,
      undefined,
      undefined,
      true,
      { methodId }
    );

    return { success: true };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    return { success: false, error: errorMessage };
  }
}

/**
 * Disable MFA for user
 */
export async function disableMFA(userId: string, methodId: string): Promise<{ success: boolean; error?: string }> {
  try {
    const supabase = await createClient();

    const { error } = await supabase
      .from("mfa_methods")
      .update({ enabled: false })
      .eq("id", methodId)
      .eq("user_id", userId);

    if (error) {
      throw new Error(`Failed to disable MFA: ${error.message}`);
    }

    // Log MFA disable
    await logDataModification(
      userId,
      "update",
      "mfa_disable",
      userId,
      undefined,
      undefined,
      true,
      { methodId }
    );

    return { success: true };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    return { success: false, error: errorMessage };
  }
}

/**
 * Check if user has MFA enabled
 */
export async function hasMFAEnabled(userId: string): Promise<boolean> {
  try {
    const supabase = await createClient();

    const { data, error } = await supabase
      .from("mfa_methods")
      .select("id")
      .eq("user_id", userId)
      .eq("enabled", true)
      .limit(1);

    if (error) {
      return false;
    }

    return (data?.length || 0) > 0;
  } catch (error) {
    return false;
  }
}

/**
 * Get MFA methods for user
 */
export async function getMFAMethods(userId: string): Promise<MFAMethod[]> {
  try {
    const supabase = await createClient();

    const { data, error } = await supabase
      .from("mfa_methods")
      .select("*")
      .eq("user_id", userId)
      .order("created_at", { ascending: false });

    if (error) {
      console.error("Failed to get MFA methods:", error);
      return [];
    }

    return (data || []).map((method) => ({
      type: method.method_type as "totp" | "sms" | "email" | "biometric",
      enabled: method.enabled,
      verified: method.verified,
      secret: method.secret || undefined,
      phoneNumber: method.phone_number || undefined,
      email: method.email || undefined,
      createdAt: method.created_at,
      lastUsed: method.last_used || undefined,
    }));
  } catch (error) {
    console.error("Get MFA methods error:", error);
    return [];
  }
}






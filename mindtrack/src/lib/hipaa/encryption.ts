/**
 * HIPAA-Compliant Encryption
 * Field-level encryption for PHI (Protected Health Information)
 */

import crypto from "crypto";

const ALGORITHM = "aes-256-gcm";
const IV_LENGTH = 16;
const SALT_LENGTH = 64;
const TAG_LENGTH = 16;
const KEY_LENGTH = 32;

/**
 * Get encryption key from environment or generate
 * In production, use a secure key management service (AWS KMS, Azure Key Vault)
 */
function getEncryptionKey(): Buffer {
  const key = process.env.ENCRYPTION_KEY;
  
  if (!key) {
    throw new Error("ENCRYPTION_KEY environment variable is required for HIPAA compliance");
  }

  // Key should be 32 bytes (256 bits) for AES-256
  if (key.length !== 64) { // 64 hex characters = 32 bytes
    throw new Error("ENCRYPTION_KEY must be 64 hex characters (32 bytes)");
  }

  return Buffer.from(key, "hex");
}

/**
 * Encrypt sensitive data (PHI)
 * Returns: iv:salt:tag:encryptedData (all base64 encoded)
 */
export function encryptPHI(data: string): string {
  if (!data) {
    return "";
  }

  try {
    const key = getEncryptionKey();
    const iv = crypto.randomBytes(IV_LENGTH);
    const salt = crypto.randomBytes(SALT_LENGTH);

    // Derive key from master key and salt
    const derivedKey = crypto.pbkdf2Sync(key, salt, 100000, KEY_LENGTH, "sha256");

    const cipher = crypto.createCipheriv(ALGORITHM, derivedKey, iv);
    
    let encrypted = cipher.update(data, "utf8", "base64");
    encrypted += cipher.final("base64");
    
    const tag = cipher.getAuthTag();

    // Combine: iv:salt:tag:encryptedData
    return [
      iv.toString("base64"),
      salt.toString("base64"),
      tag.toString("base64"),
      encrypted,
    ].join(":");
  } catch (error) {
    console.error("Encryption error:", error);
    throw new Error("Failed to encrypt PHI data");
  }
}

/**
 * Decrypt sensitive data (PHI)
 * Input format: iv:salt:tag:encryptedData (all base64 encoded)
 */
export function decryptPHI(encryptedData: string): string {
  if (!encryptedData) {
    return "";
  }

  try {
    const parts = encryptedData.split(":");
    
    if (parts.length !== 4) {
      throw new Error("Invalid encrypted data format");
    }

    const [ivBase64, saltBase64, tagBase64, encrypted] = parts;
    
    const key = getEncryptionKey();
    const iv = Buffer.from(ivBase64, "base64");
    const salt = Buffer.from(saltBase64, "base64");
    const tag = Buffer.from(tagBase64, "base64");

    // Derive key from master key and salt
    const derivedKey = crypto.pbkdf2Sync(key, salt, 100000, KEY_LENGTH, "sha256");

    const decipher = crypto.createDecipheriv(ALGORITHM, derivedKey, iv);
    decipher.setAuthTag(tag);

    let decrypted = decipher.update(encrypted, "base64", "utf8");
    decrypted += decipher.final("utf8");

    return decrypted;
  } catch (error) {
    console.error("Decryption error:", error);
    throw new Error("Failed to decrypt PHI data");
  }
}

/**
 * Encrypt object with PHI fields
 * Automatically encrypts fields marked as PHI
 */
export function encryptPHIObject<T extends Record<string, unknown>>(
  obj: T,
  phiFields: (keyof T)[]
): T {
  const encrypted = { ...obj };

  for (const field of phiFields) {
    const value = obj[field];
    if (value && typeof value === "string") {
      (encrypted as Record<string, unknown>)[field as string] = encryptPHI(value);
    }
  }

  return encrypted;
}

/**
 * Decrypt object with PHI fields
 */
export function decryptPHIObject<T extends Record<string, unknown>>(
  obj: T,
  phiFields: (keyof T)[]
): T {
  const decrypted = { ...obj };

  for (const field of phiFields) {
    const value = obj[field];
    if (value && typeof value === "string") {
      try {
        (decrypted as Record<string, unknown>)[field as string] = decryptPHI(value);
      } catch (error) {
        console.error(`Failed to decrypt field ${String(field)}:`, error);
        // Keep encrypted value if decryption fails
      }
    }
  }

  return decrypted;
}

/**
 * Check if data is encrypted (basic check)
 */
export function isEncrypted(data: string): boolean {
  if (!data) return false;
  
  // Encrypted data format: iv:salt:tag:encryptedData (4 parts separated by :)
  const parts = data.split(":");
  return parts.length === 4 && parts.every(part => part.length > 0);
}

/**
 * Generate encryption key (for setup/testing)
 * DO NOT use in production - use a secure key management service
 */
export function generateEncryptionKey(): string {
  return crypto.randomBytes(KEY_LENGTH).toString("hex");
}






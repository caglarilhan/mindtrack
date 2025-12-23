/**
 * Test encryption endpoint (for development/testing)
 */

import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";
import { encryptPHI, decryptPHI, generateEncryptionKey } from "@/lib/hipaa/encryption";
import { createAuditLog } from "@/lib/hipaa/audit-log";

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { action, data } = await request.json();

    // Log access
    await createAuditLog({
      user_id: user.id,
      action: "read",
      resource_type: "encryption_test",
      ip_address: request.headers.get("x-forwarded-for") || undefined,
      user_agent: request.headers.get("user-agent") || undefined,
      success: true,
    });

    if (action === "encrypt") {
      if (!data) {
        return NextResponse.json({ error: "Data is required" }, { status: 400 });
      }

      const encrypted = encryptPHI(data);
      return NextResponse.json({
        success: true,
        encrypted,
        originalLength: data.length,
        encryptedLength: encrypted.length,
      });
    }

    if (action === "decrypt") {
      if (!data) {
        return NextResponse.json({ error: "Encrypted data is required" }, { status: 400 });
      }

      const decrypted = decryptPHI(data);
      return NextResponse.json({
        success: true,
        decrypted,
        encryptedLength: data.length,
        decryptedLength: decrypted.length,
      });
    }

    if (action === "generate-key") {
      // Only allow in development
      if (process.env.NODE_ENV === "production") {
        return NextResponse.json({ error: "Key generation not allowed in production" }, { status: 403 });
      }

      const key = generateEncryptionKey();
      return NextResponse.json({
        success: true,
        key,
        note: "Store this key securely in ENCRYPTION_KEY environment variable",
      });
    }

    return NextResponse.json({ error: "Invalid action" }, { status: 400 });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Encryption test error:", error);
    return NextResponse.json({
      error: errorMessage,
    }, { status: 500 });
  }
}






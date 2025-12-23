/**
 * Consent Management System
 * HIPAA Requirement: §164.508 - Uses and Disclosures for Which Authorization is Required
 */

import { createClient } from "@/utils/supabase/server";
import { logDataAccess, logDataModification } from "./audit-log";
import { encryptPHI } from "./encryption";

export type ConsentType = 
  | "treatment" 
  | "payment" 
  | "healthcare_operations" 
  | "marketing" 
  | "research" 
  | "psychotherapy_notes"
  | "other";

export type ConsentStatus = "pending" | "active" | "expired" | "withdrawn" | "revoked";

export interface ConsentForm {
  id: string;
  patientId: string;
  consentType: ConsentType;
  description: string;
  status: ConsentStatus;
  signedAt?: string;
  expiresAt?: string;
  withdrawnAt?: string;
  revokedAt?: string;
  signature?: {
    name: string;
    signatureData: string; // Base64 encoded signature image
    ipAddress?: string;
    userAgent?: string;
  };
  metadata?: Record<string, unknown>;
  createdAt: string;
  updatedAt: string;
}

export interface ConsentRequest {
  patientId: string;
  consentType: ConsentType;
  description: string;
  expiresInDays?: number; // Optional expiration
}

/**
 * Create consent form
 */
export async function createConsentForm(
  request: ConsentRequest,
  therapistId: string
): Promise<{ success: boolean; consentId?: string; error?: string }> {
  try {
    const supabase = await createClient();

    // Calculate expiration date
    const expiresAt = request.expiresInDays
      ? new Date(Date.now() + request.expiresInDays * 24 * 60 * 60 * 1000).toISOString()
      : null;

    // Create consent form
    const { data, error } = await supabase
      .from("consent_forms")
      .insert({
        patient_id: request.patientId,
        consent_type: request.consentType,
        description: request.description,
        status: "pending",
        expires_at: expiresAt,
        created_by: therapistId,
      })
      .select("id")
      .single();

    if (error) {
      throw new Error(`Failed to create consent form: ${error.message}`);
    }

    // Log consent creation
    await logDataModification(
      therapistId,
      "create",
      "consent_form",
      data.id,
      undefined,
      undefined,
      true,
      {
        patientId: request.patientId,
        consentType: request.consentType,
      }
    );

    return {
      success: true,
      consentId: data.id,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Create consent form error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Sign consent form (e-signature)
 */
export async function signConsentForm(
  consentId: string,
  signature: {
    name: string;
    signatureData: string; // Base64 encoded signature image
    ipAddress?: string;
    userAgent?: string;
  },
  patientId: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const supabase = await createClient();

    // Verify patient access
    const { data: { user } } = await supabase.auth.getUser();
    if (!user || user.id !== patientId) {
      return {
        success: false,
        error: "Access denied",
      };
    }

    // Encrypt signature data
    const encryptedSignature = await encryptPHI(JSON.stringify(signature));

    // Update consent form
    const { error: updateError } = await supabase
      .from("consent_forms")
      .update({
        status: "active",
        signed_at: new Date().toISOString(),
        signature_data: encryptedSignature,
        signature_name: signature.name,
        signature_ip: signature.ipAddress || null,
        signature_user_agent: signature.userAgent || null,
      })
      .eq("id", consentId)
      .eq("patient_id", patientId)
      .eq("status", "pending");

    if (updateError) {
      throw new Error(`Failed to sign consent form: ${updateError.message}`);
    }

    // Log consent signing
    await logDataModification(
      patientId,
      "update",
      "consent_sign",
      consentId,
      undefined,
      undefined,
      true,
      {
        signatureName: signature.name,
      }
    );

    return { success: true };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Sign consent form error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Withdraw consent
 */
export async function withdrawConsent(
  consentId: string,
  patientId: string,
  reason?: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const supabase = await createClient();

    // Verify patient access
    const { data: { user } } = await supabase.auth.getUser();
    if (!user || user.id !== patientId) {
      return {
        success: false,
        error: "Access denied",
      };
    }

    // Update consent form
    const { error: updateError } = await supabase
      .from("consent_forms")
      .update({
        status: "withdrawn",
        withdrawn_at: new Date().toISOString(),
        withdrawal_reason: reason || null,
      })
      .eq("id", consentId)
      .eq("patient_id", patientId)
      .in("status", ["active", "pending"]);

    if (updateError) {
      throw new Error(`Failed to withdraw consent: ${updateError.message}`);
    }

    // Log consent withdrawal
    await logDataModification(
      patientId,
      "update",
      "consent_withdraw",
      consentId,
      undefined,
      undefined,
      true,
      {
        reason,
      }
    );

    return { success: true };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Withdraw consent error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Revoke consent (by therapist/admin)
 */
export async function revokeConsent(
  consentId: string,
  therapistId: string,
  reason?: string
): Promise<{ success: boolean; error?: string }> {
  try {
    const supabase = await createClient();

    // Update consent form
    const { error: updateError } = await supabase
      .from("consent_forms")
      .update({
        status: "revoked",
        revoked_at: new Date().toISOString(),
        revoked_by: therapistId,
        revocation_reason: reason || null,
      })
      .eq("id", consentId)
      .in("status", ["active", "pending"]);

    if (updateError) {
      throw new Error(`Failed to revoke consent: ${updateError.message}`);
    }

    // Log consent revocation
    await logDataModification(
      therapistId,
      "update",
      "consent_revoke",
      consentId,
      undefined,
      undefined,
      true,
      {
        reason,
      }
    );

    return { success: true };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Revoke consent error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Get consent forms for patient
 */
export async function getPatientConsents(
  patientId: string
): Promise<ConsentForm[]> {
  try {
    const supabase = await createClient();

    // Verify patient access
    const { data: { user } } = await supabase.auth.getUser();
    if (!user || user.id !== patientId) {
      return [];
    }

    const { data, error } = await supabase
      .from("consent_forms")
      .select("*")
      .eq("patient_id", patientId)
      .order("created_at", { ascending: false });

    if (error) {
      console.error("Get patient consents error:", error);
      return [];
    }

    // Check for expired consents
    const now = new Date();
    const consents = (data || []).map((consent) => {
      let status = consent.status as ConsentStatus;
      
      // Auto-expire if past expiration date
      if (status === "active" && consent.expires_at) {
        const expiresAt = new Date(consent.expires_at);
        if (expiresAt < now) {
          status = "expired";
          // Update in database (async, don't wait)
          supabase
            .from("consent_forms")
            .update({ status: "expired" })
            .eq("id", consent.id)
            .then(() => {});
        }
      }

      return {
        id: consent.id,
        patientId: consent.patient_id,
        consentType: consent.consent_type as ConsentType,
        description: consent.description,
        status,
        signedAt: consent.signed_at || undefined,
        expiresAt: consent.expires_at || undefined,
        withdrawnAt: consent.withdrawn_at || undefined,
        revokedAt: consent.revoked_at || undefined,
        signature: consent.signature_data
          ? {
              name: consent.signature_name || "Unknown",
              signatureData: consent.signature_data,
              ipAddress: consent.signature_ip || undefined,
              userAgent: consent.signature_user_agent || undefined,
            }
          : undefined,
        metadata: consent.metadata as Record<string, unknown> | undefined,
        createdAt: consent.created_at,
        updatedAt: consent.updated_at,
      };
    });

    return consents;
  } catch (error) {
    console.error("Get patient consents error:", error);
    return [];
  }
}

/**
 * Check if consent is valid for specific type
 */
export async function hasValidConsent(
  patientId: string,
  consentType: ConsentType
): Promise<boolean> {
  try {
    const consents = await getPatientConsents(patientId);
    
    const validConsent = consents.find(
      (consent) =>
        consent.consentType === consentType &&
        consent.status === "active" &&
        (!consent.expiresAt || new Date(consent.expiresAt) > new Date())
    );

    return !!validConsent;
  } catch (error) {
    console.error("Check valid consent error:", error);
    return false;
  }
}

/**
 * Get consent expiration warnings
 */
export async function getConsentExpirationWarnings(
  daysBeforeExpiration: number = 30
): Promise<ConsentForm[]> {
  try {
    const supabase = await createClient();

    const warningDate = new Date(Date.now() + daysBeforeExpiration * 24 * 60 * 60 * 1000);

    const { data, error } = await supabase
      .from("consent_forms")
      .select("*")
      .eq("status", "active")
      .not("expires_at", "is", null)
      .lte("expires_at", warningDate.toISOString())
      .gt("expires_at", new Date().toISOString())
      .order("expires_at", { ascending: true });

    if (error) {
      console.error("Get consent expiration warnings error:", error);
      return [];
    }

    return (data || []).map((consent) => ({
      id: consent.id,
      patientId: consent.patient_id,
      consentType: consent.consent_type as ConsentType,
      description: consent.description,
      status: consent.status as ConsentStatus,
      signedAt: consent.signed_at || undefined,
      expiresAt: consent.expires_at || undefined,
      withdrawnAt: consent.withdrawn_at || undefined,
      revokedAt: consent.revoked_at || undefined,
      signature: consent.signature_data
        ? {
            name: consent.signature_name || "Unknown",
            signatureData: consent.signature_data,
            ipAddress: consent.signature_ip || undefined,
            userAgent: consent.signature_user_agent || undefined,
          }
        : undefined,
      metadata: consent.metadata as Record<string, unknown> | undefined,
      createdAt: consent.created_at,
      updatedAt: consent.updated_at,
    }));
  } catch (error) {
    console.error("Get consent expiration warnings error:", error);
    return [];
  }
}






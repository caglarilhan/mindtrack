import crypto from "crypto";
import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

function getAdminClient() {
  if (!SUPABASE_URL || !SERVICE_ROLE_KEY) {
    return null;
  }
  return createClient(SUPABASE_URL, SERVICE_ROLE_KEY, {
    auth: { autoRefreshToken: false, persistSession: false },
  });
}

function hashToken(token: string) {
  return crypto.createHash("sha256").update(token).digest("hex");
}

export type CaregiverVerificationResult = {
  ok: boolean;
  source?: "env" | "db";
  tokenId?: string | null;
  label?: string;
  allowedRegions?: string[];
  reason?: string;
};

export async function verifyCaregiverToken(
  token: string | null | undefined,
  region?: "us" | "eu",
): Promise<CaregiverVerificationResult> {
  if (!token) {
    return { ok: false, reason: "token-missing" };
  }

  const sharedToken = process.env.CAREGIVER_SHARED_TOKEN;
  if (sharedToken && token === sharedToken) {
    return {
      ok: true,
      source: "env",
      tokenId: null,
      label: "shared-env",
      allowedRegions: ["us", "eu"],
    };
  }

  const adminClient = getAdminClient();
  if (!adminClient) {
    console.warn("[caregiver-token] Service role client unavailable");
    return { ok: false, reason: "service-client-missing" };
  }

  const hashed = hashToken(token);
  const { data, error } = await adminClient
    .from("caregiver_tokens")
    .select("id, label, allowed_regions, active, expires_at")
    .eq("token_hash", hashed)
    .maybeSingle();

  if (error) {
    console.error("[caregiver-token] lookup error", error);
    return { ok: false, reason: "db-error" };
  }

  if (!data) {
    return { ok: false, reason: "token-not-found" };
  }

  if (!data.active) {
    return { ok: false, reason: "token-inactive" };
  }

  if (data.expires_at && new Date(data.expires_at) < new Date()) {
    return { ok: false, reason: "token-expired" };
  }

  if (region && Array.isArray(data.allowed_regions) && !data.allowed_regions.includes(region)) {
    return { ok: false, reason: "region-not-allowed" };
  }

  // update last_used_at (fire and forget)
  adminClient
    .from("caregiver_tokens")
    .update({ last_used_at: new Date().toISOString() })
    .eq("id", data.id)
    .then()
    .catch((err) => console.error("[caregiver-token] last_used update error", err));

  return {
    ok: true,
    source: "db",
    tokenId: data.id,
    label: data.label,
    allowedRegions: data.allowed_regions ?? undefined,
  };
}

export interface CaregiverAccessLogInput {
  tokenId?: string | null;
  tokenLabel?: string | null;
  patientId?: string | null;
  region: "us" | "eu";
  status: "allowed" | "denied";
  reason?: string | null;
  ipAddress?: string | null;
  userAgent?: string | null;
}

export async function recordCaregiverAccessLog(payload: CaregiverAccessLogInput) {
  const adminClient = getAdminClient();
  if (!adminClient) {
    console.warn("[caregiver-token] cannot record log without service role client");
    return;
  }

  const logEntry = {
    token_id: payload.tokenId ?? null,
    token_label: payload.tokenLabel ?? null,
    patient_id: payload.patientId ?? null,
    region: payload.region,
    status: payload.status,
    reason: payload.reason ?? null,
    ip_address: payload.ipAddress ?? null,
    user_agent: payload.userAgent ?? null,
  };

  const { error } = await adminClient.from("caregiver_access_logs").insert(logEntry);
  if (error) {
    console.error("[caregiver-token] access log insert error", error);
  }
}

export function hashCaregiverTokenForStorage(token: string) {
  return hashToken(token);
}

export async function createCaregiverToken(data: { label: string; allowedRegions?: string[]; expiresAt?: Date }): Promise<{ id: string; token: string }> {
  const adminClient = getAdminClient();
  if (!adminClient) throw new Error("Service role client unavailable");
  
  const token = crypto.randomBytes(32).toString("hex");
  const hashed = hashToken(token);
  
  const { data: result, error } = await adminClient
    .from("caregiver_tokens")
    .insert({
      token_hash: hashed,
      label: data.label,
      allowed_regions: data.allowedRegions || ["us", "eu"],
      expires_at: data.expiresAt?.toISOString() || null,
      active: true,
    })
    .select("id")
    .single();
  
  if (error) throw error;
  return { id: result.id, token };
}

export async function listCaregiverTokens(): Promise<any[]> {
  const adminClient = getAdminClient();
  if (!adminClient) return [];
  
  const { data, error } = await adminClient
    .from("caregiver_tokens")
    .select("id, label, allowed_regions, active, expires_at, last_used_at, created_at")
    .order("created_at", { ascending: false });
  
  if (error) {
    console.error("[caregiver-token] list error", error);
    return [];
  }
  return data || [];
}

export async function updateCaregiverToken(tokenId: string, updates: { label?: string; active?: boolean; allowedRegions?: string[] }): Promise<void> {
  const adminClient = getAdminClient();
  if (!adminClient) throw new Error("Service role client unavailable");
  
  const { error } = await adminClient
    .from("caregiver_tokens")
    .update({
      label: updates.label,
      active: updates.active,
      allowed_regions: updates.allowedRegions,
      updated_at: new Date().toISOString(),
    })
    .eq("id", tokenId);
  
  if (error) throw error;
}

export async function deleteCaregiverToken(tokenId: string): Promise<void> {
  const adminClient = getAdminClient();
  if (!adminClient) throw new Error("Service role client unavailable");
  
  const { error } = await adminClient
    .from("caregiver_tokens")
    .delete()
    .eq("id", tokenId);
  
  if (error) throw error;
}

export async function rotateCaregiverToken(tokenId: string): Promise<{ token: string }> {
  const adminClient = getAdminClient();
  if (!adminClient) throw new Error("Service role client unavailable");
  
  const token = crypto.randomBytes(32).toString("hex");
  const hashed = hashToken(token);
  
  const { error } = await adminClient
    .from("caregiver_tokens")
    .update({ token_hash: hashed, updated_at: new Date().toISOString() })
    .eq("id", tokenId);
  
  if (error) throw error;
  return { token };
}

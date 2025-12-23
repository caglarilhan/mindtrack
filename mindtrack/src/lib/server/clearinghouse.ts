import { createClient } from "@supabase/supabase-js";
import crypto from "crypto";

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

function getAdminClient() {
  if (!SUPABASE_URL || !SERVICE_ROLE_KEY) {
    throw new Error("Supabase service role yapılandırılmalı");
  }
  return createClient(SUPABASE_URL, SERVICE_ROLE_KEY, {
    auth: { autoRefreshToken: false, persistSession: false },
  });
}

export type ClaimStatus = "queued" | "submitted" | "acknowledged" | "denied" | "paid" | "error";

export interface SubmitClaimInput {
  claimNumber: string;
  patientId: string;
  providerId: string;
  payerConnectionId: string | null;
  payload: Record<string, any>;
  region?: "us" | "eu";
}

export async function enqueueClaim(input: SubmitClaimInput) {
  const client = getAdminClient();
  const record = {
    claim_number: input.claimNumber,
    patient_id: input.patientId,
    provider_id: input.providerId,
    payer_connection_id: input.payerConnectionId,
    payload: input.payload,
    region: input.region || "us",
    status: "queued" as ClaimStatus,
  };

  const { data, error } = await client
    .from("claims_queue")
    .insert(record)
    .select("id, status, created_at")
    .single();

  if (error) {
    console.error("[clearinghouse] enqueue error", error);
    throw new Error("Claim kuyruğa alınamadı");
  }
  return data;
}

export async function getClaimByNumber(claimNumber: string) {
  const client = getAdminClient();
  const { data, error } = await client
    .from("claims_queue")
    .select("id, claim_number, patient_id, provider_id, status, region, payload, created_at, updated_at")
    .eq("claim_number", claimNumber)
    .maybeSingle();
  if (error) {
    console.error("[clearinghouse] getClaimByNumber error", error);
    return null;
  }
  return data;
}

export async function updateClaimStatus(claimId: string, status: ClaimStatus, meta?: Record<string, any>) {
  const client = getAdminClient();
  const { data, error } = await client
    .from("claims_queue")
    .update({ status, acknowledgements: meta || null, updated_at: new Date().toISOString() })
    .eq("id", claimId)
    .select("id, status, acknowledgements, updated_at")
    .single();
  if (error) {
    console.error("[clearinghouse] status update error", error);
    throw new Error("Claim durumu güncellenemedi");
  }
  return data;
}

export async function logEraEvent(claimId: string, code: string, description: string, amount: number, payload: any) {
  const client = getAdminClient();
  const { error } = await client.from("era_events").insert({
    claim_id: claimId,
    code,
    description,
    amount,
    raw_payload: payload,
  });
  if (error) {
    console.error("[clearinghouse] era log error", error);
  }
}

export async function listEraEvents(params: { claimId?: string; claimNumber?: string; limit?: number }) {
  const client = getAdminClient();
  let query = client
    .from("era_events_view")
    .select("id, claim_id, claim_number, code, description, amount, raw_payload, created_at")
    .order("created_at", { ascending: false })
    .limit(params.limit ?? 50);

  if (params.claimId) {
    query = query.eq("claim_id", params.claimId);
  }
  if (params.claimNumber) {
    query = query.eq("claim_number", params.claimNumber);
  }

  const { data, error } = await query;
  if (error) {
    console.error("[clearinghouse] listEraEvents error", error);
    return [];
  }
  return data || [];
}

export async function listClaims(status?: ClaimStatus) {
  const client = getAdminClient();
  let query = client
    .from("claims_queue")
    .select("id, claim_number, status, patient_id, provider_id, region, created_at, updated_at")
    .order("created_at", { ascending: false })
    .limit(100);
  if (status) {
    query = query.eq("status", status);
  }
  const { data, error } = await query;
  if (error) {
    console.error("[clearinghouse] list error", error);
    throw new Error("Claim listesi alınamadı");
  }
  return data;
}

export function build837Payload(payload: Record<string, any>) {
  // Basit mock: gerçek 837 segment'leri yerine JSON string döndürüyoruz.
  return JSON.stringify({ ...payload, traceId: crypto.randomUUID(), createdAt: new Date().toISOString() });
}

export async function listDeniedClaimsWithEvents(limit = 50) {
  const client = getAdminClient();
  const { data: claims, error } = await client
    .from("claims_queue")
    .select("id, claim_number, status, patient_id, provider_id, region, created_at, updated_at")
    .in("status", ["denied", "error"])
    .order("updated_at", { ascending: false })
    .limit(limit);

  if (error) {
    console.error("[clearinghouse] denied list error", error);
    return [];
  }

  const numbers = (claims || []).map((c: any) => c.claim_number).filter(Boolean);
  let events: any[] = [];
  if (numbers.length > 0) {
    const { data: evData, error: evError } = await client
      .from("era_events_view")
      .select("id, claim_number, code, description, amount, raw_payload, created_at")
      .in("claim_number", numbers)
      .order("created_at", { ascending: false })
      .limit(limit * 3);
    if (evError) {
      console.error("[clearinghouse] era events fetch error", evError);
    } else {
      events = evData || [];
    }
  }

  return (claims || []).map((c: any) => ({
    ...c,
    eraEvents: events.filter((e) => e.claim_number === c.claim_number),
  }));
}

export async function getClaimDetail(claimId: string) {
  const client = getAdminClient();
  const { data, error } = await client
    .from("claims_queue")
    .select("*")
    .eq("id", claimId)
    .maybeSingle();
  if (error) {
    console.error("[clearinghouse] getClaimDetail error", error);
    return null;
  }
  return data;
}

export async function resubmitClaim(claimId: string) {
  const client = getAdminClient();
  const { data, error } = await client
    .from("claims_queue")
    .update({ status: "queued", updated_at: new Date().toISOString() })
    .eq("id", claimId)
    .select()
    .single();
  if (error) {
    console.error("[clearinghouse] resubmitClaim error", error);
    throw new Error("Claim yeniden gönderilemedi");
  }
  return data;
}

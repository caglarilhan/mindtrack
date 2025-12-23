import { createSupabaseServerClient } from "@/lib/supabaseClient";

export type IntegrationAuthType = "oauth" | "api_key" | "webhook";

export interface IntegrationCatalogItem {
  id: string;
  slug: string;
  name: string;
  description: string;
  category: string;
  logoUrl?: string | null;
  authType: IntegrationAuthType;
  docsUrl?: string | null;
}

export interface IntegrationConnection {
  id: string;
  clinicId: string;
  integrationId: string;
  status: "connected" | "disconnected" | "needs_action" | "error";
  settings: Record<string, unknown> | null;
  healthStatus?: string | null;
  errorMessage?: string | null;
  lastSyncedAt?: string | null;
}

export interface IntegrationEventLog {
  id: string;
  integrationId: string | null;
  clinicId: string | null;
  eventType: string;
  payload: Record<string, unknown>;
  status: string;
  receivedAt: string;
  processedAt?: string | null;
  error?: string | null;
}

const FALLBACK_CATALOG: IntegrationCatalogItem[] = [
  {
    id: "fallback-google",
    slug: "google-calendar",
    name: "Google Calendar",
    description: "Randevuları Google Calendar ile eşitleyin",
    category: "Calendar",
    logoUrl: "/integrations/google.svg",
    authType: "oauth",
    docsUrl: "https://support.google.com/calendar",
  },
  {
    id: "fallback-zoom",
    slug: "zoom",
    name: "Zoom",
    description: "Telehealth seansları için Zoom entegrasyonu",
    category: "Telehealth",
    logoUrl: "/integrations/zoom.svg",
    authType: "oauth",
    docsUrl: "https://developers.zoom.us",
  },
  {
    id: "fallback-twilio",
    slug: "twilio",
    name: "Twilio",
    description: "SMS ve sesli arama bildirimleri",
    category: "Messaging",
    logoUrl: "/integrations/twilio.svg",
    authType: "api_key",
    docsUrl: "https://www.twilio.com/docs",
  },
  {
    id: "fallback-stripe",
    slug: "stripe",
    name: "Stripe",
    description: "Ödeme ve abonelik yönetimi",
    category: "Billing",
    logoUrl: "/integrations/stripe.svg",
    authType: "oauth",
    docsUrl: "https://stripe.com/docs",
  },
  {
    id: "fallback-resend",
    slug: "resend",
    name: "Resend",
    description: "Transactional e-posta gönderimi",
    category: "Messaging",
    logoUrl: "/integrations/resend.svg",
    authType: "api_key",
    docsUrl: "https://resend.com/docs",
  },
];

export async function fetchIntegrationCatalog(): Promise<IntegrationCatalogItem[]> {
  try {
    const supabase = await createSupabaseServerClient();
    const { data, error } = await supabase
      .from("integrations_catalog")
      .select("id, slug, name, description, category, logo_url, auth_type, docs_url")
      .order("name", { ascending: true });
    if (error) {
      console.warn("[integrations] catalog error", error);
      return FALLBACK_CATALOG;
    }
    if (!data || data.length === 0) {
      return FALLBACK_CATALOG;
    }
    return data.map((item) => ({
      id: item.id,
      slug: item.slug,
      name: item.name,
      description: item.description ?? "",
      category: item.category ?? "General",
      logoUrl: item.logo_url,
      authType: (item.auth_type as IntegrationAuthType) || "api_key",
      docsUrl: item.docs_url,
    }));
  } catch (error) {
    console.error("[integrations] catalog exception", error);
    return FALLBACK_CATALOG;
  }
}

export async function fetchIntegrationConnections(clinicId: string): Promise<IntegrationConnection[]> {
  try {
    const supabase = await createSupabaseServerClient();
    const { data, error } = await supabase
      .from("integration_connections")
      .select("id, clinic_id, integration_id, status, settings, health_status, error_message, last_synced_at")
      .eq("clinic_id", clinicId);
    if (error) throw error;
    return (data || []).map((row) => ({
      id: row.id,
      clinicId: row.clinic_id,
      integrationId: row.integration_id,
      status: row.status,
      settings: row.settings,
      healthStatus: row.health_status,
      errorMessage: row.error_message,
      lastSyncedAt: row.last_synced_at,
    }));
  } catch (error) {
    console.error("[integrations] connections error", error);
    return [];
  }
}

export async function upsertIntegrationConnection(params: {
  clinicId: string;
  integrationSlug: string;
  status: "connected" | "disconnected" | "needs_action" | "error";
  settings?: Record<string, unknown>;
}): Promise<{ success: boolean; error?: string }> {
  try {
    const supabase = await createSupabaseServerClient();
    const { data: integration } = await supabase
      .from("integrations_catalog")
      .select("id")
      .eq("slug", params.integrationSlug)
      .maybeSingle();
    const integrationId = integration?.id || FALLBACK_CATALOG.find((c) => c.slug === params.integrationSlug)?.id;
    if (!integrationId) {
      return { success: false, error: "integration-not-found" };
    }
    const payload = {
      clinic_id: params.clinicId,
      integration_id: integrationId,
      status: params.status,
      settings: params.settings || null,
      updated_at: new Date().toISOString(),
    };
    const { error } = await supabase
      .from("integration_connections")
      .upsert(payload, { onConflict: "clinic_id,integration_id" });
    if (error) throw error;
    return { success: true };
  } catch (error) {
    console.error("[integrations] upsert error", error);
    return { success: false, error: (error as Error).message };
  }
}

export async function fetchIntegrationEvents(clinicId: string, limit = 10): Promise<IntegrationEventLog[]> {
  try {
    const supabase = await createSupabaseServerClient();
    const { data, error } = await supabase
      .from("integration_events")
      .select("id, integration_id, clinic_id, event_type, payload, status, received_at, processed_at, error")
      .eq("clinic_id", clinicId)
      .order("received_at", { ascending: false })
      .limit(limit);
    if (error) throw error;
    return (data || []).map((row) => ({
      id: row.id,
      integrationId: row.integration_id,
      clinicId: row.clinic_id,
      eventType: row.event_type,
      payload: row.payload || {},
      status: row.status,
      receivedAt: row.received_at,
      processedAt: row.processed_at,
      error: row.error,
    }));
  } catch (error) {
    console.error("[integrations] events error", error);
    return [];
  }
}

export interface AutomationRule {
  id: string;
  clinicId: string;
  name: string;
  trigger: Record<string, unknown>;
  conditions: Record<string, unknown>[] | null;
  actions: Record<string, unknown>[];
  enabled: boolean;
  lastRunAt?: string | null;
}

export async function fetchAutomationRules(clinicId: string): Promise<AutomationRule[]> {
  try {
    const supabase = await createSupabaseServerClient();
    const { data, error } = await supabase
      .from("automation_rules")
      .select("id, clinic_id, name, trigger, conditions, actions, enabled, last_run_at")
      .eq("clinic_id", clinicId)
      .order("created_at", { ascending: false });
    if (error) throw error;
    return (data || []).map((row) => ({
      id: row.id,
      clinicId: row.clinic_id,
      name: row.name,
      trigger: row.trigger || {},
      conditions: row.conditions || null,
      actions: row.actions || [],
      enabled: row.enabled,
      lastRunAt: row.last_run_at,
    }));
  } catch (error) {
    console.error("[automation] rules error", error);
    return [];
  }
}

export async function saveAutomationRule(payload: {
  id?: string;
  clinicId: string;
  name: string;
  trigger: Record<string, unknown>;
  conditions?: Record<string, unknown>[];
  actions: Record<string, unknown>[];
  enabled?: boolean;
}): Promise<{ success: boolean; error?: string }> {
  try {
    const supabase = await createSupabaseServerClient();
    const record = {
      id: payload.id || undefined,
      clinic_id: payload.clinicId,
      name: payload.name,
      trigger: payload.trigger,
      conditions: payload.conditions || null,
      actions: payload.actions,
      enabled: payload.enabled ?? true,
      updated_at: new Date().toISOString(),
    };
    const { error } = await supabase
      .from("automation_rules")
      .upsert(record, { onConflict: "id" });
    if (error) throw error;
    return { success: true };
  } catch (error) {
    console.error("[automation] save error", error);
    return { success: false, error: (error as Error).message };
  }
}

export async function logIntegrationEvent(params: {
  clinicId?: string;
  integrationSlug?: string;
  integrationId?: string;
  eventType: string;
  payload: Record<string, unknown>;
  status?: "queued" | "processed" | "failed";
  error?: string | null;
}) {
  try {
    const supabase = await createSupabaseServerClient();
    let integrationId = params.integrationId;
    if (!integrationId && params.integrationSlug) {
      const { data } = await supabase
        .from("integrations_catalog")
        .select("id")
        .eq("slug", params.integrationSlug)
        .maybeSingle();
      integrationId = data?.id || FALLBACK_CATALOG.find((c) => c.slug === params.integrationSlug)?.id || null;
    }
    await supabase.from("integration_events").insert({
      integration_id: integrationId,
      clinic_id: params.clinicId ?? null,
      event_type: params.eventType,
      payload: params.payload,
      status: params.status || "queued",
      error: params.error ?? null,
    });
  } catch (error) {
    console.error("[integrations] log event error", error);
  }
}

export async function processPendingIntegrationEvents(limit = 10): Promise<{ processed: number; errors: number }> {
  // Placeholder implementation
  console.log("[Integrations] Would process pending events:", limit);
  return { processed: 0, errors: 0 };
}

export async function fetchIntegrationHealth(clinicId: string): Promise<Record<string, { status: string; lastSync?: string }>> {
  // Placeholder implementation
  console.log("[Integrations] Would fetch health for clinic:", clinicId);
  return {};
}

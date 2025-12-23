import { createSupabaseServerClient } from "@/lib/supabaseClient";

export interface TelehealthBranding {
  clinicId: string;
  logoUrl: string | null;
  accentColor: string;
  waitingRoomMessage: string | null;
  helpLinks: { label: string; url: string }[];
  allowCaregiverJoin: boolean;
  defaultRegion: "us" | "eu";
}

const DEFAULT_BRANDING: TelehealthBranding = {
  clinicId: "default",
  logoUrl: null,
  accentColor: "#2563eb",
  waitingRoomMessage: "Danışmanınız birazdan bağlanacaktır. Lütfen bekleyiniz.",
  helpLinks: [
    { label: "Teknik destek", url: "mailto:support@mindtrack.dev" },
    { label: "Kriz hattı", url: "tel:988" },
  ],
  allowCaregiverJoin: true,
  defaultRegion: "us",
};

function mapRow(row: any): TelehealthBranding {
  if (!row) return DEFAULT_BRANDING;
  return {
    clinicId: row.clinic_id,
    logoUrl: row.logo_url,
    accentColor: row.accent_color || DEFAULT_BRANDING.accentColor,
    waitingRoomMessage: row.waiting_room_message,
    helpLinks: Array.isArray(row.help_links)
      ? row.help_links.map((link: any) => ({ label: link.label, url: link.url }))
      : DEFAULT_BRANDING.helpLinks,
    allowCaregiverJoin: row.allow_caregiver_join ?? true,
    defaultRegion: (row.default_region as "us" | "eu") || DEFAULT_BRANDING.defaultRegion,
  };
}

export async function fetchTelehealthBranding(clinicId: string): Promise<TelehealthBranding> {
  try {
    const supabase = await createSupabaseServerClient();
    const { data, error } = await supabase
      .from("telehealth_branding")
      .select("clinic_id, logo_url, accent_color, waiting_room_message, help_links, allow_caregiver_join, default_region")
      .eq("clinic_id", clinicId)
      .maybeSingle();

    if (error) {
      console.error("[telehealthBranding] fetch error", error);
      return DEFAULT_BRANDING;
    }

    return mapRow(data);
  } catch (error) {
    console.error("[telehealthBranding] fetch exception", error);
    return DEFAULT_BRANDING;
  }
}

interface UpsertBrandingInput {
  clinicId: string;
  logoUrl?: string | null;
  accentColor?: string;
  waitingRoomMessage?: string | null;
  helpLinks?: { label: string; url: string }[];
  allowCaregiverJoin?: boolean;
  defaultRegion?: "us" | "eu";
}

export async function upsertTelehealthBranding(input: UpsertBrandingInput) {
  const supabase = await createSupabaseServerClient();
  const payload = {
    clinic_id: input.clinicId,
    logo_url: input.logoUrl ?? null,
    accent_color: input.accentColor ?? DEFAULT_BRANDING.accentColor,
    waiting_room_message: input.waitingRoomMessage ?? DEFAULT_BRANDING.waitingRoomMessage,
    help_links: input.helpLinks ?? DEFAULT_BRANDING.helpLinks,
    allow_caregiver_join: input.allowCaregiverJoin ?? true,
    default_region: input.defaultRegion ?? DEFAULT_BRANDING.defaultRegion,
    updated_at: new Date().toISOString(),
  };

  const { error } = await supabase.from("telehealth_branding").upsert(payload, { onConflict: "clinic_id" });
  if (error) {
    console.error("[telehealthBranding] upsert error", error);
    return { success: false, error: error.message };
  }
  return { success: true };
}

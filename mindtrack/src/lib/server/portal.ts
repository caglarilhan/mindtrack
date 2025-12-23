import { createSupabaseServerClient } from "@/lib/supabaseClient";
import { computeCareGaps } from "@/lib/server/careGaps";
import { fetchSafetySummaryByPatients } from "@/lib/server/safety";

export interface PortalAppointment {
  id: string;
  date: string;
  provider: string;
  status: string;
  location?: string | null;
}

export interface PortalInvoice {
  id: string;
  amount: number;
  dueDate: string;
  status: string;
}

export interface PortalClaim {
  id: string;
  claimNumber: string;
  status: string;
  amount?: number;
  updatedAt?: string;
}

export interface ClientPortalData {
  patientId: string;
  patientName: string;
  region: "us" | "eu";
  appointments: PortalAppointment[];
  invoices: PortalInvoice[];
  claims: PortalClaim[];
  careGaps: Awaited<ReturnType<typeof computeCareGaps>>;
  safetySummary: Awaited<ReturnType<typeof fetchSafetySummaryByPatients>>[string] | null;
  nextActions: string[];
}

const FALLBACK_DATA = {
  appointments: [
    {
      id: "appt-demo-1",
      date: new Date(Date.now() + 86400000).toISOString(),
      provider: "Dr. Aylin Kaya",
      status: "scheduled",
      location: "Telehealth",
    },
  ],
  invoices: [
    {
      id: "inv-demo-1",
      amount: 120,
      dueDate: new Date(Date.now() + 3 * 86400000).toISOString(),
      status: "pending",
    },
  ],
  claims: [
    {
      id: "claim-demo-1",
      claimNumber: "CLM-1001",
      status: "submitted",
      amount: 120,
      updatedAt: new Date().toISOString(),
    },
  ],
};

export async function fetchClientPortalData(patientId: string, region: "us" | "eu" = "us"): Promise<ClientPortalData> {
  const supabase = await createSupabaseServerClient();
  const patient = await supabase
    .from("patients")
    .select("id, full_name")
    .eq("id", patientId)
    .maybeSingle();

  const [appointmentsRes, invoicesRes, claimsRes, careGaps, safetyMap] = await Promise.all([
    supabase
      .from("appointments")
      .select("id, scheduled_at, provider_name, status, location")
      .eq("patient_id", patientId)
      .order("scheduled_at", { ascending: true })
      .limit(5),
    supabase
      .from("invoices")
      .select("id, amount, due_date, status")
      .eq("patient_id", patientId)
      .order("due_date", { ascending: true })
      .limit(5),
    supabase
      .from("claims_queue")
      .select("id, claim_number, status, payload, updated_at")
      .eq("patient_id", patientId)
      .order("updated_at", { ascending: false })
      .limit(5),
    computeCareGaps(patientId, region),
    fetchSafetySummaryByPatients([patientId], region),
  ]);

  const appointments = (appointmentsRes.data || []).map((appt) => ({
    id: appt.id,
    date: appt.scheduled_at,
    provider: appt.provider_name,
    status: appt.status,
    location: appt.location,
  }));

  const invoices = (invoicesRes.data || []).map((inv) => ({
    id: inv.id,
    amount: inv.amount,
    dueDate: inv.due_date,
    status: inv.status,
  }));

  const claims = (claimsRes.data || []).map((claim) => ({
    id: claim.id,
    claimNumber: claim.claim_number,
    status: claim.status,
    amount: claim.payload?.amount,
    updatedAt: claim.updated_at,
  }));

  return {
    patientId,
    patientName: patient.data?.full_name || "MindTrack Patient",
    region,
    appointments: appointments.length ? appointments : FALLBACK_DATA.appointments,
    invoices: invoices.length ? invoices : FALLBACK_DATA.invoices,
    claims: claims.length ? claims : FALLBACK_DATA.claims,
    careGaps,
    safetySummary: safetyMap[patientId] || null,
    nextActions: buildNextActions(careGaps, invoices, claims),
  };
}

function buildNextActions(careGaps: Awaited<ReturnType<typeof computeCareGaps>>, invoices: PortalInvoice[], claims: PortalClaim[]) {
  const actions: string[] = [];
  const unpaid = invoices.find((inv) => inv.status !== "paid");
  if (unpaid) {
    actions.push(`Open invoice ${unpaid.id} tutarı $${unpaid.amount.toFixed(2)} için ödeme yapın.`);
  }
  const highGap = careGaps.find((gap) => gap.severity === "high" || gap.severity === "critical");
  if (highGap) {
    actions.push(`Care gap: ${highGap.title} → ${highGap.recommendedAction}`);
  }
  const deniedClaim = claims.find((claim) => claim.status === "denied");
  if (deniedClaim) {
    actions.push(`Claim ${deniedClaim.claimNumber} reddedildi; destek ekibiyle iletişime geçin.`);
  }
  if (actions.length === 0) {
    actions.push("Her şey yolunda! Bir sonraki seans için hazırlanın.");
  }
  return actions;
}

export async function fetchCaregiverPortalData(patientId: string, region: "us" | "eu" = "us") {
  const clientData = await fetchClientPortalData(patientId, region);
  return {
    ...clientData,
    caregiverSummary: {
      riskLevel: clientData.safetySummary?.highestSeverity ?? "none",
      primaryContact: clientData.safetySummary?.primaryContact || "Clinic Support",
      careGaps: clientData.careGaps.slice(0, 3),
    },
  };
}

/**
 * Care Gap Monitor
 * Tedavi planı, seanslar, ilaçlar, ölçümler ve güvenlik uyarılarına göre bakım boşluklarını tespit eder.
 */

import { createSupabaseServerClient } from "@/lib/supabaseClient";
import type { TreatmentPlan, TherapySession } from "./therapy";
import type { AssessmentScale } from "./assessments";
import type { SafetySummary } from "./safety";
import type { Medication } from "./medication";

export type CareGapSeverity = "info" | "low" | "medium" | "high" | "critical";

export interface CareGap {
  id: string;
  patientId: string;
  title: string;
  description: string;
  severity: CareGapSeverity;
  category: "therapy" | "medication" | "assessment" | "safety" | "engagement";
  recommendedAction: string;
  relatedModules: string[]; // örn: ['/dashboard/therapy', '/dashboard/analytics/outcomes']
}

interface RawAssessment {
  scale: AssessmentScale;
  score: number;
  taken_at: string;
}

interface CareGapContext {
  plan: TreatmentPlan | null;
  sessions: TherapySession[];
  assessments: RawAssessment[];
  medications: Medication[];
  safety: SafetySummary | null;
}

export async function computeCareGaps(patientId: string, region: "us" | "eu" = "us"): Promise<CareGap[]> {
  const supabase = await createSupabaseServerClient();
  const now = new Date();
  const cutoff90 = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000).toISOString();

  // Paralel sorgular
  const [planRes, sessionRes, assessRes, medsRes, safetyRes] = await Promise.all([
    supabase
      .from("treatment_plans")
      .select("id, patient_id, therapist_id, diagnosis_code, goals, interventions, estimated_sessions, start_date, end_date, status")
      .eq("patient_id", patientId)
      .eq("status", "active")
      .maybeSingle(),
    supabase
      .from("therapy_sessions")
      .select("id, patient_id, therapist_id, session_date, session_type, duration, status, goals, homework, progress_rating")
      .eq("patient_id", patientId)
      .gte("session_date", cutoff90)
      .order("session_date", { ascending: false }),
    supabase
      .from("patient_assessments")
      .select("scale, score, taken_at")
      .eq("patient_id", patientId)
      .gte("taken_at", cutoff90),
    supabase
      .from("medications")
      .select("id, patient_id, medication_name, dosage, frequency, start_date, end_date, prescriber_id, status, adherence")
      .eq("patient_id", patientId),
    supabase
      .from("patient_safety_alerts")
      .select("patient_id, category, severity, note, updated_at")
      .eq("patient_id", patientId)
      .eq("region", region)
      .order("updated_at", { ascending: false })
      .limit(1),
  ]);

  const ctx: CareGapContext = {
    plan: (planRes.data as any) || null,
    sessions: (sessionRes.data as any) || [],
    assessments: (assessRes.data as any) || [],
    medications: (medsRes.data as any) || [],
    safety: buildSafetySummary(patientId, safetyRes.data as any[] | null),
  };

  const gaps: CareGap[] = [];
  gaps.push(...detectTherapyGaps(ctx, patientId));
  gaps.push(...detectAssessmentGaps(ctx, patientId));
  gaps.push(...detectMedicationGaps(ctx, patientId));
  gaps.push(...detectSafetyGaps(ctx, patientId, region));

  return gaps;
}

function detectTherapyGaps(ctx: CareGapContext, patientId: string): CareGap[] {
  const gaps: CareGap[] = [];
  const latestSession = ctx.sessions[0];

  // 1) Aktif plan var ama son 21 gündür seans yok
  if (ctx.plan) {
    if (!latestSession) {
      gaps.push({
        id: `${patientId}-therapy-no-session`,
        patientId,
        title: "Aktif plan var, seans yok",
        description: "Aktif tedavi planı bulunuyor ancak son 90 gün içinde tamamlanan seans kaydı yok.",
        severity: "high",
        category: "therapy",
        recommendedAction: "Hemen takip randevusu planlayın veya plan durumunu gözden geçirin.",
        relatedModules: ["/dashboard/therapy", "/dashboard/psychology"],
      });
    } else {
      const lastDate = new Date(latestSession.sessionDate);
      const diffDays = (Date.now() - lastDate.getTime()) / (1000 * 60 * 60 * 24);
      if (diffDays > 21) {
        gaps.push({
          id: `${patientId}-therapy-gap-21d`,
          patientId,
          title: "Tedavi planında aralık oluştu",
          description: `Son seans üzerinden yaklaşık ${Math.round(diffDays)} gün geçti.",`,
          severity: diffDays > 35 ? "high" : "medium",
          category: "therapy",
          recommendedAction: "Hastayla iletişime geçip yeni seans planlayın veya dropout riskini değerlendirin.",
          relatedModules: ["/dashboard/therapy"],
        });
      }
    }
  }

  // 2) İlerleme skoru düşük
  const completed = ctx.sessions.filter((s) => s.status === "completed" && s.progressRating != null);
  if (completed.length >= 3) {
    const avg =
      completed.reduce((sum, s) => sum + (s.progressRating || 0), 0) / completed.length;
    if (avg < 5) {
      gaps.push({
        id: `${patientId}-therapy-low-progress`,
        patientId,
        title: "Düşük terapi ilerlemesi",
        description: `Son ${completed.length} seansın ortalama ilerleme puanı ${avg.toFixed(1)} (10 üzerinden).`,
        severity: "medium",
        category: "therapy",
        recommendedAction:
          "Müdahale yaklaşımını gözden geçirin; süpervizyon veya farklı teknik kombinasyonu düşünün.",
        relatedModules: ["/dashboard/therapy", "/dashboard/analytics/outcomes"],
      });
    }
  }

  return gaps;
}

function detectAssessmentGaps(ctx: CareGapContext, patientId: string): CareGap[] {
  const gaps: CareGap[] = [];
  const phq = ctx.assessments.filter((a) => a.scale === "phq-9");
  const gad = ctx.assessments.filter((a) => a.scale === "gad-7");

  // 3) Yüksek depresyon/anksiyete skoru ama son 30 günde tekrar yok
  const highPhq = phq.find((a) => a.score >= 15);
  if (highPhq) {
    const lastDate = new Date(highPhq.taken_at);
    const diffDays = (Date.now() - lastDate.getTime()) / (1000 * 60 * 60 * 24);
    if (diffDays > 30) {
      gaps.push({
        id: `${patientId}-assessment-phq-followup`,
        patientId,
        title: "PHQ-9 takibi eksik",
        description: "Yüksek PHQ-9 skoru sonrası 30 günden uzun süredir yeniden değerlendirme yapılmamış.",
        severity: "medium",
        category: "assessment",
        recommendedAction: "Yeni bir PHQ-9 değerlendirmesi planlayın ve trendi izleyin.",
        relatedModules: ["/dashboard/analytics/outcomes"],
      });
    }
  }

  const highGad = gad.find((a) => a.score >= 15);
  if (highGad) {
    const lastDate = new Date(highGad.taken_at);
    const diffDays = (Date.now() - lastDate.getTime()) / (1000 * 60 * 60 * 24);
    if (diffDays > 30) {
      gaps.push({
        id: `${patientId}-assessment-gad-followup`,
        patientId,
        title: "GAD-7 takibi eksik",
        description: "Yüksek GAD-7 skoru sonrası 30 günden uzun süredir yeniden değerlendirme yapılmamış.",
        severity: "medium",
        category: "assessment",
        recommendedAction: "Yeni bir GAD-7 değerlendirmesi planlayın.",
        relatedModules: ["/dashboard/analytics/outcomes"],
      });
    }
  }

  return gaps;
}

function detectMedicationGaps(ctx: CareGapContext, patientId: string): CareGap[] {
  const gaps: CareGap[] = [];
  const activeMeds = ctx.medications.filter((m) => m.status === "active");

  for (const med of activeMeds) {
    if (typeof med.adherence === "number" && med.adherence < 0.6) {
      gaps.push({
        id: `${patientId}-medication-adherence-${med.id}`,
        patientId,
        title: "Düşük ilaç uyumu",
        description: `${med.medicationName} için tahmini uyum %${Math.round(
          med.adherence * 100
        )} seviyesinde.",`,
        severity: "high",
        category: "medication",
        recommendedAction: "İlaç yan etkileri, doz ve hasta motivasyonunu değerlendirin; gerekirse rejimi sadeleştirin.",
        relatedModules: ["/dashboard/analytics/safety", "/dashboard/psychiatry"],
      });
    }
  }

  return gaps;
}

function detectSafetyGaps(ctx: CareGapContext, patientId: string, region: "us" | "eu"): CareGap[] {
  const gaps: CareGap[] = [];

  if (!ctx.safety) return gaps;

  // 5) Yüksek self-harm riski ama kriz planı yok
  if (ctx.safety.highestSeverity === "high" && !ctx.safety.categories.includes("crisis-plan")) {
    gaps.push({
      id: `${patientId}-safety-crisis-plan`,
      patientId,
      title: "Kriz planı eksik",
      description: "Yüksek özkıyım riski olan hasta için onaylı kriz planı bulunmuyor.",
      severity: "critical",
      category: "safety",
      recommendedAction:
        region === "us"
          ? "Hasta ile birlikte 988 numarasını içeren yazılı kriz planı oluşturun."
          : "Hasta ile birlikte 112 ve yerel kriz hatlarını içeren yazılı kriz planı oluşturun.",
      relatedModules: ["/dashboard/analytics/safety", "/dashboard/psychiatry"],
    });
  }

  return gaps;
}

function buildSafetySummary(patientId: string, rows: any[] | null): SafetySummary | null {
  if (!rows || rows.length === 0) return null;
  const row = rows[0];
  return {
    patientId,
    highestSeverity: row.severity,
    categories: [row.category],
    lastUpdated: row.updated_at,
    notes: row.note || undefined,
  };
}

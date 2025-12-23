import { ClinicalPlanTemplate, suggestPlanForDiagnosis, getRelapseScore } from "./clinicalPlans";
import { DSM5Diagnosis } from "./dsm5";

export interface HomeworkSuggestion {
  title: string;
  description: string;
  cadence: string;
  adherenceTips: string[];
}

export interface FollowUpMessage {
  channel: "email" | "sms" | "portal";
  subject: string;
  body: string;
}

export function generateHomeworkSuggestions(options: {
  diagnosis: DSM5Diagnosis | null;
  sessionFocus?: string;
  adherenceScore?: number; // 0-1
}): HomeworkSuggestion[] {
  const { diagnosis, sessionFocus, adherenceScore = 0.8 } = options;
  const template = suggestPlanForDiagnosis(diagnosis);
  if (!template) return [];

  const base: HomeworkSuggestion[] = template.homeworkIdeas.map((idea) => ({
    title: idea,
    description: `${idea} pratiği, ${template.sessionFrequency} programı ile uyumlu şekilde takip edilir. ${sessionFocus ? `Bu hafta odak: ${sessionFocus}.` : ""}`.trim(),
    cadence: "Haftada 3",
    adherenceTips: [
      "Günlük hatırlatıcı kur",
      "Seans öncesi kısa özet hazırla",
    ],
  }));

  if (adherenceScore < 0.6) {
    base.push({
      title: "Mini Görev",
      description: "Ödevi küçülterek başlanacak ilk adımı yaz",
      cadence: "Günde 1",
      adherenceTips: ["Tamamlanan her adımı portala yükle", "Ödüllendirici aktivite ile eşleştir"],
    });
  }

  return base;
}

export function buildFollowUpMessage(options: {
  diagnosis: DSM5Diagnosis | null;
  language?: "tr" | "en" | "es" | "de";
  riskLevel?: "low" | "moderate" | "high";
}): FollowUpMessage {
  const { diagnosis, language = "tr", riskLevel = "low" } = options;
  const subjectMap = {
    tr: "Seans Sonrası Takip",
    en: "Session Follow-up",
    es: "Seguimiento de Sesión",
    de: "Sitzungsnachbereitung",
  } as const;

  const riskLine = {
    low: "Planlanan ödevleri uyguladığınızda süreci desteklemiş olursunuz.",
    moderate: "Belirlediğimiz ödevleri tamamlamak belirtileri hafifletmeye yardımcı olacak.",
    high: "Ödevleri uygularken zorlanırsanız anında portal üzerinden haber verebilirsiniz.",
  }[riskLevel];

  const diagName = diagnosis?.name || "görüşme";

  const bodyTr = `Bugünkü ${diagName} çalışmasını özetledim. Ödevler MindTrack portalında. ${riskLine}`;
  const translations: Record<typeof language, string> = {
    tr: bodyTr,
    en: `I recapped today's ${diagName} work. Homework is in the MindTrack portal. ${riskLine}`,
    es: `Resumí el trabajo de ${diagName} de hoy. Las tareas están en el portal. ${riskLine}`,
    de: `Ich habe die heutige ${diagName}-Sitzung zusammengefasst. Die Aufgaben stehen im Portal. ${riskLine}`,
  } as const;

  return {
    channel: "portal",
    subject: subjectMap[language],
    body: translations[language],
  };
}

export function buildOutcomeBenchmark(params: {
  scale: "PHQ-9" | "GAD-7" | "PCL-5";
  patientAverage: number;
}): { cohortMedian: number; percentile: number; status: string } {
  const COHORT_MEDIANS = {
    "PHQ-9": 11,
    "GAD-7": 9,
    "PCL-5": 28,
  } as const;

  const median = COHORT_MEDIANS[params.scale];
  const percentile = Math.max(1, Math.min(99, Math.round((params.patientAverage / median) * 50)));
  const status = params.patientAverage <= median ? "On Track" : "Needs Attention";

  return { cohortMedian: median, percentile, status };
}

export function buildRelapseRadar(params: {
  recentPHQ9?: number;
  baselinePHQ9?: number;
  missedSessions?: number;
  homeworkAdherence?: number;
  crisisFlags?: number;
}) {
  const score = getRelapseScore(params);
  let level: "low" | "warning" | "critical" = "low";
  if (score >= 70) level = "critical";
  else if (score >= 40) level = "warning";

  return { score, level };
}

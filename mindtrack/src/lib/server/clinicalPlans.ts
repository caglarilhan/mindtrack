/**
 * Clinical AI Workbench — tanıya göre tedavi planı ve protokol önerileri
 */

import { DSM5Diagnosis } from "./dsm5";

export interface ClinicalPlanTemplate {
  diagnosisCode: string; // DSM-5 code
  icd10Code: string;
  title: string;
  sessionFrequency: string;
  durationWeeks: number;
  coreGoals: string[];
  interventions: string[];
  homeworkIdeas: string[];
  outcomeMeasures: string[];
  relapseSignals: string[];
}

const PLAN_LIBRARY: ClinicalPlanTemplate[] = [
  {
    diagnosisCode: "296.33",
    icd10Code: "F32.2",
    title: "MDD · CBT + Aktivasyon",
    sessionFrequency: "Haftada 1 (60 dk)",
    durationWeeks: 12,
    coreGoals: [
      "Anhedoni ve motivasyon düşüklüğünü azaltmak",
      "Bilişsel çarpıtmaları yeniden yapılandırmak",
      "Uyku ve iştah düzenini stabilize etmek",
    ],
    interventions: [
      "Davranışsal aktivasyon planı",
      "Çekirdek inanç keşfi ve yeniden çerçeveleme",
      "Uyku hijyeni protokolü",
    ],
    homeworkIdeas: [
      "Haftalık aktivite-mood kaydı",
      "Otomatik düşünce günlüğü",
      "Uyku ve beslenme takip formu",
    ],
    outcomeMeasures: ["PHQ-9", "HAM-D", "Beck Hopelessness"],
    relapseSignals: [
      "PHQ-9 skorunun 5+ artması",
      "Aktivite kaydında 3 gün art arda boşluk",
      "Uyku < 5 saat",
    ],
  },
  {
    diagnosisCode: "300.02",
    icd10Code: "F41.1",
    title: "GAD · CBT + Somatik",
    sessionFrequency: "Haftada 1 (50 dk)",
    durationWeeks: 10,
    coreGoals: [
      "Worry döngüsünü kırmak",
      "Somatik belirtileri regüle etmek",
      "Anksiyete tetikleyicilerini yeniden çerçevelemek",
    ],
    interventions: [
      "Worry exposure ve planlama",
      "PMR + nefes egzersizleri",
      "Bilişsel yeniden yapılandırma",
    ],
    homeworkIdeas: [
      "Worry log + yapılandırılmış problem çözme",
      "Gevşeme egzersizi audio takibi",
      "Tetikleyici-düşünce-duygu defteri",
    ],
    outcomeMeasures: ["GAD-7", "PSWQ"],
    relapseSignals: [
      "GAD-7 skor artışı ≥4",
      "Gevşeme pratiklerinin < %50 uygulanması",
      "Uyku bozukluğu geri dönüşü",
    ],
  },
  {
    diagnosisCode: "309.81",
    icd10Code: "F43.10",
    title: "PTSD · TF-CBT",
    sessionFrequency: "Haftada 1 (75 dk)",
    durationWeeks: 16,
    coreGoals: [
      "Travma anlatısını güvenli şekilde işlemek",
      "Hiperarousal belirtilerini azaltmak",
      "Yakın ilişkilerde yeniden bağ kurmak",
    ],
    interventions: [
      "Psychoeducation + grounding",
      "İmgeleme yeniden betimleme",
      "In-vivo/imaginal maruziyet",
    ],
    homeworkIdeas: [
      "Grounding kartları",
      "Maruziyet hazırlık listeleri",
      "Destekli journaling",
    ],
    outcomeMeasures: ["PCL-5", "CAPS-5"],
    relapseSignals: [
      "PCL-5 artışı ≥10",
      "Flashback sıklığında artış",
      "Avoidance davranışında artış",
    ],
  },
];

export function suggestPlanForDiagnosis(diagnosis: DSM5Diagnosis | null) {
  if (!diagnosis) return null;
  return PLAN_LIBRARY.find((plan) => plan.diagnosisCode === diagnosis.code) || null;
}

export function listPlanTemplates() {
  return PLAN_LIBRARY;
}

export function getRelapseScore(params: { recentPHQ9?: number; baselinePHQ9?: number; missedSessions?: number; homeworkAdherence?: number; crisisFlags?: number; }) {
  const { recentPHQ9 = 0, baselinePHQ9 = 0, missedSessions = 0, homeworkAdherence = 1, crisisFlags = 0 } = params;
  const symptomDelta = Math.max(0, recentPHQ9 - baselinePHQ9);
  const adherencePenalty = (1 - homeworkAdherence) * 20; // %50 adherence → 10 puan
  const sessionPenalty = Math.min(20, missedSessions * 5);
  const crisisPenalty = crisisFlags * 15;
  const raw = symptomDelta * 2 + adherencePenalty + sessionPenalty + crisisPenalty;
  return Math.min(100, Math.round(raw));
}


import { Prescription, RegionId } from "./types";

type RegionRule = {
  limit: number;
  highUsage: number; // %
  criticalUsage: number; // %
  label: string;
  notes: string[];
};

const REGION_RULES: Record<RegionId, RegionRule> = {
  TR: {
    limit: 150,
    highUsage: 75,
    criticalUsage: 90,
    label: "TİTCK kontrollü reçete kotası (örnek)",
    notes: [
      "Kırmızı/yeşil reçete kontrolleri Sprint 3+’ta detaylanacak.",
      "E-Nabız entegrasyonu planlı.",
    ],
  },
  US: {
    limit: 200,
    highUsage: 70,
    criticalUsage: 90,
    label: "DEA Schedule II-IV hacim limiti (örnek)",
    notes: ["EPCS gereksinimleri (2FA, sertifika) Sprint 3’te ele alınacak."],
  },
  EU: {
    limit: 180,
    highUsage: 70,
    criticalUsage: 90,
    label: "EMA / ülke bazlı ATC kontrollü sınırlar (örnek)",
    notes: ["GDPR uyumluluğu için audit ve veri minimizasyonu uygulanacak."],
  },
};

export function calculateComplianceSummary(prescriptions: Prescription[], region: RegionId) {
  const rule = REGION_RULES[region];

  const controlled = prescriptions.filter(
    (p) => p.risk === "high" || p.risk === "critical" || p.controlledSchedule
  );

  const scheduleCounts = controlled.reduce<Record<string, number>>((acc, p) => {
    const sch = p.controlledSchedule;
    if (sch) acc[sch] = (acc[sch] || 0) + 1;
    return acc;
  }, {});

  const usage = Math.min(100, (controlled.length / rule.limit) * 100);
  const score = Math.max(30, 100 - usage); // basit ters oran
  const remaining = Math.max(0, rule.limit - controlled.length);

  const warnings: string[] = [];
  if (usage >= rule.criticalUsage) warnings.push("Kontrollü madde limitine çok yakınsınız.");
  else if (usage >= rule.highUsage) warnings.push("Kontrollü madde kullanım oranı yüksek.");

  ["II", "III", "IV"].forEach((sch) => {
    if (scheduleCounts[sch]) warnings.push(`Schedule ${sch} reçete sayısı: ${scheduleCounts[sch]}`);
  });

  return {
    score: Math.round(score),
    totalControlled: controlled.length,
    limit: rule.limit,
    usagePercent: Number(usage.toFixed(1)),
    remaining,
    warnings,
    scheduleCounts,
    ruleLabel: rule.label,
    ruleNotes: rule.notes,
  };
}



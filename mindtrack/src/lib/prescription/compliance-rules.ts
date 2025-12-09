import { Prescription, RegionId } from "./types";

export function calculateComplianceSummary(prescriptions: Prescription[], region: RegionId) {
  // risk veya controlledSchedule içerenler kontrollü olarak sayılır
  const controlled = prescriptions.filter(
    (p) => p.risk === "high" || p.risk === "critical" || p.controlledSchedule
  );
  const scheduleCounts = controlled.reduce(
    (acc, p) => {
      const sch = p.controlledSchedule;
      if (sch) acc[sch] = (acc[sch] || 0) + 1;
      return acc;
    },
    {} as Record<string, number>
  );

  const limit = region === "US" ? 200 : region === "TR" ? 150 : 180;
  const usage = Math.min(100, (controlled.length / limit) * 100);
  const score = Math.max(40, 100 - usage); // basit ters oran
  const warnings: string[] = [];
  if (usage > 90) warnings.push("Kontrollü madde limitine çok yakınsınız.");
  if (usage > 75) warnings.push("Kontrollü madde kullanım oranı yüksek.");
  if (scheduleCounts["II"]) warnings.push(`Schedule II reçete sayısı: ${scheduleCounts["II"]}`);
  if (scheduleCounts["III"]) warnings.push(`Schedule III reçete sayısı: ${scheduleCounts["III"]}`);
  if (scheduleCounts["IV"]) warnings.push(`Schedule IV reçete sayısı: ${scheduleCounts["IV"]}`);

  return {
    score: Math.round(score),
    totalControlled: controlled.length,
    limit,
    usagePercent: Number(usage.toFixed(1)),
    warnings,
    scheduleCounts,
  };
}



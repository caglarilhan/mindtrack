export type InteractionRisk = "none" | "minor" | "moderate" | "major";

export interface DrugInteractionResult {
  drugA: string;
  drugB: string;
  risk: InteractionRisk;
  message: string;
}

export interface DoseValidationResult {
  ok: boolean;
  level: "ok" | "warning" | "danger";
  message: string;
}

export interface AllergyCheckResult {
  hasAllergy: boolean;
  message: string;
}

// Mock rules: simple string contains checks
const sedatives = ["alprazolam", "xanax", "diazepam", "clonazepam"];
const opioids = ["morphine", "oxycodone", "fentanyl", "codeine", "tramadol"];
const ssri = ["sertraline", "paroxetine", "fluoxetine", "escitalopram"];

export function checkInteractions(drugs: string[]): DrugInteractionResult[] {
  const results: DrugInteractionResult[] = [];
  const lower = drugs.map((d) => d.toLowerCase());

  // Xanax + opioid -> major
  lower.forEach((a, i) => {
    lower.slice(i + 1).forEach((b) => {
      if (sedatives.includes(a) && opioids.includes(b)) {
        results.push({
          drugA: drugs[i],
          drugB: drugs[lower.indexOf(b)],
          risk: "major",
          message: "Benzodiazepin + opioid kombinasyonu solunum depresyonu riskini artırır.",
        });
      } else if (sedatives.includes(a) && sedatives.includes(b)) {
        results.push({
          drugA: drugs[i],
          drugB: drugs[lower.indexOf(b)],
          risk: "major",
          message: "İki benzodiazepin kombinasyonu sedasyon ve bağımlılık riskini artırır.",
        });
      } else if (ssri.includes(a) && b.includes("tramadol")) {
        results.push({
          drugA: drugs[i],
          drugB: drugs[lower.indexOf(b)],
          risk: "major",
          message: "SSRI + Tramadol serotonin sendromu riskini artırır.",
        });
      } else if (ssri.includes(a) && ssri.includes(b)) {
        results.push({
          drugA: drugs[i],
          drugB: drugs[lower.indexOf(b)],
          risk: "moderate",
          message: "Aynı sınıf SSRI kombinasyonu önerilmez.",
        });
      }
    });
  });

  return results;
}

export function checkDose(drug: string, doseMg?: number): DoseValidationResult {
  if (!doseMg) return { ok: true, level: "ok", message: "Doz belirtilmedi" };
  const name = drug.toLowerCase();
  if (ssri.some((d) => name.includes(d)) && doseMg > 200) {
    return { ok: false, level: "danger", message: "SSRI için 200 mg/gün üzerinde doz önerilmez." };
  }
  if (sedatives.some((d) => name.includes(d)) && doseMg > 4) {
    return { ok: false, level: "warning", message: "Yüksek benzo dozu, sedasyon riski." };
  }
  return { ok: true, level: "ok", message: "Doz aralıkta görünüyor." };
}

export function checkAllergy(drug: string, patientAllergies: string[]): AllergyCheckResult {
  const hit = patientAllergies.some((a) => drug.toLowerCase().includes(a.toLowerCase()));
  if (hit) {
    return { hasAllergy: true, message: `Alerji uyarısı: ${drug} hastanın alerji listesinde.` };
  }
  return { hasAllergy: false, message: "" };
}



export type LabRiskLevel = "normal" | "borderline" | "critical";

export interface LabResult {
  id: string;
  patientId: string;
  prescriptionId?: string;
  testType: string;
  value: number | string;
  unit: string;
  referenceRange: string;
  resultDate: string;
  riskLevel: LabRiskLevel;
}

export const mockLabResults: LabResult[] = [
  {
    id: "LAB-1",
    patientId: "P-1003",
    prescriptionId: "RX-003",
    testType: "Lithium Level",
    value: 0.8,
    unit: "mEq/L",
    referenceRange: "0.6 - 1.2",
    resultDate: "2024-12-10",
    riskLevel: "normal",
  },
  {
    id: "LAB-2",
    patientId: "P-1002",
    prescriptionId: "RX-002",
    testType: "LFT (ALT)",
    value: 65,
    unit: "U/L",
    referenceRange: "7 - 56",
    resultDate: "2024-12-01",
    riskLevel: "borderline",
  },
];



export type SideEffectSeverity = "mild" | "moderate" | "severe";

export interface SideEffectEntry {
  id: string;
  patientId: string;
  prescriptionId?: string;
  drugName: string;
  sideEffectName: string;
  severity: SideEffectSeverity;
  firstObserved: string;
  lastUpdated: string;
}

export const mockSideEffects: SideEffectEntry[] = [
  {
    id: "SE-1",
    patientId: "P-1001",
    prescriptionId: "RX-001",
    drugName: "Sertraline",
    sideEffectName: "Nausea",
    severity: "mild",
    firstObserved: "2024-11-20",
    lastUpdated: "2024-12-01",
  },
  {
    id: "SE-2",
    patientId: "P-1003",
    prescriptionId: "RX-003",
    drugName: "Alprazolam",
    sideEffectName: "Drowsiness",
    severity: "moderate",
    firstObserved: "2024-12-02",
    lastUpdated: "2024-12-08",
  },
];



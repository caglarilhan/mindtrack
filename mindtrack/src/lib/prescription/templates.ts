import { PrescriptionMedication, RegionId } from "./types";

export interface PrescriptionTemplate {
  id: string;
  name: string;
  region: RegionId;
  medications: PrescriptionMedication[];
  notes?: string;
}

let templates: PrescriptionTemplate[] = [
  {
    id: "TPL-1",
    name: "SSRI Başlangıç",
    region: "TR",
    medications: [
      { name: "Sertraline", doseMg: 50, frequency: "qd" },
      { name: "Propranolol", doseMg: 10, frequency: "bid" },
    ],
    notes: "Sabah, yemekle birlikte",
  },
  {
    id: "TPL-2",
    name: "Anksiyete Kısa Dönem",
    region: "US",
    medications: [{ name: "Alprazolam", doseMg: 0.5, frequency: "prn" }],
    notes: "Kısa süreli kullanım, en fazla 2 hafta",
  },
];

export function getTemplates(region?: RegionId) {
  return region ? templates.filter((t) => t.region === region) : templates;
}

export function addTemplate(t: Omit<PrescriptionTemplate, "id">) {
  const row: PrescriptionTemplate = { ...t, id: `TPL-${Date.now()}` };
  templates = [row, ...templates];
  return row;
}

export function updateTemplate(id: string, payload: Partial<PrescriptionTemplate>) {
  templates = templates.map((t) => (t.id === id ? { ...t, ...payload } : t));
}

export function deleteTemplate(id: string) {
  templates = templates.filter((t) => t.id !== id);
}


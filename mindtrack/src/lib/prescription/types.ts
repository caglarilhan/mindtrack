export type PrescriptionStatus = 'draft' | 'active' | 'voided' | 'expired';
export type PrescriptionRisk = 'low' | 'medium' | 'high' | 'critical';
export type RegionId = 'TR' | 'US' | 'EU';

export interface PrescriptionMedication {
  name: string;
  doseMg?: number;
  frequency?: string;
}

export interface Prescription {
  id: string;
  patientName: string;
  patientId: string;
  region: RegionId;
  medications: PrescriptionMedication[];
  status: PrescriptionStatus;
  risk: PrescriptionRisk;
  createdAt: string;
  pharmacyName?: string;
  notes?: string;
  controlledSchedule?: 'II' | 'III' | 'IV';
}

export interface Patient {
  id: string;
  name: string;
  allergies: string[];
}



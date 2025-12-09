export type ERxStatus = "pending" | "sent" | "failed";

export interface EPrescriptionRecord {
  id: string;
  prescriptionId: string;
  status: ERxStatus;
  createdAt: string;
  updatedAt: string;
  pharmacyResponseCode?: string;
  pharmacyResponseMessage?: string;
}



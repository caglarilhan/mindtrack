import { EPrescriptionRecord } from "./erx-types";
import { addAuditEntry } from "./audit-log";

let store: EPrescriptionRecord[] = [];

export function createPendingERx(prescriptionId: string): EPrescriptionRecord {
  const rec: EPrescriptionRecord = {
    id: `ERX-${Date.now()}`,
    prescriptionId,
    status: "pending",
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  };
  store = [rec, ...store];
  return rec;
}

export function markERxSent(id: string) {
  const rec = store.find((r) => r.id === id);
  store = store.map((r) => (r.id === id ? { ...r, status: "sent", updatedAt: new Date().toISOString() } : r));
  if (rec) {
    addAuditEntry({
      userId: "system",
      eventType: "ERX_SENT",
      prescriptionId: rec.prescriptionId,
      details: "E-Reçete gönderildi (mock, store)",
    });
  }
}

export function markERxFailed(id: string, code?: string, message?: string) {
  const rec = store.find((r) => r.id === id);
  store = store.map((r) =>
    r.id === id
      ? {
          ...r,
          status: "failed",
          updatedAt: new Date().toISOString(),
          pharmacyResponseCode: code,
          pharmacyResponseMessage: message,
        }
      : r
  );
  if (rec) {
    addAuditEntry({
      userId: "system",
      eventType: "ERX_FAILED",
      prescriptionId: rec.prescriptionId,
      details: `E-Reçete hatası (mock, store): ${code || ""} ${message || ""}`.trim(),
    });
  }
}

export function getERxRecords() {
  return store;
}



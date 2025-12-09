import { EPrescriptionRecord } from "./erx-types";

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
  store = store.map((r) => (r.id === id ? { ...r, status: "sent", updatedAt: new Date().toISOString() } : r));
}

export function markERxFailed(id: string, code?: string, message?: string) {
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
}

export function getERxRecords() {
  return store;
}



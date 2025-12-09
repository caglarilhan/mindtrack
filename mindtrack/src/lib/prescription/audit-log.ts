export type AuditEventType =
  | "PRESCRIPTION_CREATED"
  | "PRESCRIPTION_VOIDED"
  | "ERX_SENT"
  | "ERX_FAILED"
  | "ERX_RETRY"
  | "SAFETY_OVERRIDE";

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  userId: string;
  eventType: AuditEventType;
  prescriptionId?: string;
  details: string;
}

let auditStore: AuditLogEntry[] = [];

export function addAuditEntry(entry: Omit<AuditLogEntry, "id" | "timestamp">) {
  const row: AuditLogEntry = {
    id: `AUD-${Date.now()}`,
    timestamp: new Date().toISOString(),
    ...entry,
  };
  auditStore = [row, ...auditStore];
  return row;
}

export function getAuditLogs() {
  return auditStore;
}



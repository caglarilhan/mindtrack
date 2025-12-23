import { createSupabaseServerClient } from '@/lib/supabaseClient';

export type AuditAction =
  | 'telehealth.link.create'
  | 'telehealth.reminder.send'
  | 'patient.preferences.read'
  | 'patient.preferences.write'
  | 'patient.anamnesis.read'
  | 'patient.anamnesis.write'
  | 'patient.anamnesis.decrypt.user'
  | 'patient.anamnesis.decrypt.admin';

export interface AuditEntry {
  action: AuditAction;
  userId?: string | null;
  patientId?: string | null;
  appointmentId?: string | null;
  ip?: string | null;
  userAgent?: string | null;
  context?: Record<string, any>;
}

export async function writeAudit(entry: AuditEntry) {
  const supabase = await createSupabaseServerClient();
  const { data: { user } } = await supabase.auth.getUser();
  const payload = {
    action: entry.action,
    user_id: user?.id || null,
    patient_id: entry.patientId || null,
    appointment_id: entry.appointmentId || null,
    ip: entry.ip || null,
    user_agent: entry.userAgent || null,
    context: entry.context || {},
    created_at: new Date().toISOString()
  };
  // audit_logs tablosu yoksa sessiz geçer; migration ile eklenecek
  try {
    await supabase.from('audit_logs').insert(payload);
  } catch (_) {
    // no-op
  }
}




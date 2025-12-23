import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabaseClient';
import { selectForPatientAndAppointment } from '@/lib/notifications/autoSelect';
import { enqueueDelivery } from '@/lib/queue';

// Basit cron: X dakika sonra başlayacak randevular için otomatik hatırlatma
export async function POST(request: NextRequest) {
  try {
    const supabase = await createSupabaseServerClient();
    const { data: { user } } = await supabase.auth.getUser();
    // Opsiyonel: sadece yetkili kullanıcılar tetikleyebilir; yoksa public cron da olabilir
    if (!user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const { windowMinutes = 60 } = await request.json().catch(() => ({ windowMinutes: 60 }));

    const now = new Date();
    const upper = new Date(now.getTime() + windowMinutes * 60 * 1000);
    const nowIso = now.toISOString();
    const upperIso = upper.toISOString();

    // appointments: id, patient_id, start_at, telehealth_link
    // appointment_settings: appointment_id, settings(autoReminderMinutes)
    let appts: any[] = [];
    try {
      const { data } = await supabase
        .from('appointments')
        .select('id, patient_id, start_at, telehealth_link')
        .gte('start_at', nowIso)
        .lte('start_at', upperIso);
      appts = data || [];
    } catch (_) {
      appts = [];
    }

    // Load appointment_settings into a map
    const apptIds = appts.map(a => a.id);
    let settingsMap = new Map<string, any>();
    if (apptIds.length > 0) {
      try {
        const { data: settingRows } = await supabase
          .from('appointment_settings')
          .select('appointment_id, settings')
          .in('appointment_id', apptIds);
        (settingRows || []).forEach((r: any) => settingsMap.set(r.appointment_id, r.settings));
      } catch (_) {
        // ignore
      }
    }

    const tasks: Promise<any>[] = [];
    for (const appt of appts) {
      const s = settingsMap.get(appt.id) || {};
      const autoReminder = typeof s.autoReminderMinutes === 'number' ? s.autoReminderMinutes : 60;
      const minutesToStart = Math.floor((new Date(appt.start_at).getTime() - now.getTime()) / 60000);
      if (minutesToStart < 0 || minutesToStart > windowMinutes) continue;

      // Auto select providers and recipients by patient/clinic settings
      try {
        const sel = await selectForPatientAndAppointment(appt.patient_id, appt.id);
        const link = appt.telehealth_link || '';
        if (sel.email?.to) {
          tasks.push(enqueueDelivery({ channel: 'email', payload: { to: sel.email.to, subject: sel.email.subject, body: (sel.email.text || '').replace('{{link}}', link) } }));
        }
        if (sel.sms?.to) {
          tasks.push(enqueueDelivery({ channel: 'sms', payload: { to: sel.sms.to, body: (sel.sms.body || '').replace('{{link}}', link), provider: sel.sms.provider } }));
        }
      } catch (e) {
        // skip faulty
      }
    }

    await Promise.allSettled(tasks);
    return NextResponse.json({ success: true, windowMinutes, processed: appts.length });
  } catch (error) {
    console.error('cron/reminders error', error);
    return NextResponse.json({ error: 'Failed to run reminders cron' }, { status: 500 });
  }
}



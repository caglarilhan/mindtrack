import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabaseClient';
import { requirePermission } from '@/lib/rbac';
import { writeAudit } from '@/lib/audit';

type EmailProvider = 'sendgrid' | 'postmark' | 'ses' | 'brevo' | 'mailjet' | 'mailgun_eu';
type SmsProvider = 'twilio' | 'messagebird' | 'vonage' | 'sinch';
type DataRegion = 'us' | 'eu';

interface CommunicationsSettings {
  emailProvider: EmailProvider;
  smsProvider: SmsProvider;
  dataRegion: DataRegion;
  defaultReminderOffsetMinutes: number;
  templates: {
    emailSubject: string;
    emailBody: string;
    smsBody: string;
  };
}

const DEFAULT_SETTINGS: CommunicationsSettings = {
  emailProvider: 'sendgrid',
  smsProvider: 'twilio',
  dataRegion: 'us',
  defaultReminderOffsetMinutes: 60,
  templates: {
    emailSubject: 'Telehealth Session Reminder',
    emailBody: 'Your session is scheduled soon. Join using the link: {{link}}',
    smsBody: 'Your session is scheduled soon. Join: {{link}}'
  }
};

async function getClinicIdForUser() {
  const supabase = await createSupabaseServerClient();
  const { data: { user }, error: authError } = await supabase.auth.getUser();
  if (authError || !user) return { error: 'Unauthorized', status: 401 } as const;
  const { data: clinicMember, error } = await supabase
    .from('clinic_members')
    .select('clinic_id')
    .eq('user_id', user.id)
    .eq('status', 'active')
    .single();
  if (error || !clinicMember) return { error: 'No active clinic membership', status: 403 } as const;
  return { clinicId: clinicMember.clinic_id } as const;
}

export async function GET() {
  try {
    await requirePermission('settings:communications:read');
    const supabase = await createSupabaseServerClient();
    const ctx = await getClinicIdForUser();
    if ('error' in ctx) return NextResponse.json({ error: ctx.error }, { status: ctx.status });
    const { clinicId } = ctx;

    const { data, error } = await supabase
      .from('clinic_settings')
      .select('value')
      .eq('clinic_id', clinicId)
      .eq('key', 'communications')
      .single();

    if (error || !data) {
      // Tablo yoksa veya kayıt yoksa varsayılanı dön
      return NextResponse.json({ settings: DEFAULT_SETTINGS, exists: false });
    }

    return NextResponse.json({ settings: data.value as CommunicationsSettings, exists: true });
  } catch (error) {
    console.error('GET /settings/communications error', error);
    return NextResponse.json({ error: 'Failed to fetch settings' }, { status: 500 });
  }
}

export async function PUT(request: NextRequest) {
  try {
    await requirePermission('settings:communications:write');
    const supabase = await createSupabaseServerClient();
    const ctx = await getClinicIdForUser();
    if ('error' in ctx) return NextResponse.json({ error: ctx.error }, { status: ctx.status });
    const { clinicId } = ctx;

    const body = await request.json();
    const incoming = body?.settings as Partial<CommunicationsSettings>;
    if (!incoming) return NextResponse.json({ error: 'Invalid payload' }, { status: 400 });

    const nextSettings: CommunicationsSettings = {
      ...DEFAULT_SETTINGS,
      ...incoming,
      templates: { ...DEFAULT_SETTINGS.templates, ...(incoming.templates || {}) }
    };

    const { error } = await supabase
      .from('clinic_settings')
      .upsert({ clinic_id: clinicId, key: 'communications', value: nextSettings }, { onConflict: 'clinic_id,key' });

    if (error) {
      // Örn. tablo yoksa ayrıntı düşer
      console.error('Upsert clinic_settings error', error);
      return NextResponse.json({ error: 'Failed to save settings' }, { status: 500 });
    }

    await writeAudit({ action: 'patient.preferences.write', ip: request.ip, userAgent: request.headers.get('user-agent'), context: { section: 'settings.communications' } });
    return NextResponse.json({ success: true, settings: nextSettings });
  } catch (error) {
    console.error('PUT /settings/communications error', error);
    return NextResponse.json({ error: 'Failed to save settings' }, { status: 500 });
  }
}





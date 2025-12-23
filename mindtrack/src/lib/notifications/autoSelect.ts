import { createSupabaseServerClient } from '@/lib/supabaseClient';

type EmailProvider = 'sendgrid' | 'postmark' | 'ses' | 'brevo' | 'mailjet' | 'mailgun_eu';
type SmsProvider = 'twilio' | 'messagebird' | 'vonage' | 'sinch';
type DataRegion = 'us' | 'eu';

export interface AutoSelection {
  language: string;
  email?: { provider: EmailProvider; to: string; subject: string; html?: string; text?: string };
  sms?: { provider: SmsProvider; to: string; body: string };
}

export async function selectForPatientAndAppointment(patientId: string, appointmentId?: string): Promise<AutoSelection> {
  const supabase = await createSupabaseServerClient();

  // Klinik ayarları
  const { data: { user } } = await supabase.auth.getUser();
  let clinicId: string | null = null;
  if (user) {
    const { data: member } = await supabase
      .from('clinic_members')
      .select('clinic_id')
      .eq('user_id', user.id)
      .eq('status', 'active')
      .single();
    clinicId = member?.clinic_id || null;
  }

  let settings: any = null;
  if (clinicId) {
    const { data: setting } = await supabase
      .from('clinic_settings')
      .select('value')
      .eq('clinic_id', clinicId)
      .eq('key', 'communications')
      .single();
    settings = setting?.value || null;
  }

  // Hasta tercihleri
  const { data: prefRow } = await supabase
    .from('patient_preferences')
    .select('preferences')
    .eq('patient_id', patientId)
    .single();
  const prefs = prefRow?.preferences || {};

  const language = prefs.preferredLanguage || settings?.language || 'tr';
  const contactPreference = prefs.contactPreference || 'email';

  // Alıcı bilgileri
  const emailTo = prefs.email || process.env.TEST_EMAIL || '';
  const phoneTo = prefs.phone || process.env.TEST_PHONE || '';

  // Sağlayıcı seçimi (bölgeye göre)
  const region: DataRegion = settings?.dataRegion || 'us';
  const smsProvider: SmsProvider = prefs.smsProvider || settings?.smsProvider || (region === 'eu' ? 'messagebird' : 'twilio');
  const emailProvider: EmailProvider = prefs.emailProvider || settings?.emailProvider || (region === 'eu' ? 'brevo' : 'sendgrid');

  // Şablonlar
  const subjectTpl = settings?.templates?.emailSubject || 'Tele‑seans Hatırlatma';
  const emailTpl = settings?.templates?.emailBody || 'Seansınız yakında başlayacaktır. Bağlantı: {{link}}';
  const smsTpl = settings?.templates?.smsBody || 'Seansınız yakında başlayacaktır. Bağlantı: {{link}}';

  return {
    language,
    email: contactPreference !== 'sms' && emailTo ? { provider: emailProvider, to: emailTo, subject: subjectTpl } : undefined,
    sms: contactPreference !== 'email' && phoneTo ? { provider: smsProvider, to: phoneTo, body: smsTpl } : undefined,
  };
}



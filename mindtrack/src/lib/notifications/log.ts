import { createSupabaseServerClient } from '@/lib/supabaseClient';

export async function logDelivery(entry: {
  channel: 'email' | 'sms';
  provider: string;
  to: string;
  subject?: string;
  body?: string;
  status: 'sent' | 'failed';
  error?: string;
  context?: Record<string, any>;
}) {
  try {
    const supabase = await createSupabaseServerClient();
    await supabase.from('delivery_logs').insert({
      channel: entry.channel,
      provider: entry.provider,
      to_address: entry.to,
      subject: entry.subject || null,
      body: entry.body || null,
      status: entry.status,
      error: entry.error || null,
      context: entry.context || {}
    });
  } catch (_) {
    // no-op
  }
}





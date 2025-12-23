import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabaseClient';

interface AppointmentSettings {
  telehealthProvider?: 'custom' | 'google_meet' | 'zoom';
  telehealthLink?: string;
  autoReminderMinutes?: number; // send automatically before session
}

export async function GET(
  _req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const supabase = await createSupabaseServerClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const appointmentId = params.id;
    const { data, error } = await supabase
      .from('appointment_settings')
      .select('*')
      .eq('appointment_id', appointmentId)
      .single();
    if (error && error.code !== 'PGRST116') throw error;
    return NextResponse.json({ settings: (data?.settings || {}) as AppointmentSettings, exists: !!data });
  } catch (error) {
    console.error('GET appointment settings error', error);
    return NextResponse.json({ error: 'Failed to fetch settings' }, { status: 500 });
  }
}

export async function PUT(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const supabase = await createSupabaseServerClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const appointmentId = params.id;
    const body = await req.json();
    const settings = (body?.settings || {}) as AppointmentSettings;

    const { error } = await supabase
      .from('appointment_settings')
      .upsert({ appointment_id: appointmentId, settings }, { onConflict: 'appointment_id' });
    if (error) throw error;
    return NextResponse.json({ success: true, settings });
  } catch (error) {
    console.error('PUT appointment settings error', error);
    return NextResponse.json({ error: 'Failed to save settings' }, { status: 500 });
  }
}






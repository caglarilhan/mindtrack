import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabaseClient';

interface PatientPreferences {
  preferredLanguage?: string; // 'en' | 'de' | 'es' | 'tr' | ...
  timeZone?: string; // e.g. 'Europe/Berlin'
  contactPreference?: 'email' | 'sms' | 'none';
  email?: string;
  phone?: string;
  consentMarketing?: boolean;
  consentReminders?: boolean;
}

export async function GET(
  _req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const supabase = await createSupabaseServerClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const patientId = params.id;
    const { data, error } = await supabase
      .from('patient_preferences')
      .select('*')
      .eq('patient_id', patientId)
      .single();
    if (error && error.code !== 'PGRST116') throw error;
    return NextResponse.json({ preferences: (data?.preferences || {}) as PatientPreferences, exists: !!data });
  } catch (error) {
    console.error('GET patient preferences error', error);
    return NextResponse.json({ error: 'Failed to fetch preferences' }, { status: 500 });
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

    const patientId = params.id;
    const body = await req.json();
    const preferences = (body?.preferences || {}) as PatientPreferences;

    const { error } = await supabase
      .from('patient_preferences')
      .upsert({ patient_id: patientId, preferences }, { onConflict: 'patient_id' });
    if (error) throw error;
    return NextResponse.json({ success: true, preferences });
  } catch (error) {
    console.error('PUT patient preferences error', error);
    return NextResponse.json({ error: 'Failed to save preferences' }, { status: 500 });
  }
}






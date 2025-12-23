import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabaseClient';
import { requirePermission } from '@/lib/rbac';

export async function POST(request: NextRequest) {
  try {
    await requirePermission('appointments:write');
    const { patientId, startAt, type, location, recurrence, telehealthLink } = await request.json();
    if (!patientId || !startAt) return NextResponse.json({ error: 'patientId and startAt required' }, { status: 400 });
    const supabase = await createSupabaseServerClient();
    const { data, error } = await supabase
      .from('appointments')
      .insert({ patient_id: patientId, start_at: startAt, type: type || 'consult', location: location || null, recurrence: recurrence || null, telehealth_link: telehealthLink || null })
      .select('id')
      .single();
    if (error) throw error;
    return NextResponse.json({ success: true, id: data.id });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'failed' }, { status: 500 });
  }
}





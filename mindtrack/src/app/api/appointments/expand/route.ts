import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabaseClient';
import { requirePermission } from '@/lib/rbac';

function addDays(date: Date, days: number) { const d = new Date(date); d.setDate(d.getDate() + days); return d; }
function addWeeks(date: Date, weeks: number) { return addDays(date, weeks * 7); }

export async function POST(request: NextRequest) {
  try {
    await requirePermission('appointments:write');
    const { baseId, freq, count } = await request.json();
    if (!baseId || !freq || !count) return NextResponse.json({ error: 'baseId, freq, count required' }, { status: 400 });
    const supabase = await createSupabaseServerClient();
    const { data: base, error } = await supabase
      .from('appointments')
      .select('*')
      .eq('id', baseId)
      .single();
    if (error || !base) return NextResponse.json({ error: 'base appointment not found' }, { status: 404 });

    const created: string[] = [];
    let last = new Date(base.start_at);
    for (let i = 1; i <= count; i++) {
      if (freq === 'WEEKLY') last = addWeeks(last, 1);
      else if (freq === 'DAILY') last = addDays(last, 1);
      else return NextResponse.json({ error: 'unsupported freq' }, { status: 400 });
      const { data: ins, error: insErr } = await supabase
        .from('appointments')
        .insert({ patient_id: base.patient_id, start_at: last.toISOString(), type: base.type, location: base.location, status: 'scheduled', telehealth_link: base.telehealth_link })
        .select('id')
        .single();
      if (!insErr && ins?.id) created.push(ins.id);
    }
    return NextResponse.json({ success: true, created });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'failed' }, { status: 500 });
  }
}





import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabaseClient';
import { requirePermission } from '@/lib/rbac';
import { writeAudit } from '@/lib/audit';

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    await requirePermission('appointments:write');
    const { id } = params;
    
    if (!id) {
      return NextResponse.json({ error: 'Appointment ID required' }, { status: 400 });
    }

    const supabase = await createSupabaseServerClient();
    
    // Randevuyu onayla
    const { error } = await supabase
      .from('appointments')
      .update({ status: 'confirmed' })
      .eq('id', id);

    if (error) {
      throw error;
    }

    // Audit log
    await writeAudit({
      action: 'appointment.confirm',
      details: { appointmentId: id },
      userId: 'system' // Hasta tarafından yapıldığı için system olarak işaretle
    });

    return NextResponse.json({ success: true, status: 'confirmed' });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'Failed to confirm appointment' }, { status: 500 });
  }
}



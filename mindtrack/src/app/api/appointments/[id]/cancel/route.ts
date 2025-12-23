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
    
    // Randevuyu iptal et
    const { error } = await supabase
      .from('appointments')
      .update({ status: 'cancelled' })
      .eq('id', id);

    if (error) {
      throw error;
    }

    // Audit log
    await writeAudit({
      action: 'appointment.cancel',
      details: { appointmentId: id },
      userId: 'system' // Hasta tarafından yapıldığı için system olarak işaretle
    });

    return NextResponse.json({ success: true, status: 'cancelled' });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'Failed to cancel appointment' }, { status: 500 });
  }
}



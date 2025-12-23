import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabaseClient';
import { requirePermission } from '@/lib/rbac';
import { writeAudit } from '@/lib/audit';

export async function GET(request: NextRequest) {
  try {
    await requirePermission('patient:messages:read');
    
    const { searchParams } = new URL(request.url);
    const patientId = searchParams.get('patientId');
    
    if (!patientId) {
      return NextResponse.json({ error: 'Patient ID required' }, { status: 400 });
    }

    const supabase = await createSupabaseServerClient();
    
    // Hasta mesajlarını getir
    const { data, error } = await supabase
      .from('patient_messages')
      .select(`
        *,
        sender:clinic_members!patient_messages_sender_id_fkey(user_id, role)
      `)
      .eq('patient_id', patientId)
      .order('created_at', { ascending: false })
      .limit(50);

    if (error) {
      throw error;
    }

    return NextResponse.json({ messages: data || [] });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'Failed to fetch messages' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    await requirePermission('patient:messages:write');
    
    const { patientId, content, messageType = 'text', attachments } = await request.json();
    
    if (!patientId || !content) {
      return NextResponse.json({ error: 'Patient ID and content are required' }, { status: 400 });
    }

    const supabase = await createSupabaseServerClient();
    
    // Mesajı kaydet
    const { data, error } = await supabase
      .from('patient_messages')
      .insert({
        patient_id: patientId,
        content,
        message_type: messageType,
        attachments: attachments || null,
        is_read: false,
        sender_id: 'system' // Şimdilik system olarak işaretle, auth.uid() ile değiştirilecek
      })
      .select('id')
      .single();

    if (error) {
      throw error;
    }

    // Audit log
    await writeAudit({
      action: 'patient.message.send',
      details: { messageId: data.id, patientId, messageType },
      userId: 'system'
    });

    return NextResponse.json({ success: true, messageId: data.id });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'Failed to send message' }, { status: 500 });
  }
}



import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/utils/supabase/server';

export async function GET(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '20');
    const offset = parseInt(searchParams.get('offset') || '0');
    const unreadOnly = searchParams.get('unreadOnly') === 'true';

    // Get patient profile
    const { data: patient, error: patientError } = await supabase
      .from('patients')
      .select('id')
      .eq('user_id', user.id)
      .single();

    if (patientError || !patient) {
      return NextResponse.json({ error: 'Patient profile not found' }, { status: 404 });
    }

    // Fetch messages (patient_messages table)
    let query = supabase
      .from('patient_messages')
      .select(`
        id,
        patient_id,
        sender_id,
        message,
        is_read,
        created_at,
        user_profiles!sender_id(full_name, role)
      `)
      .eq('patient_id', patient.id)
      .order('created_at', { ascending: false })
      .range(offset, offset + limit - 1);

    if (unreadOnly) {
      query = query.eq('is_read', false);
    }

    const { data: messages, error: messagesError } = await query;

    if (messagesError) {
      // Table may not exist
      return NextResponse.json({ 
        messages: [],
        unreadCount: 0,
        pagination: { limit, offset, hasMore: false }
      });
    }

    // Count unread messages
    const { count: unreadCount } = await supabase
      .from('patient_messages')
      .select('*', { count: 'exact', head: true })
      .eq('patient_id', patient.id)
      .eq('is_read', false);

    return NextResponse.json({
      messages: messages || [],
      unreadCount: unreadCount || 0,
      pagination: {
        limit,
        offset,
        hasMore: (messages?.length || 0) === limit
      }
    });
  } catch (error) {
    console.error('Error fetching messages:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { message, recipientId, isCrisis } = await request.json();

    if (!message || !recipientId) {
      return NextResponse.json({ error: 'message and recipientId required' }, { status: 400 });
    }

    // Get patient profile
    const { data: patient, error: patientError } = await supabase
      .from('patients')
      .select('id')
      .eq('user_id', user.id)
      .single();

    if (patientError || !patient) {
      return NextResponse.json({ error: 'Patient profile not found' }, { status: 404 });
    }

    // Create message
    const { data: newMessage, error: insertError } = await supabase
      .from('patient_messages')
      .insert({
        patient_id: patient.id,
        sender_id: user.id,
        recipient_id: recipientId,
        message,
        is_crisis: isCrisis || false,
        is_read: false,
        created_at: new Date().toISOString()
      })
      .select()
      .single();

    if (insertError) {
      console.error('Error creating message:', insertError);
      return NextResponse.json({ error: 'Failed to send message' }, { status: 500 });
    }

    // If crisis message, trigger notification
    if (isCrisis) {
      // TODO: Send urgent notification to therapist
      // await notifyTherapistCrisis(recipientId, patient.id, message);
    }

    return NextResponse.json({
      success: true,
      message: newMessage
    });
  } catch (error) {
    console.error('Error sending message:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { messageId, isRead } = await request.json();

    if (!messageId || isRead === undefined) {
      return NextResponse.json({ error: 'messageId and isRead required' }, { status: 400 });
    }

    // Get patient profile
    const { data: patient, error: patientError } = await supabase
      .from('patients')
      .select('id')
      .eq('user_id', user.id)
      .single();

    if (patientError || !patient) {
      return NextResponse.json({ error: 'Patient profile not found' }, { status: 404 });
    }

    // Update message read status
    const { data: updatedMessage, error: updateError } = await supabase
      .from('patient_messages')
      .update({ is_read: isRead, read_at: isRead ? new Date().toISOString() : null })
      .eq('id', messageId)
      .eq('patient_id', patient.id)
      .select()
      .single();

    if (updateError) {
      console.error('Error updating message:', updateError);
      return NextResponse.json({ error: 'Failed to update message' }, { status: 500 });
    }

    return NextResponse.json({
      success: true,
      message: updatedMessage
    });
  } catch (error) {
    console.error('Error updating message:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}











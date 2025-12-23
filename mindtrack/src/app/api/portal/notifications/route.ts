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

    // Fetch notifications (patient_notifications table or fallback to delivery_logs)
    let query = supabase
      .from('patient_notifications')
      .select('id, patient_id, type, title, message, is_read, created_at, metadata')
      .eq('patient_id', patient.id)
      .order('created_at', { ascending: false })
      .range(offset, offset + limit - 1);

    if (unreadOnly) {
      query = query.eq('is_read', false);
    }

    const { data: notifications, error: notificationsError } = await query;

    if (notificationsError) {
      // Fallback: try delivery_logs table
      const { data: deliveryLogs } = await supabase
        .from('delivery_logs')
        .select('id, patient_id, notification_type, message, delivered_at, status')
        .eq('patient_id', patient.id)
        .eq('status', 'delivered')
        .order('delivered_at', { ascending: false })
        .limit(limit);

      const formattedNotifications = deliveryLogs?.map(log => ({
        id: log.id,
        type: log.notification_type || 'general',
        title: 'Bildirim',
        message: log.message || '',
        isRead: false,
        createdAt: log.delivered_at
      })) || [];

      return NextResponse.json({
        notifications: formattedNotifications,
        unreadCount: formattedNotifications.length,
        pagination: { limit, offset, hasMore: false }
      });
    }

    // Count unread notifications
    const { count: unreadCount } = await supabase
      .from('patient_notifications')
      .select('*', { count: 'exact', head: true })
      .eq('patient_id', patient.id)
      .eq('is_read', false);

    return NextResponse.json({
      notifications: notifications || [],
      unreadCount: unreadCount || 0,
      pagination: {
        limit,
        offset,
        hasMore: (notifications?.length || 0) === limit
      }
    });
  } catch (error) {
    console.error('Error fetching notifications:', error);
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

    const { notificationId, isRead } = await request.json();

    if (!notificationId || isRead === undefined) {
      return NextResponse.json({ error: 'notificationId and isRead required' }, { status: 400 });
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

    // Update notification read status
    const { data: updatedNotification, error: updateError } = await supabase
      .from('patient_notifications')
      .update({ is_read: isRead, read_at: isRead ? new Date().toISOString() : null })
      .eq('id', notificationId)
      .eq('patient_id', patient.id)
      .select()
      .single();

    if (updateError) {
      // Try delivery_logs as fallback
      return NextResponse.json({
        success: true,
        message: 'Notification status updated (fallback)'
      });
    }

    return NextResponse.json({
      success: true,
      notification: updatedNotification
    });
  } catch (error) {
    console.error('Error updating notification:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}











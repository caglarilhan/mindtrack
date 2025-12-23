import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/utils/supabase/server';

export async function GET(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    // Get patient profile
    const { data: patient, error: patientError } = await supabase
      .from('patients')
      .select('id, mode, first_name, last_name, pseudo_name, email, phone, user_id')
      .eq('user_id', user.id)
      .single();

    if (patientError || !patient) {
      return NextResponse.json({ error: 'Patient profile not found' }, { status: 404 });
    }

    const patientId = patient.id;
    const mode = patient.mode || 'full';

    // Get next appointment
    const { data: nextAppointment } = await supabase
      .from('appointments')
      .select('id, start_at, type, status, location, telehealth_link, provider_id, user_profiles!inner(full_name, role)')
      .eq('patient_id', patientId)
      .gte('start_at', new Date().toISOString())
      .order('start_at', { ascending: true })
      .limit(1)
      .maybeSingle();

    // Get recent appointments (last 3)
    const { data: recentAppointments } = await supabase
      .from('appointments')
      .select('id, start_at, type, status, location')
      .eq('patient_id', patientId)
      .order('start_at', { ascending: false })
      .limit(3);

    // Get upcoming appointments (next 3)
    const { data: upcomingAppointments } = await supabase
      .from('appointments')
      .select('id, start_at, type, status, location, telehealth_link')
      .eq('patient_id', patientId)
      .gte('start_at', new Date().toISOString())
      .order('start_at', { ascending: true })
      .limit(3);

    // Get active assignments
    const { data: assignments } = await supabase
      .from('treatment_plans')
      .select('id, goals, interventions, progress_notes')
      .eq('patient_id', patientId)
      .order('created_at', { ascending: false })
      .limit(1)
      .maybeSingle();

    // Get pending forms
    const { data: pendingForms } = await supabase
      .from('assessments')
      .select('id, type, created_at')
      .eq('client_id', patientId)
      .is('completed_at', null)
      .order('created_at', { ascending: false })
      .limit(5);

    // Get recent assessments (for scores)
    const { data: recentAssessments } = await supabase
      .from('assessments')
      .select('id, type, score, max_score, severity, created_at')
      .eq('client_id', patientId)
      .not('score', 'is', null)
      .order('created_at', { ascending: false })
      .limit(3);

    // Get unread messages count
    const { count: unreadMessagesCount } = await supabase
      .from('patient_messages')
      .select('*', { count: 'exact', head: true })
      .eq('patient_id', patientId)
      .eq('is_read', false)
      .catch(() => ({ count: 0 }));

    // Get recent notifications
    const { data: notifications } = await supabase
      .from('patient_notifications')
      .select('id, type, title, message, is_read, created_at')
      .eq('patient_id', patientId)
      .order('created_at', { ascending: false })
      .limit(5)
      .catch(() => ({ data: [] }));

    // Format response based on mode
    const displayName = mode === 'full' 
      ? `${patient.first_name} ${patient.last_name}`
      : patient.pseudo_name || `Client #${patientId.slice(0, 8)}`;

    return NextResponse.json({
      patient: {
        id: patient.id,
        mode,
        displayName,
        email: mode === 'full' ? patient.email : null,
        phone: mode === 'full' ? patient.phone : null
      },
      nextAppointment: nextAppointment ? {
        id: nextAppointment.id,
        date: nextAppointment.start_at,
        type: nextAppointment.type,
        status: nextAppointment.status,
        location: nextAppointment.location,
        telehealthLink: nextAppointment.telehealth_link,
        providerName: nextAppointment.user_profiles?.full_name,
        providerRole: nextAppointment.user_profiles?.role
      } : null,
      appointments: {
        recent: recentAppointments || [],
        upcoming: upcomingAppointments || []
      },
      assignments: assignments ? {
        goals: assignments.goals || [],
        interventions: assignments.interventions || []
      } : null,
      forms: {
        pending: pendingForms || [],
        recent: recentAssessments || []
      },
      messages: {
        unreadCount: unreadMessagesCount
      },
      notifications
    });
  } catch (error) {
    console.error('Error in portal dashboard API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}


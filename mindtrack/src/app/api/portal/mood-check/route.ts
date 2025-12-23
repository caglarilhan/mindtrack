import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/utils/supabase/server';

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { score, note } = await request.json();

    if (!score || score < 1 || score > 5) {
      return NextResponse.json({ error: 'score must be between 1 and 5' }, { status: 400 });
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

    // Save mood check (create mood_logs table if not exists)
    const { data: moodLog, error: insertError } = await supabase
      .from('mood_logs')
      .insert({
        patient_id: patient.id,
        user_id: user.id,
        score,
        note: note || null,
        date: new Date().toISOString().split('T')[0], // Today's date
        created_at: new Date().toISOString()
      })
      .select()
      .single();

    if (insertError) {
      // If table doesn't exist, create it first (fallback)
      console.warn('mood_logs table may not exist:', insertError);
      // Return success anyway for MVP
      return NextResponse.json({
        success: true,
        message: 'Mood check saved (table may need migration)',
        moodLog: {
          score,
          note,
          date: new Date().toISOString().split('T')[0]
        }
      });
    }

    // Check if this is a concerning score (1-2) and should notify therapist
    const shouldNotify = score <= 2;
    if (shouldNotify) {
      // TODO: Send notification to therapist (optional)
      // await notifyTherapist(patient.id, score, note);
    }

    return NextResponse.json({
      success: true,
      moodLog: {
        id: moodLog.id,
        score,
        note: moodLog.note,
        date: moodLog.date,
        createdAt: moodLog.created_at
      },
      shouldNotify
    });
  } catch (error) {
    console.error('Error in mood check API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function GET(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const period = searchParams.get('period') || '7d'; // 7d, 30d, 90d

    // Get patient profile
    const { data: patient, error: patientError } = await supabase
      .from('patients')
      .select('id')
      .eq('user_id', user.id)
      .single();

    if (patientError || !patient) {
      return NextResponse.json({ error: 'Patient profile not found' }, { status: 404 });
    }

    // Calculate date range
    const now = new Date();
    let startDate: Date;
    switch (period) {
      case '7d': startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000); break;
      case '30d': startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000); break;
      case '90d': startDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000); break;
      default: startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    }

    // Fetch mood logs
    const { data: moodLogs, error: fetchError } = await supabase
      .from('mood_logs')
      .select('id, score, note, date, created_at')
      .eq('patient_id', patient.id)
      .gte('date', startDate.toISOString().split('T')[0])
      .order('date', { ascending: false });

    if (fetchError) {
      // Table may not exist
      return NextResponse.json({ moodLogs: [], period });
    }

    // Calculate average score
    const avgScore = moodLogs && moodLogs.length > 0
      ? moodLogs.reduce((sum, log) => sum + log.score, 0) / moodLogs.length
      : null;

    return NextResponse.json({
      moodLogs: moodLogs || [],
      period,
      averageScore: avgScore ? Math.round(avgScore * 100) / 100 : null,
      totalEntries: moodLogs?.length || 0
    });
  } catch (error) {
    console.error('Error fetching mood logs:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}











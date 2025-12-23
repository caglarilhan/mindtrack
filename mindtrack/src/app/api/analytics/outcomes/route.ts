import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabaseClient';
import { requirePermission } from '@/lib/rbac';

export async function GET(request: NextRequest) {
  try {
    await requirePermission('analytics:patients:read');
    
    const { searchParams } = new URL(request.url);
    const patientId = searchParams.get('patientId');
    const period = searchParams.get('period') || '90d';
    const clinicId = searchParams.get('clinicId');
    
    const supabase = await createSupabaseServerClient();
    
    // Period calculation
    const now = new Date();
    let startDate: Date;
    switch (period) {
      case '30d': startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000); break;
      case '90d': startDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000); break;
      case '180d': startDate = new Date(now.getTime() - 180 * 24 * 60 * 60 * 1000); break;
      case '1y': startDate = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000); break;
      default: startDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000);
    }

    // Fetch assessments and appointments for outcome tracking
    let query = supabase
      .from('assessments')
      .select('id, client_id, type, score, max_score, severity, created_at')
      .gte('created_at', startDate.toISOString())
      .order('created_at', { ascending: true });

    if (patientId) {
      query = query.eq('client_id', patientId);
    }

    const { data: assessments, error: assessError } = await query;
    if (assessError) throw assessError;

    // Fetch appointments for completion rate
    let apptQuery = supabase
      .from('appointments')
      .select('id, patient_id, status, start_at, created_at')
      .gte('created_at', startDate.toISOString());

    if (patientId) {
      apptQuery = apptQuery.eq('patient_id', patientId);
    }

    const { data: appointments, error: apptError } = await apptQuery;
    if (apptError) throw apptError;

    // Calculate outcome metrics
    const totalAssessments = assessments?.length || 0;
    const completedAppointments = appointments?.filter(a => a.status === 'completed').length || 0;
    const totalAppointments = appointments?.length || 0;
    const completionRate = totalAppointments > 0 ? (completedAppointments / totalAppointments) * 100 : 0;

    // Score trends (for assessments with scores)
    const scoreTrends = (assessments || [])
      .filter(a => a.score !== null && a.max_score !== null)
      .map(a => ({
        date: a.created_at.split('T')[0],
        score: a.score,
        maxScore: a.max_score,
        percentage: ((a.score / a.max_score) * 100).toFixed(1),
        type: a.type,
        severity: a.severity
      }));

    // Severity distribution
    const severityDist = {
      low: assessments?.filter(a => a.severity === 'low').length || 0,
      medium: assessments?.filter(a => a.severity === 'medium').length || 0,
      high: assessments?.filter(a => a.severity === 'high').length || 0,
      critical: assessments?.filter(a => a.severity === 'critical').length || 0
    };

    // Forecast (simple trend-based prediction)
    const recentScores = scoreTrends.slice(-5);
    const avgRecentScore = recentScores.length > 0
      ? recentScores.reduce((sum, s) => sum + parseFloat(s.percentage), 0) / recentScores.length
      : null;

    const forecast = avgRecentScore !== null ? {
      next30Days: avgRecentScore > 70 ? 'improving' : avgRecentScore < 40 ? 'declining' : 'stable',
      confidence: recentScores.length >= 3 ? 'medium' : 'low',
      predictedScore: avgRecentScore.toFixed(1)
    } : null;

    return NextResponse.json({
      period,
      summary: {
        totalAssessments,
        totalAppointments,
        completedAppointments,
        completionRate: Math.round(completionRate * 100) / 100
      },
      trends: {
        scoreTrends,
        severityDistribution: severityDist
      },
      forecast
    });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'Failed to fetch outcome analytics' }, { status: 500 });
  }
}











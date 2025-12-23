import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabaseClient';
import { requirePermission } from '@/lib/rbac';

export async function GET(request: NextRequest) {
  try {
    await requirePermission('analytics:appointments:read');
    
    const { searchParams } = new URL(request.url);
    const period = searchParams.get('period') || '30d';
    const clinicId = searchParams.get('clinicId');
    
    const supabase = await createSupabaseServerClient();
    
    // Period calculation
    const now = new Date();
    let startDate: Date;
    switch (period) {
      case '7d': startDate = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000); break;
      case '30d': startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000); break;
      case '90d': startDate = new Date(now.getTime() - 90 * 24 * 60 * 60 * 1000); break;
      case '1y': startDate = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000); break;
      default: startDate = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
    }

    // Fetch appointments
    const { data: appointments, error } = await supabase
      .from('appointments')
      .select('id, patient_id, start_at, status, type, location, created_at')
      .gte('created_at', startDate.toISOString())
      .order('created_at', { ascending: false });

    if (error) throw error;

    const totalAppointments = appointments?.length || 0;

    // Status distribution
    const statusDistribution = appointments?.reduce((acc: Record<string, number>, apt) => {
      acc[apt.status] = (acc[apt.status] || 0) + 1;
      return acc;
    }, {}) || {};

    // Type distribution
    const typeDistribution = appointments?.reduce((acc: Record<string, number>, apt) => {
      acc[apt.type] = (acc[apt.type] || 0) + 1;
      return acc;
    }, {}) || {};

    // Location distribution
    const locationDistribution = appointments?.reduce((acc: Record<string, number>, apt) => {
      const location = apt.location || 'unknown';
      acc[location] = (acc[location] || 0) + 1;
      return acc;
    }, {}) || {};

    // Daily appointment trend
    const dailyTrend = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
      const dayStart = new Date(date.getFullYear(), date.getMonth(), date.getDate());
      const dayEnd = new Date(dayStart.getTime() + 24 * 60 * 60 * 1000);
      
      const dayAppointments = appointments?.filter(apt => {
        const startAt = new Date(apt.start_at);
        return startAt >= dayStart && startAt < dayEnd;
      }).length || 0;
      
      dailyTrend.push({
        date: dayStart.toISOString().split('T')[0],
        count: dayAppointments
      });
    }

    // Hourly distribution (peak hours)
    const hourlyDistribution = Array.from({ length: 24 }, (_, hour) => {
      const hourAppointments = appointments?.filter(apt => {
        const startAt = new Date(apt.start_at);
        return startAt.getHours() === hour;
      }).length || 0;
      
      return {
        hour,
        count: hourAppointments,
        label: `${hour}:00`
      };
    });

    // No-show rate
    const noShowCount = statusDistribution['cancelled'] || 0;
    const noShowRate = totalAppointments > 0 ? (noShowCount / totalAppointments) * 100 : 0;

    // Completion rate
    const completedCount = statusDistribution['completed'] || 0;
    const completionRate = totalAppointments > 0 ? (completedCount / totalAppointments) * 100 : 0;

    // Average appointment duration (estimated)
    const avgDuration = 45; // minutes - could be calculated from actual data

    return NextResponse.json({
      period,
      summary: {
        totalAppointments,
        noShowRate: Math.round(noShowRate * 100) / 100,
        completionRate: Math.round(completionRate * 100) / 100,
        avgDurationMinutes: avgDuration
      },
      distributions: {
        status: statusDistribution,
        type: typeDistribution,
        location: locationDistribution
      },
      trends: {
        dailyAppointments: dailyTrend,
        hourlyDistribution
      },
      metrics: {
        peakHour: hourlyDistribution.reduce((max, curr) => curr.count > max.count ? curr : max, hourlyDistribution[0]),
        busiestDay: dailyTrend.reduce((max, curr) => curr.count > max.count ? curr : max, dailyTrend[0])
      }
    });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'Failed to fetch appointment analytics' }, { status: 500 });
  }
}



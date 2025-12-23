import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabaseClient';
import { requirePermission } from '@/lib/rbac';

export async function GET(request: NextRequest) {
  try {
    await requirePermission('analytics:patients:read');
    
    const { searchParams } = new URL(request.url);
    const period = searchParams.get('period') || '30d'; // 7d, 30d, 90d, 1y
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

    // Patient demographics
    const { data: demographics, error: demoError } = await supabase
      .from('patients')
      .select('age, gender, created_at')
      .gte('created_at', startDate.toISOString())
      .order('created_at', { ascending: false });

    if (demoError) throw demoError;

    // Calculate statistics
    const totalPatients = demographics?.length || 0;
    const ageGroups = {
      '18-25': demographics?.filter(p => p.age >= 18 && p.age <= 25).length || 0,
      '26-35': demographics?.filter(p => p.age >= 26 && p.age <= 35).length || 0,
      '36-45': demographics?.filter(p => p.age >= 36 && p.age <= 45).length || 0,
      '46-55': demographics?.filter(p => p.age >= 46 && p.age <= 55).length || 0,
      '56-65': demographics?.filter(p => p.age >= 56 && p.age <= 65).length || 0,
      '65+': demographics?.filter(p => p.age > 65).length || 0
    };

    const genderDistribution = {
      male: demographics?.filter(p => p.gender === 'male').length || 0,
      female: demographics?.filter(p => p.gender === 'female').length || 0,
      other: demographics?.filter(p => p.gender === 'other').length || 0
    };

    // New patients trend (daily)
    const dailyTrend = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
      const dayStart = new Date(date.getFullYear(), date.getMonth(), date.getDate());
      const dayEnd = new Date(dayStart.getTime() + 24 * 60 * 60 * 1000);
      
      const dayPatients = demographics?.filter(p => {
        const createdAt = new Date(p.created_at);
        return createdAt >= dayStart && createdAt < dayEnd;
      }).length || 0;
      
      dailyTrend.push({
        date: dayStart.toISOString().split('T')[0],
        count: dayPatients
      });
    }

    // Patient retention (appointments per patient)
    const { data: appointments, error: apptError } = await supabase
      .from('appointments')
      .select('patient_id, status, created_at')
      .gte('created_at', startDate.toISOString());

    if (apptError) throw apptError;

    const patientAppointmentCounts = appointments?.reduce((acc: Record<string, number>, apt) => {
      acc[apt.patient_id] = (acc[apt.patient_id] || 0) + 1;
      return acc;
    }, {}) || {};

    const avgAppointmentsPerPatient = totalPatients > 0 
      ? Object.values(patientAppointmentCounts).reduce((sum, count) => sum + count, 0) / totalPatients 
      : 0;

    return NextResponse.json({
      period,
      summary: {
        totalPatients,
        newPatientsThisPeriod: totalPatients,
        avgAppointmentsPerPatient: Math.round(avgAppointmentsPerPatient * 100) / 100
      },
      demographics: {
        ageGroups,
        genderDistribution
      },
      trends: {
        dailyNewPatients: dailyTrend
      },
      retention: {
        avgAppointmentsPerPatient: Math.round(avgAppointmentsPerPatient * 100) / 100,
        patientsWithMultipleAppointments: Object.values(patientAppointmentCounts).filter(count => count > 1).length
      }
    });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'Failed to fetch patient analytics' }, { status: 500 });
  }
}



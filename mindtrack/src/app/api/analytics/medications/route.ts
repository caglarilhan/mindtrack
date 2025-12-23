import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabaseClient';
import { requirePermission } from '@/lib/rbac';

export async function GET(request: NextRequest) {
  try {
    await requirePermission('analytics:medications:read');
    
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

    // Mock medication data (since we don't have medication tables yet)
    const mockMedications = [
      { id: 'med-1', name: 'Sertraline', category: 'SSRI', prescribedCount: 45, patientCount: 38 },
      { id: 'med-2', name: 'Fluoxetine', category: 'SSRI', prescribedCount: 32, patientCount: 28 },
      { id: 'med-3', name: 'Lorazepam', category: 'Benzodiazepine', prescribedCount: 28, patientCount: 25 },
      { id: 'med-4', name: 'Quetiapine', category: 'Atypical Antipsychotic', prescribedCount: 22, patientCount: 20 },
      { id: 'med-5', name: 'Bupropion', category: 'NDRI', prescribedCount: 18, patientCount: 16 },
      { id: 'med-6', name: 'Diazepam', category: 'Benzodiazepine', prescribedCount: 15, patientCount: 14 },
      { id: 'med-7', name: 'Venlafaxine', category: 'SNRI', prescribedCount: 12, patientCount: 11 },
      { id: 'med-8', name: 'Risperidone', category: 'Atypical Antipsychotic', prescribedCount: 10, patientCount: 9 }
    ];

    // Calculate statistics
    const totalPrescriptions = mockMedications.reduce((sum, med) => sum + med.prescribedCount, 0);
    const totalPatientsOnMedication = mockMedications.reduce((sum, med) => sum + med.patientCount, 0);

    // Category distribution
    const categoryDistribution = mockMedications.reduce((acc: Record<string, { count: number, medications: string[] }>, med) => {
      if (!acc[med.category]) {
        acc[med.category] = { count: 0, medications: [] };
      }
      acc[med.category].count += med.prescribedCount;
      acc[med.category].medications.push(med.name);
      return acc;
    }, {});

    // Most prescribed medications
    const topMedications = mockMedications
      .sort((a, b) => b.prescribedCount - a.prescribedCount)
      .slice(0, 5);

    // Medication adherence simulation (mock data)
    const adherenceData = mockMedications.map(med => ({
      medication: med.name,
      adherenceRate: Math.round((85 + Math.random() * 15) * 100) / 100, // 85-100%
      missedDoses: Math.floor(Math.random() * 5),
      sideEffects: Math.floor(Math.random() * 3)
    }));

    // Drug interaction alerts (mock)
    const interactionAlerts = [
      { medications: ['Sertraline', 'Fluoxetine'], severity: 'high', description: 'Serotonin syndrome risk' },
      { medications: ['Lorazepam', 'Diazepam'], severity: 'medium', description: 'Increased sedation' },
      { medications: ['Quetiapine', 'Risperidone'], severity: 'low', description: 'Metabolic effects' }
    ];

    // Side effects tracking (mock)
    const sideEffectsDistribution = {
      'Nausea': 12,
      'Drowsiness': 8,
      'Insomnia': 6,
      'Dry mouth': 5,
      'Headache': 4,
      'Weight gain': 3,
      'Anxiety': 2,
      'Dizziness': 2
    };

    return NextResponse.json({
      period,
      summary: {
        totalPrescriptions,
        totalPatientsOnMedication,
        avgMedicationsPerPatient: totalPatientsOnMedication > 0 
          ? Math.round((totalPrescriptions / totalPatientsOnMedication) * 100) / 100 
          : 0,
        activeMedications: mockMedications.length
      },
      distributions: {
        categories: categoryDistribution,
        sideEffects: sideEffectsDistribution
      },
      topMedications,
      adherence: adherenceData,
      alerts: {
        drugInteractions: interactionAlerts,
        totalAlerts: interactionAlerts.length
      },
      trends: {
        // Mock trend data
        monthlyPrescriptions: [
          { month: 'Ocak', count: 45 },
          { month: 'Şubat', count: 52 },
          { month: 'Mart', count: 48 },
          { month: 'Nisan', count: 61 },
          { month: 'Mayıs', count: 58 },
          { month: 'Haziran', count: 67 }
        ]
      }
    });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'Failed to fetch medication analytics' }, { status: 500 });
  }
}



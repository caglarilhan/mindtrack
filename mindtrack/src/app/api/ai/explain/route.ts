import { NextRequest, NextResponse } from 'next/server';
import { requirePermission } from '@/lib/rbac';

export async function POST(request: NextRequest) {
  try {
    await requirePermission('analytics:patients:read');
    
    const { patientId, decisionType, features } = await request.json();
    
    if (!patientId || !decisionType) {
      return NextResponse.json({ error: 'patientId and decisionType required' }, { status: 400 });
    }

    // Mock SHAP values - gerçek implementasyonda ML model'den gelecek
    // Örnek: risk assessment için feature importance
    const mockShapValues: Record<string, number> = {
      'assessment_score': 0.35,
      'appointment_completion_rate': -0.22,
      'days_since_last_session': 0.18,
      'medication_adherence': -0.15,
      'age': 0.08,
      'session_frequency': -0.12
    };

    // Features varsa onları kullan, yoksa mock değerler
    const shapValues = features 
      ? Object.fromEntries(Object.keys(features).map(key => [key, mockShapValues[key] || 0]))
      : mockShapValues;

    // Feature importance sıralaması
    const featureImportance = Object.entries(shapValues)
      .map(([feature, value]) => ({
        feature,
        importance: Math.abs(value),
        contribution: value > 0 ? 'positive' : 'negative',
        value: value.toFixed(3)
      }))
      .sort((a, b) => b.importance - a.importance);

    // Top 3 contributing factors
    const topContributors = featureImportance.slice(0, 3);

    // Explanation text
    const explanation = `Bu kararın %${(topContributors[0]?.importance * 100).toFixed(0)}'si ${topContributors[0]?.feature} faktöründen kaynaklanıyor. ` +
      `${topContributors[0]?.contribution === 'positive' ? 'Artış' : 'Azalış'} risk seviyesini ${topContributors[0]?.contribution === 'positive' ? 'yükseltiyor' : 'düşürüyor'}.`;

    return NextResponse.json({
      patientId,
      decisionType,
      shapValues,
      featureImportance,
      topContributors,
      explanation,
      model: 'risk_assessment_v1',
      timestamp: new Date().toISOString()
    });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'Failed to generate explanation' }, { status: 500 });
  }
}











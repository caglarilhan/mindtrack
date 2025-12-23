import { NextRequest, NextResponse } from 'next/server';
import { requirePermission } from '@/lib/rbac';
import { writeAudit } from '@/lib/audit';

interface ClinicalData {
  patientAge: number;
  patientGender: string;
  symptoms: string[];
  currentMedications: string[];
  medicalHistory: string[];
  vitalSigns?: {
    bloodPressure?: string;
    heartRate?: number;
    temperature?: number;
    weight?: number;
    height?: number;
  };
}

interface ClinicalRecommendation {
  diagnosis: {
    primary: string;
    secondary?: string[];
    confidence: number;
  };
  treatment: {
    medications: Array<{
      name: string;
      dosage: string;
      duration: string;
      rationale: string;
    }>;
    lifestyle: string[];
    followUp: string;
  };
  warnings: string[];
  references: string[];
}

export async function POST(request: NextRequest) {
  try {
    await requirePermission('ai:clinical:read');
    
    const clinicalData: ClinicalData = await request.json();
    
    if (!clinicalData.patientAge || !clinicalData.symptoms || clinicalData.symptoms.length === 0) {
      return NextResponse.json({ error: 'Patient age and symptoms are required' }, { status: 400 });
    }

    // AI Clinical Decision Support Logic (Mock Implementation)
    const recommendation = await generateClinicalRecommendation(clinicalData);

    // Audit log
    await writeAudit({
      action: 'ai.clinical.decision',
      details: { 
        patientAge: clinicalData.patientAge,
        symptomsCount: clinicalData.symptoms.length,
        diagnosis: recommendation.diagnosis.primary
      },
      userId: 'system'
    });

    return NextResponse.json({
      success: true,
      recommendation,
      disclaimer: 'Bu öneriler AI destekli klinik karar desteği sağlar. Kesin tanı ve tedavi için uzman doktor görüşü gereklidir.',
      generatedAt: new Date().toISOString()
    });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'Failed to generate clinical recommendation' }, { status: 500 });
  }
}

async function generateClinicalRecommendation(data: ClinicalData): Promise<ClinicalRecommendation> {
  // Mock AI Clinical Decision Support
  // In a real implementation, this would integrate with OpenAI, Google Health AI, or similar services
  
  const { patientAge, patientGender, symptoms, currentMedications, medicalHistory } = data;
  
  // Symptom analysis
  const anxietySymptoms = ['kaygı', 'endişe', 'panik', 'huzursuzluk', 'sinirlilik'];
  const depressionSymptoms = ['depresyon', 'üzüntü', 'umutsuzluk', 'enerji kaybı', 'uyku bozukluğu'];
  const bipolarSymptoms = ['mani', 'hipomani', 'duygusal dalgalanma', 'risk alma'];
  
  const hasAnxiety = symptoms.some(s => anxietySymptoms.some(as => s.toLowerCase().includes(as)));
  const hasDepression = symptoms.some(s => depressionSymptoms.some(ds => s.toLowerCase().includes(ds)));
  const hasBipolar = symptoms.some(s => bipolarSymptoms.some(bs => s.toLowerCase().includes(bs)));
  
  // Age-based considerations
  const isElderly = patientAge >= 65;
  const isYoungAdult = patientAge >= 18 && patientAge <= 25;
  
  // Generate diagnosis
  let primaryDiagnosis = 'Genel Psikiyatrik Değerlendirme';
  let confidence = 0.7;
  
  if (hasAnxiety && hasDepression) {
    primaryDiagnosis = 'Anksiyete ve Depresyon Bozukluğu';
    confidence = 0.85;
  } else if (hasAnxiety) {
    primaryDiagnosis = 'Anksiyete Bozukluğu';
    confidence = 0.8;
  } else if (hasDepression) {
    primaryDiagnosis = 'Majör Depresif Bozukluk';
    confidence = 0.8;
  } else if (hasBipolar) {
    primaryDiagnosis = 'Bipolar Bozukluk';
    confidence = 0.75;
  }
  
  // Generate treatment recommendations
  const medications = [];
  const lifestyle = [];
  const warnings = [];
  
  if (primaryDiagnosis.includes('Anksiyete')) {
    medications.push({
      name: 'Sertraline',
      dosage: isElderly ? '25mg/gün' : '50mg/gün',
      duration: '6-12 ay',
      rationale: 'SSRI, anksiyete semptomlarını azaltır'
    });
    
    lifestyle.push('Düzenli egzersiz', 'Nefes egzersizleri', 'Stres yönetimi teknikleri');
  }
  
  if (primaryDiagnosis.includes('Depresyon')) {
    medications.push({
      name: 'Fluoxetine',
      dosage: isElderly ? '10mg/gün' : '20mg/gün',
      duration: '6-12 ay',
      rationale: 'SSRI, depresyon semptomlarını iyileştirir'
    });
    
    lifestyle.push('Düzenli uyku', 'Sosyal aktiviteler', 'Hobi edinme');
  }
  
  if (primaryDiagnosis.includes('Bipolar')) {
    medications.push({
      name: 'Lithium',
      dosage: '300mg 2x/gün',
      duration: 'Uzun süreli',
      rationale: 'Duygudurum stabilizatörü'
    });
    
    warnings.push('Lithium seviyeleri düzenli kontrol edilmeli', 'Su alımına dikkat');
  }
  
  // Age-specific warnings
  if (isElderly) {
    warnings.push('Yaşlı hastalarda ilaç etkileşimleri riski', 'Düşük dozla başlanmalı');
  }
  
  if (isYoungAdult) {
    warnings.push('Genç erişkinlerde intihar riski değerlendirilmeli');
  }
  
  // Drug interaction warnings
  if (currentMedications.length > 0) {
    warnings.push('Mevcut ilaçlarla etkileşim kontrolü yapılmalı');
  }
  
  return {
    diagnosis: {
      primary: primaryDiagnosis,
      secondary: hasAnxiety && hasDepression ? ['Anksiyete Bozukluğu', 'Depresyon'] : [],
      confidence
    },
    treatment: {
      medications,
      lifestyle,
      followUp: '2 hafta sonra kontrol randevusu önerilir'
    },
    warnings,
    references: [
      'DSM-5 Tanı Kriterleri',
      'APA Tedavi Kılavuzları',
      'NICE Guidelines'
    ]
  };
}
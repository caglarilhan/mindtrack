import { NextRequest, NextResponse } from 'next/server';
import { requirePermission } from '@/lib/rbac';
import { writeAudit } from '@/lib/audit';

interface DrugInteractionRequest {
  medications: string[];
  patientAge?: number;
  patientWeight?: number;
  comorbidities?: string[];
}

interface DrugInteraction {
  severity: 'minor' | 'moderate' | 'major' | 'contraindicated';
  description: string;
  mechanism: string;
  clinicalSignificance: string;
  management: string;
  references: string[];
}

interface InteractionResult {
  interactions: DrugInteraction[];
  summary: {
    totalInteractions: number;
    majorInteractions: number;
    contraindications: number;
    riskLevel: 'low' | 'medium' | 'high' | 'critical';
  };
  recommendations: string[];
}

export async function POST(request: NextRequest) {
  try {
    await requirePermission('medications:interactions:read');
    
    const { medications, patientAge, patientWeight, comorbidities }: DrugInteractionRequest = await request.json();
    
    if (!medications || medications.length < 2) {
      return NextResponse.json({ error: 'At least 2 medications are required for interaction check' }, { status: 400 });
    }

    // Drug Interaction Check Logic
    const interactionResult = await checkDrugInteractions(medications, patientAge, patientWeight, comorbidities);

    // Audit log
    await writeAudit({
      action: 'medications.interaction.check',
      details: { 
        medicationCount: medications.length,
        riskLevel: interactionResult.summary.riskLevel,
        majorInteractions: interactionResult.summary.majorInteractions
      },
      userId: 'system'
    });

    return NextResponse.json({
      success: true,
      result: interactionResult,
      checkedAt: new Date().toISOString(),
      disclaimer: 'Bu etkileşim kontrolü referans amaçlıdır. Kesin değerlendirme için eczacı veya doktor görüşü gereklidir.'
    });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'Failed to check drug interactions' }, { status: 500 });
  }
}

async function checkDrugInteractions(
  medications: string[], 
  patientAge?: number, 
  patientWeight?: number, 
  comorbidities?: string[]
): Promise<InteractionResult> {
  
  // Mock Drug Interaction Database
  const interactionDatabase = {
    'Sertraline': {
      'Fluoxetine': {
        severity: 'major',
        description: 'Serotonin Sendromu Riski',
        mechanism: 'Her iki ilaç da serotonin geri alımını inhibe eder',
        clinicalSignificance: 'Yüksek ateş, kas sertliği, mental durum değişiklikleri',
        management: 'İlaçların birlikte kullanımından kaçınılmalı',
        references: ['Lexicomp', 'Drugs.com']
      },
      'Warfarin': {
        severity: 'moderate',
        description: 'Kanama Riski Artışı',
        mechanism: 'Sertraline warfarin metabolizmasını etkiler',
        clinicalSignificance: 'INR değerleri artabilir',
        management: 'INR değerleri yakın takip edilmeli',
        references: ['Lexicomp']
      },
      'Lithium': {
        severity: 'moderate',
        description: 'Serotonin Sendromu Riski',
        mechanism: 'Lithium serotonin seviyelerini artırabilir',
        clinicalSignificance: 'Serotonin sendromu belirtileri',
        management: 'Dikkatli kullanım ve yakın takip',
        references: ['Drugs.com']
      }
    },
    'Fluoxetine': {
      'Sertraline': {
        severity: 'major',
        description: 'Serotonin Sendromu Riski',
        mechanism: 'Her iki ilaç da serotonin geri alımını inhibe eder',
        clinicalSignificance: 'Yüksek ateş, kas sertliği, mental durum değişiklikleri',
        management: 'İlaçların birlikte kullanımından kaçınılmalı',
        references: ['Lexicomp', 'Drugs.com']
      },
      'Tramadol': {
        severity: 'major',
        description: 'Serotonin Sendromu Riski',
        mechanism: 'Fluoxetine tramadol metabolizmasını inhibe eder',
        clinicalSignificance: 'Serotonin sendromu riski artar',
        management: 'Tramadol dozu azaltılmalı veya alternatif kullanılmalı',
        references: ['Lexicomp']
      }
    },
    'Lorazepam': {
      'Alcohol': {
        severity: 'major',
        description: 'Merkezi Sinir Sistemi Depresyonu',
        mechanism: 'Her iki madde de GABA reseptörlerini etkiler',
        clinicalSignificance: 'Solunum depresyonu, koma riski',
        management: 'Alkol kullanımından kaçınılmalı',
        references: ['Drugs.com']
      },
      'Opioids': {
        severity: 'major',
        description: 'Solunum Depresyonu Riski',
        mechanism: 'Her iki ilaç da merkezi sinir sistemini baskılar',
        clinicalSignificance: 'Solunum durması riski',
        management: 'Kontrendike kombinasyon',
        references: ['FDA']
      }
    },
    'Lithium': {
      'NSAIDs': {
        severity: 'moderate',
        description: 'Lithium Toksisitesi Riski',
        mechanism: 'NSAID\'ler lithium eliminasyonunu azaltır',
        clinicalSignificance: 'Lithium seviyeleri artabilir',
        management: 'Lithium seviyeleri yakın takip edilmeli',
        references: ['Lexicomp']
      },
      'ACE Inhibitors': {
        severity: 'moderate',
        description: 'Lithium Seviyesi Artışı',
        mechanism: 'ACE inhibitörleri lithium eliminasyonunu azaltır',
        clinicalSignificance: 'Lithium toksisitesi riski',
        management: 'Lithium dozu azaltılabilir',
        references: ['Drugs.com']
      }
    }
  };

  const interactions: DrugInteraction[] = [];
  const checkedPairs = new Set<string>();

  // Check all medication pairs
  for (let i = 0; i < medications.length; i++) {
    for (let j = i + 1; j < medications.length; j++) {
      const med1 = medications[i];
      const med2 = medications[j];
      const pairKey = `${med1}-${med2}`;
      const reversePairKey = `${med2}-${med1}`;
      
      if (checkedPairs.has(pairKey) || checkedPairs.has(reversePairKey)) {
        continue;
      }
      
      checkedPairs.add(pairKey);
      
      // Check interaction database
      const interaction = interactionDatabase[med1]?.[med2] || interactionDatabase[med2]?.[med1];
      
      if (interaction) {
        interactions.push(interaction);
      }
    }
  }

  // Age-specific interactions
  if (patientAge && patientAge >= 65) {
    interactions.push({
      severity: 'moderate',
      description: 'Yaşlı Hastada İlaç Etkileşimi Riski',
      mechanism: 'Yaşlı hastalarda ilaç metabolizması yavaşlar',
      clinicalSignificance: 'İlaç seviyeleri artabilir, yan etki riski yüksek',
      management: 'Düşük dozla başlanmalı, yakın takip edilmeli',
      references: ['Beers Criteria']
    });
  }

  // Comorbidity-specific interactions
  if (comorbidities?.includes('liver_disease')) {
    interactions.push({
      severity: 'moderate',
      description: 'Karaciğer Hastalığında Metabolizma Riski',
      mechanism: 'Karaciğer fonksiyon bozukluğu ilaç metabolizmasını etkiler',
      clinicalSignificance: 'İlaç birikimi ve toksisite riski',
      management: 'Karaciğer fonksiyonları takip edilmeli',
      references: ['Clinical Pharmacology']
    });
  }

  // Calculate summary
  const majorInteractions = interactions.filter(i => i.severity === 'major').length;
  const contraindications = interactions.filter(i => i.severity === 'contraindicated').length;
  
  let riskLevel: 'low' | 'medium' | 'high' | 'critical' = 'low';
  if (contraindications > 0) {
    riskLevel = 'critical';
  } else if (majorInteractions > 0) {
    riskLevel = 'high';
  } else if (interactions.length > 2) {
    riskLevel = 'medium';
  }

  // Generate recommendations
  const recommendations: string[] = [];
  
  if (riskLevel === 'critical') {
    recommendations.push('Bu ilaç kombinasyonu kontrendikedir. Alternatif tedavi seçenekleri değerlendirilmeli.');
  } else if (riskLevel === 'high') {
    recommendations.push('Major etkileşimler tespit edildi. Yakın takip ve doz ayarlaması gerekebilir.');
  } else if (riskLevel === 'medium') {
    recommendations.push('Orta düzeyde etkileşimler mevcut. Hastanın durumu yakından izlenmeli.');
  } else {
    recommendations.push('Minor etkileşimler tespit edildi. Rutin takip yeterli olabilir.');
  }

  if (patientAge && patientAge >= 65) {
    recommendations.push('Yaşlı hasta - ilaç dozları dikkatli ayarlanmalı.');
  }

  return {
    interactions,
    summary: {
      totalInteractions: interactions.length,
      majorInteractions,
      contraindications,
      riskLevel
    },
    recommendations
  };
}



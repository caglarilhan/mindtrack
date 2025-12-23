export interface SOAPTemplate {
  id: string;
  name: string;
  description: string;
  therapyType: string;
  sections: {
    subjective: string[];
    objective: string[];
    assessment: string[];
    plan: string[];
  };
}

export const DEFAULT_TEMPLATES: SOAPTemplate[] = [
  {
    id: 'general',
    name: 'Genel Terapi',
    description: 'Genel psikoterapi seansları için standart şablon',
    therapyType: 'general',
    sections: {
      subjective: [
        'Danışanın şikayetleri',
        'Duygusal durum',
        'Günlük yaşam etkisi',
      ],
      objective: [
        'Görünüm ve davranış',
        'Göz teması ve afekt',
        'Konuşma hızı ve tonu',
      ],
      assessment: [
        'Klinik değerlendirme',
        'İlerleme durumu',
        'Risk faktörleri',
      ],
      plan: [
        'Sonraki seans planı',
        'Ev ödevi',
        'Takip planı',
      ],
    },
  },
  {
    id: 'cbt',
    name: 'Bilişsel Davranışçı Terapi (CBT)',
    description: 'CBT seansları için özelleştirilmiş şablon',
    therapyType: 'cbt',
    sections: {
      subjective: [
        'Otomatik düşünceler',
        'Duygusal tepkiler',
        'Davranışsal gözlemler',
      ],
      objective: [
        'Düşünce kayıtları',
        'Davranış deneyleri',
        'Bilişsel çarpıtmalar',
      ],
      assessment: [
        'Bilişsel yapı analizi',
        'İşlevsel olmayan düşünceler',
        'Değişim ölçümü',
      ],
      plan: [
        'Bilişsel yeniden yapılandırma',
        'Davranış deneyleri',
        'Ev ödevi ve kayıtlar',
      ],
    },
  },
  {
    id: 'crisis',
    name: 'Kriz Müdahalesi',
    description: 'Acil durumlar ve kriz seansları için şablon',
    therapyType: 'crisis',
    sections: {
      subjective: [
        'Kriz durumu',
        'Acil ihtiyaçlar',
        'Risk faktörleri',
      ],
      objective: [
        'Güvenlik değerlendirmesi',
        'Duygusal durum',
        'Davranışsal gözlemler',
      ],
      assessment: [
        'Risk seviyesi',
        'Acil müdahale gereksinimi',
        'Destek sistemleri',
      ],
      plan: [
        'Acil güvenlik planı',
        'Destek kaynakları',
        'Takip planı',
      ],
    },
  },
  {
    id: 'family',
    name: 'Aile Terapisi',
    description: 'Aile terapisi seansları için şablon',
    therapyType: 'family',
    sections: {
      subjective: [
        'Aile dinamikleri',
        'İletişim kalıpları',
        'Çatışma alanları',
      ],
      objective: [
        'Aile etkileşimleri',
        'Gözlemler',
        'Rol dağılımları',
      ],
      assessment: [
        'Aile sistemi analizi',
        'İşlevsellik değerlendirmesi',
        'Değişim potansiyeli',
      ],
      plan: [
        'Aile müdahaleleri',
        'İletişim egzersizleri',
        'Sonraki seans planı',
      ],
    },
  },
];

/**
 * Template'i SOAP notuna uygula
 */
export function applyTemplate(template: SOAPTemplate): {
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
} {
  return {
    subjective: template.sections.subjective
      .map((item, idx) => `${idx + 1}. ${item}:`)
      .join('\n'),
    objective: template.sections.objective
      .map((item, idx) => `${idx + 1}. ${item}:`)
      .join('\n'),
    assessment: template.sections.assessment
      .map((item, idx) => `${idx + 1}. ${item}:`)
      .join('\n'),
    plan: template.sections.plan
      .map((item, idx) => `${idx + 1}. ${item}:`)
      .join('\n'),
  };
}

/**
 * Template'i ID'ye göre bul
 */
export function getTemplateById(id: string): SOAPTemplate | null {
  return DEFAULT_TEMPLATES.find(t => t.id === id) || null;
}

/**
 * Terapi türüne göre template'leri getir
 */
export function getTemplatesByTherapyType(therapyType: string): SOAPTemplate[] {
  return DEFAULT_TEMPLATES.filter(t => t.therapyType === therapyType);
}






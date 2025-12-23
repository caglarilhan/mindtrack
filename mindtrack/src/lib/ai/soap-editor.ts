import { getAIOrchestrator } from "./orchestrator";
import type { SOAPNote } from "./gemini-service";

export interface EditSuggestion {
  section: 'subjective' | 'objective' | 'assessment' | 'plan';
  original: string;
  suggested: string;
  reason: string;
  confidence: number;
}

/**
 * SOAP notu bölümünü AI ile düzenle
 */
export async function editSOAPSection(
  section: 'subjective' | 'objective' | 'assessment' | 'plan',
  content: string,
  instruction: string
): Promise<string> {
  try {
    const orchestrator = getAIOrchestrator();
    
    // Basit prompt ile düzenleme
    const prompt = `Aşağıdaki SOAP notu ${section} bölümünü düzenle:

Mevcut içerik:
${content}

Talimat: ${instruction}

Lütfen düzenlenmiş versiyonu döndür. Sadece içeriği döndür, başka açıklama yapma.`;

    // Gemini kullanarak düzenleme yap
    const { getGeminiService } = await import('./gemini-service');
    const gemini = getGeminiService();
    
    if (!gemini.isAvailable()) {
      return content; // Fallback: orijinal içeriği döndür
    }

    const result = await (gemini as any).model.generateContent(prompt);
    const edited = result.response.text().trim();
    
    return edited || content;
  } catch (error) {
    console.error('SOAP düzenleme hatası:', error);
    return content; // Hata durumunda orijinal içeriği döndür
  }
}

/**
 * SOAP notu için AI önerileri al
 */
export async function getSOAPSuggestions(
  soap: SOAPNote,
  context?: string
): Promise<EditSuggestion[]> {
  try {
    const { getGeminiService } = await import('./gemini-service');
    const gemini = getGeminiService();
    
    if (!gemini.isAvailable()) {
      return [];
    }

    const prompt = `Aşağıdaki SOAP notunu analiz et ve iyileştirme önerileri sun:

${JSON.stringify(soap, null, 2)}

${context ? `Context: ${context}` : ''}

Her bölüm için şu formatta öneriler sun:
- Eksik bilgiler varsa tamamla
- Gramer hatalarını düzelt
- Klinik terminolojiyi iyileştir
- Daha profesyonel bir dil kullan

JSON formatında döndür:
[
  {
    "section": "subjective",
    "original": "...",
    "suggested": "...",
    "reason": "...",
    "confidence": 0.8
  }
]`;

    const result = await (gemini as any).model.generateContent(prompt);
    const response = result.response.text();
    
    // JSON parse et
    const jsonMatch = response.match(/\[[\s\S]*\]/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[0]) as EditSuggestion[];
    }
    
    return [];
  } catch (error) {
    console.error('SOAP önerileri hatası:', error);
    return [];
  }
}

/**
 * Eksik bilgileri tamamla
 */
export async function completeSOAPSection(
  section: 'subjective' | 'objective' | 'assessment' | 'plan',
  content: string,
  previousSessions?: string[]
): Promise<string> {
  try {
    const { getGeminiService } = await import('./gemini-service');
    const gemini = getGeminiService();
    
    if (!gemini.isAvailable()) {
      return content;
    }

    const context = previousSessions 
      ? `Geçmiş seanslar:\n${previousSessions.join('\n\n')}`
      : '';

    const prompt = `Aşağıdaki SOAP notu ${section} bölümünü tamamla ve iyileştir:

Mevcut içerik:
${content}

${context}

Eksik bilgileri ekle, daha detaylı ve profesyonel hale getir. Sadece içeriği döndür.`;

    const result = await (gemini as any).model.generateContent(prompt);
    const completed = result.response.text().trim();
    
    return completed || content;
  } catch (error) {
    console.error('SOAP tamamlama hatası:', error);
    return content;
  }
}






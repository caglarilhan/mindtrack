import { GoogleGenerativeAI } from "@google/generative-ai";

export interface ClinicalSummary {
  timeline: Array<{
    date: string;
    event: string;
    severity?: "low" | "medium" | "high";
  }>;
  keyFindings: string[];
  medicationHistory: string[];
  riskFactors: string[];
  familyHistory: string[];
}

export interface SOAPNote {
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
}

export class GeminiService {
  private client: GoogleGenerativeAI;
  private model: any;

  constructor() {
    const apiKey = process.env.GOOGLE_GEMINI_API_KEY;
    if (!apiKey) {
      console.warn("⚠️ GOOGLE_GEMINI_API_KEY eksik - Gemini servisi devre dışı");
      // Fallback için boş client (mock mode)
      this.client = {} as GoogleGenerativeAI;
      return;
    }

    try {
      this.client = new GoogleGenerativeAI(apiKey);
      // Model adı: gemini-2.5-flash (hızlı ve ücretsiz) veya gemini-2.5-pro (daha güçlü)
      // API'den kontrol edildi: gemini-2.5-flash ve gemini-2.5-pro mevcut
      this.model = this.client.getGenerativeModel({ 
        model: "gemini-2.5-flash", // Free tier için önerilen model, 1M token context
        generationConfig: {
          temperature: 0.3,
          topP: 0.95,
          topK: 40,
        }
      });
    } catch (error) {
      console.error("❌ Gemini servisi başlatılamadı:", error);
      this.client = {} as GoogleGenerativeAI;
    }
  }

  /**
   * Büyük hasta verilerini özetler (hafıza görevi)
   */
  async summarizePatientData(patientData: string): Promise<ClinicalSummary> {
    if (!this.model) {
      return this.getMockSummary();
    }

    try {
      const prompt = `Sen bir psikiyatrist asistanısın. Aşağıdaki hasta verilerini oku ve yapılandırılmış bir klinik özet çıkar.

VERİLER:
${patientData}

Çıktı formatı (JSON):
{
  "timeline": [
    {"date": "2021-01", "event": "X ilacı kullanıldı", "severity": "medium"},
    {"date": "2022-03", "event": "Baba ile çatışma", "severity": "high"}
  ],
  "keyFindings": [
    "3 yıl önce X ilacı yan etki yaptı",
    "Babasıyla ilişki travmatik",
    "Son 2 aydır uyku düzeni bozuk"
  ],
  "medicationHistory": ["İlaç adı", "Doğz", "Tarih"],
  "riskFactors": ["Risk faktörü 1", "Risk faktörü 2"],
  "familyHistory": ["Aile geçmişi notları"]
}

Sadece JSON döndür, başka açıklama yapma.`;

      const result = await this.model.generateContent(prompt);
      const response = result.response.text();
      
      // JSON parse et
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]) as ClinicalSummary;
      }

      return this.getMockSummary();
    } catch (error) {
      console.error("❌ Gemini özetleme hatası:", error);
      return this.getMockSummary();
    }
  }

  /**
   * Seans transkriptinden SOAP notu oluşturur
   */
  async generateSOAP(transcript: string): Promise<SOAPNote> {
    if (!this.model) {
      return this.getMockSOAP();
    }

    try {
      const prompt = `Sen bir psikolog asistanısın. Aşağıdaki seans transkriptinden profesyonel bir SOAP notu oluştur.

Transkript:
${transcript}

Lütfen aşağıdaki formatı kullanarak SOAP notu oluştur:

**Subjective (S):**
- Danışanın ifadeleri, şikayetleri, duyguları
- Kendi sözleriyle anlattıkları

**Objective (O):**
- Terapist gözlemleri
- Davranışsal gözlemler
- Görünüm, göz teması, konuşma hızı, afekt

**Assessment (A):**
- Klinik değerlendirme
- Tanısal düşünceler
- Risk faktörleri (varsa)
- İlerleme değerlendirmesi

**Plan (P):**
- Sonraki seans planı
- Müdahaleler
- Ev ödevi veya öneriler
- Takip planı

SOAP notunu Türkçe olarak, profesyonel ve klinik bir dille yaz. Her bölümü net bir şekilde ayır.`;

      const result = await this.model.generateContent(prompt);
      const response = result.response.text();

      return this.parseSOAP(response);
    } catch (error) {
      console.error("❌ Gemini SOAP oluşturma hatası:", error);
      return this.getMockSOAP();
    }
  }

  /**
   * SOAP notunu parse eder
   */
  private parseSOAP(text: string): SOAPNote {
    // Önce markdown formatını temizle
    const cleanText = text.replace(/\*\*/g, "").trim();
    
    const sections = {
      subjective: this.extractSection(cleanText, "Subjective", "Objective"),
      objective: this.extractSection(cleanText, "Objective", "Assessment"),
      assessment: this.extractSection(cleanText, "Assessment", "Plan"),
      plan: this.extractSection(cleanText, "Plan", ""),
    };

    // Eğer parse başarısız olduysa, alternatif formatları dene
    if (!sections.subjective || sections.subjective.length < 10) {
      // (S): formatını dene
      sections.subjective = this.extractSection(cleanText, "(S)", "(O)") || 
                            this.extractSection(cleanText, "S:", "O:") ||
                            sections.subjective;
    }
    
    if (!sections.objective || sections.objective.length < 10) {
      sections.objective = this.extractSection(cleanText, "(O)", "(A)") ||
                          this.extractSection(cleanText, "O:", "A:") ||
                          sections.objective;
    }
    
    if (!sections.assessment || sections.assessment.length < 10) {
      sections.assessment = this.extractSection(cleanText, "(A)", "(P)") ||
                           this.extractSection(cleanText, "A:", "P:") ||
                           sections.assessment;
    }
    
    if (!sections.plan || sections.plan.length < 10) {
      sections.plan = this.extractSection(cleanText, "(P)", "") ||
                     this.extractSection(cleanText, "P:", "") ||
                     sections.plan;
    }

    // Eğer hala parse başarısız olduysa, mock döndür
    if ((!sections.subjective || sections.subjective.length < 10) && 
        (!sections.objective || sections.objective.length < 10)) {
      console.warn("⚠️ SOAP parse başarısız, mock döndürülüyor");
      return this.getMockSOAP();
    }

    return sections;
  }

  private extractSection(
    text: string,
    startMarker: string,
    endMarker: string
  ): string {
    // Markdown formatını temizle
    const cleanText = text.replace(/\*\*/g, "").trim();
    const lowerText = cleanText.toLowerCase();
    
    // Farklı formatları dene
    const startPatterns = [
      `${startMarker.toLowerCase()}:`, // "Subjective:"
      `(${startMarker.charAt(0).toLowerCase()}):`, // "(S):"
      startMarker.toLowerCase(), // "Subjective"
    ];
    
    let startIndex = -1;
    for (const pattern of startPatterns) {
      const idx = lowerText.indexOf(pattern);
      if (idx !== -1) {
        startIndex = idx + pattern.length;
        // Sonraki satıra geç
        const nextLineBreak = cleanText.indexOf("\n", startIndex);
        if (nextLineBreak !== -1) {
          startIndex = nextLineBreak + 1;
        }
        break;
      }
    }
    
    if (startIndex === -1) return "";

    const sectionText = cleanText.substring(startIndex).trim();

    if (endMarker) {
      // End marker için de farklı formatları dene
      const endPatterns = [
        `${endMarker.toLowerCase()}:`, // "Objective:"
        `(${endMarker.charAt(0).toLowerCase()}):`, // "(O):"
        endMarker.toLowerCase(), // "Objective"
      ];
      
      let endIndex = -1;
      for (const pattern of endPatterns) {
        const idx = sectionText.toLowerCase().indexOf(pattern);
        if (idx !== -1) {
          endIndex = idx;
          break;
        }
      }

      if (endIndex !== -1) {
        return sectionText.substring(0, endIndex).trim();
      }
    }

    return sectionText.trim();
  }

  /**
   * Mock veriler (fallback)
   */
  private getMockSummary(): ClinicalSummary {
    return {
      timeline: [
        { date: "2024-01", event: "İlk seans", severity: "low" },
      ],
      keyFindings: ["Mock veri"],
      medicationHistory: [],
      riskFactors: [],
      familyHistory: [],
    };
  }

  private getMockSOAP(): SOAPNote {
    return {
      subjective: "Danışan bu seansta...",
      objective: "Gözlemler...",
      assessment: "Değerlendirme...",
      plan: "Plan...",
    };
  }

  /**
   * Servisin aktif olup olmadığını kontrol eder
   */
  isAvailable(): boolean {
    return !!this.model;
  }
}

// Singleton instance
let geminiServiceInstance: GeminiService | null = null;

export function getGeminiService(): GeminiService {
  if (!geminiServiceInstance) {
    geminiServiceInstance = new GeminiService();
  }
  return geminiServiceInstance;
}


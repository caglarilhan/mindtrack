import { getGeminiService, ClinicalSummary, SOAPNote } from "./gemini-service";
import { getOpenAIClient } from "../ai-assistant";

export type ProcessingMode = "standard" | "premium" | "consultation";

export interface PatientData {
  sessions: Array<{ date: string; transcript: string }>;
  rawData: string;
  riskFactors: string[];
  sessionCount: number;
}

export interface HybridResult {
  summary?: ClinicalSummary;
  soap?: SOAPNote;
  flow: "gemini-only" | "hybrid" | "consultation";
  complexity: number;
  costEstimate?: {
    gemini: number;
    openai?: number;
    total: number;
  };
}

export class AIOrchestrator {
  private gemini = getGeminiService();
  private openai = getOpenAIClient();

  /**
   * Kompleksite skoru hesaplar (0-1 arası)
   */
  calculateComplexity(data: PatientData): number {
    const factors = {
      sessionCount: Math.min(data.sessionCount / 50, 1), // 0-1 (50+ seans = 1)
      dataSize: Math.min(data.rawData.length / 200000, 1), // 0-1 (200K+ karakter = 1)
      riskFactors: Math.min(data.riskFactors.length / 5, 1), // 0-1 (5+ risk = 1)
    };

    // Ağırlıklı ortalama
    return (
      factors.sessionCount * 0.4 +
      factors.dataSize * 0.4 +
      factors.riskFactors * 0.2
    );
  }

  /**
   * SOAP notu oluşturur (router ile)
   */
  async processSOAP(
    transcript: string,
    mode: ProcessingMode = "standard",
    patientData?: PatientData
  ): Promise<SOAPNote> {
    // Kompleksite skoru hesapla
    const complexity = patientData
      ? this.calculateComplexity(patientData)
      : this.estimateComplexityFromTranscript(transcript);

    // Router mantığı
    if (mode === "standard" && complexity < 0.7) {
      // Basit: Sadece Gemini
      console.log("📊 Router: Gemini-only (basit vaka)");
      return await this.gemini.generateSOAP(transcript);
    }

    if (mode === "premium" || complexity >= 0.7) {
      // Karmaşık: Hybrid flow
      console.log("📊 Router: Hybrid flow (karmaşık vaka)");
      return await this.hybridSOAP(transcript, patientData);
    }

    if (mode === "consultation") {
      // Konsültasyon: Paralel
      console.log("📊 Router: Consultation mode (ikinci görüş)");
      return await this.consultationSOAP(transcript, patientData);
    }

    // Fallback: Gemini
    return await this.gemini.generateSOAP(transcript);
  }

  /**
   * Hybrid flow: Gemini özetle → OpenAI analiz et
   */
  private async hybridSOAP(
    transcript: string,
    patientData?: PatientData
  ): Promise<SOAPNote> {
    try {
      // 1. Gemini özetle (hafıza)
      let summary: ClinicalSummary | null = null;
      
      if (patientData && patientData.rawData.length > 10000) {
        // Büyük veri varsa önce özetle
        summary = await this.gemini.summarizePatientData(patientData.rawData);
        console.log("✅ Gemini özetleme tamamlandı");
      }

      // 2. OpenAI analiz et (akıl)
      const openAIPrompt = summary
        ? `Vaka özeti:
${JSON.stringify(summary, null, 2)}

Seans transkripti:
${transcript}

Bu bilgilere göre profesyonel bir SOAP notu oluştur. Türkçe yaz.`
        : `Seans transkripti:
${transcript}

Profesyonel bir SOAP notu oluştur. Türkçe yaz.`;

      const completion = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content:
              "Sen kıdemli bir psikologsun. Klinik, profesyonel SOAP notları oluştur.",
          },
          {
            role: "user",
            content: openAIPrompt,
          },
        ],
        temperature: 0.7,
        max_tokens: 1500,
      });

      const response = completion.choices[0]?.message?.content || "";
      return this.parseSOAP(response);
    } catch (error) {
      console.error("❌ Hybrid SOAP hatası:", error);
      // Fallback: Gemini
      return await this.gemini.generateSOAP(transcript);
    }
  }

  /**
   * Konsültasyon modu: Paralel işleme
   */
  private async consultationSOAP(
    transcript: string,
    patientData?: PatientData
  ): Promise<SOAPNote> {
    try {
      // Paralel işleme
      const [geminiResult, openAIResult] = await Promise.all([
        this.gemini.generateSOAP(transcript),
        this.hybridSOAP(transcript, patientData),
      ]);

      // Karşılaştır ve consensus oluştur
      return this.consensusSOAP(geminiResult, openAIResult);
    } catch (error) {
      console.error("❌ Konsültasyon modu hatası:", error);
      // Fallback: Gemini
      return await this.gemini.generateSOAP(transcript);
    }
  }

  /**
   * İki SOAP notunu karşılaştırır ve consensus oluşturur
   */
  private consensusSOAP(
    geminiSOAP: SOAPNote,
    openAISOAP: SOAPNote
  ): SOAPNote {
    // Basit consensus: Her bölüm için daha detaylı olanı seç
    return {
      subjective: this.mergeSections(
        geminiSOAP.subjective,
        openAISOAP.subjective
      ),
      objective: this.mergeSections(
        geminiSOAP.objective,
        openAISOAP.objective
      ),
      assessment: this.mergeSections(
        geminiSOAP.assessment,
        openAISOAP.assessment
      ),
      plan: this.mergeSections(geminiSOAP.plan, openAISOAP.plan),
    };
  }

  private mergeSections(section1: string, section2: string): string {
    // Daha uzun ve detaylı olanı seç
    if (section1.length > section2.length) {
      return section1;
    }
    return section2;
  }

  /**
   * Transkriptten kompleksite tahmin eder
   */
  private estimateComplexityFromTranscript(transcript: string): number {
    const length = transcript.length;
    const wordCount = transcript.split(/\s+/).length;
    const riskKeywords = [
      "intihar",
      "ölmek",
      "zarar",
      "şiddet",
      "kriz",
      "acil",
    ].filter((keyword) =>
      transcript.toLowerCase().includes(keyword)
    ).length;

    return Math.min(
      (length / 5000) * 0.4 + (wordCount / 1000) * 0.4 + (riskKeywords / 3) * 0.2,
      1
    );
  }

  /**
   * SOAP notunu parse eder
   */
  private parseSOAP(text: string): SOAPNote {
    const sections = {
      subjective: this.extractSection(text, "Subjective", "Objective"),
      objective: this.extractSection(text, "Objective", "Assessment"),
      assessment: this.extractSection(text, "Assessment", "Plan"),
      plan: this.extractSection(text, "Plan", ""),
    };

    // Eğer parse başarısız olduysa, mock döndür
    if (!sections.subjective && !sections.objective) {
      return {
        subjective: text.substring(0, 200),
        objective: "",
        assessment: "",
        plan: "",
      };
    }

    return sections;
  }

  private extractSection(
    text: string,
    startMarker: string,
    endMarker: string
  ): string {
    const startIndex = text.indexOf(startMarker);
    if (startIndex === -1) return "";

    const sectionStart = startIndex + startMarker.length;
    const sectionText = text.substring(sectionStart);

    if (endMarker) {
      const endIndex = sectionText.indexOf(endMarker);
      if (endIndex !== -1) {
        return sectionText.substring(0, endIndex).trim();
      }
    }

    return sectionText.trim();
  }
}

// Singleton instance
let orchestratorInstance: AIOrchestrator | null = null;

export function getAIOrchestrator(): AIOrchestrator {
  if (!orchestratorInstance) {
    orchestratorInstance = new AIOrchestrator();
  }
  return orchestratorInstance;
}






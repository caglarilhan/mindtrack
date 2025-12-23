export type Speaker = "patient" | "provider" | "caregiver" | "system";

export interface TranscriptSegment {
  timestamp: number;
  speaker: Speaker;
  text: string;
  duration?: number;
}

export interface RiskTickerEvent {
  severity: "low" | "medium" | "high" | "critical";
  category: "self-harm" | "medication" | "violence" | "crisis-plan" | "other";
  message: string;
  transcriptSegment: string;
  recommendedAction: string;
  detectedAt: string;
}

interface KeywordRule {
  match: RegExp;
  category: RiskTickerEvent["category"];
  severity: RiskTickerEvent["severity"];
  recommendedAction: string;
}

const KEYWORD_RULES: KeywordRule[] = [
  {
    match: /(intihar|self[- ]?harm|kendimi öldür|yaşamak istemiyorum)/i,
    category: "self-harm",
    severity: "critical",
    recommendedAction: "Kriz protokolünü başlat, acil iletişim kişisini bilgilendir.",
  },
  {
    match: /(ilaç|doz|yan etki|ateş|baygınlık|ateş bastı)/i,
    category: "medication",
    severity: "high",
    recommendedAction: "İlaç yan etkisi protokolünü kontrol et, gerekirse hekim onayı al.",
  },
  {
    match: /(vururum|zarar veririm|saldır|döv)/i,
    category: "violence",
    severity: "high",
    recommendedAction: "De-eskalasyon adımlarını uygula, gerekirse güvenlik ekiplerini haberdar et.",
  },
  {
    match: /(kriz planı|safety plan|güvenlik planı)/i,
    category: "crisis-plan",
    severity: "medium",
    recommendedAction: "Kriz planını gözden geçir, danışanla adımları teyit et.",
  },
];

export function analyzeTranscriptSegment(
  segment: TranscriptSegment,
  region: "us" | "eu" = "us",
): RiskTickerEvent | null {
  const text = segment.text.toLowerCase();
  for (const rule of KEYWORD_RULES) {
    if (rule.match.test(text)) {
      return {
        severity: rule.severity,
        category: rule.category,
        message: `Risk tespit edildi: ${rule.category}`,
        transcriptSegment: segment.text.slice(0, 280),
        recommendedAction: rule.recommendedAction,
        detectedAt: new Date().toISOString(),
      };
    }
  }

  // Region-based light heuristic (örnek)
  if (region === "eu" && text.includes("112")) {
    return {
      severity: "critical",
      category: "crisis-plan",
      message: "112 ifadesi geçti, acil yönlendirme gerekebilir.",
      transcriptSegment: segment.text.slice(0, 280),
      recommendedAction: "Kriz protokolünü aç ve 112 bağlantısını hazırla.",
      detectedAt: new Date().toISOString(),
    };
  }

  return null;
}

export function processTranscriptStream(
  segments: TranscriptSegment[],
  region: "us" | "eu" = "us",
) {
  const events: RiskTickerEvent[] = [];
  for (const segment of segments) {
    const risk = analyzeTranscriptSegment(segment, region);
    if (risk) {
      events.push(risk);
    }
  }
  const criticalCount = events.filter((e) => e.severity === "critical" || e.severity === "high").length;
  return { events, criticalCount };
}











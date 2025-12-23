/**
 * Voice Risk Detection
 * CRITICAL: Multi-signal risk detection with false positive reduction
 */

import { detectEmotionsHybrid, type EmotionScores } from "../ai/emotion-detection";
import { type AudioFeatures } from "../audio/audio-features";
import { processWithAI, type HIPAACompliantAIRequest } from "../ai/hipaa-compliant-processor";
import { getAIOrchestrator } from "../ai/orchestrator";

export type RiskLevel = "low" | "medium" | "high" | "critical";

export interface RiskSignal {
  type: "keyword" | "emotion" | "audio" | "pattern";
  severity: RiskLevel;
  description: string;
  confidence: number; // 0-1
  source: string;
}

export interface RiskDetectionResult {
  riskLevel: RiskLevel;
  riskScore: number; // 0-100
  signals: RiskSignal[];
  confidence: number; // 0-1
  requiresImmediateAttention: boolean;
  recommendations: string[];
  timestamp: number;
}

/**
 * Risk keywords (Turkish)
 */
const RISK_KEYWORDS = {
  critical: [
    "intihar", "kendimi öldürmek", "yaşamak istemiyorum", "bitirmek istiyorum",
    "son yolculuk", "veda", "artık yeter", "çıkış yok",
  ],
  high: [
    "umutsuz", "çaresiz", "hiçbir şey iyi gitmiyor", "değersizim",
    "kimse beni sevmiyor", "yalnızım", "kimse yok", "herkes benden nefret ediyor",
  ],
  medium: [
    "depresyon", "kaygı", "panik", "korku", "endişe",
    "uyuyamıyorum", "yemek yiyemiyorum", "hiçbir şey yapmak istemiyorum",
  ],
};

/**
 * Detect risk keywords in transcript
 */
function detectRiskKeywords(transcript: string): RiskSignal[] {
  const signals: RiskSignal[] = [];
  const lowerTranscript = transcript.toLowerCase();

  // Check critical keywords
  for (const keyword of RISK_KEYWORDS.critical) {
    if (lowerTranscript.includes(keyword)) {
      signals.push({
        type: "keyword",
        severity: "critical",
        description: `Critical risk keyword detected: "${keyword}"`,
        confidence: 0.9,
        source: keyword,
      });
    }
  }

  // Check high-risk keywords
  for (const keyword of RISK_KEYWORDS.high) {
    if (lowerTranscript.includes(keyword)) {
      signals.push({
        type: "keyword",
        severity: "high",
        description: `High-risk keyword detected: "${keyword}"`,
        confidence: 0.75,
        source: keyword,
      });
    }
  }

  // Check medium-risk keywords
  for (const keyword of RISK_KEYWORDS.medium) {
    if (lowerTranscript.includes(keyword)) {
      signals.push({
        type: "keyword",
        severity: "medium",
        description: `Medium-risk keyword detected: "${keyword}"`,
        confidence: 0.6,
        source: keyword,
      });
    }
  }

  return signals;
}

/**
 * Detect risk from emotions
 */
function detectRiskFromEmotions(emotions: EmotionScores): RiskSignal[] {
  const signals: RiskSignal[] = [];

  // High sadness + low hope = risk
  if (emotions.sadness > 0.8 && emotions.hope < 0.2) {
    signals.push({
      type: "emotion",
      severity: "high",
      description: "Very high sadness combined with low hope",
      confidence: 0.8,
      source: `sadness:${emotions.sadness.toFixed(2)}, hope:${emotions.hope.toFixed(2)}`,
    });
  }

  // High fear + high anxiety = risk
  if (emotions.fear > 0.8 && emotions.anxiety > 0.8) {
    signals.push({
      type: "emotion",
      severity: "medium",
      description: "High fear and anxiety levels",
      confidence: 0.7,
      source: `fear:${emotions.fear.toFixed(2)}, anxiety:${emotions.anxiety.toFixed(2)}`,
    });
  }

  // Very negative overall mood = risk
  if (emotions.overallMood < -0.7) {
    signals.push({
      type: "emotion",
      severity: "high",
      description: "Very negative overall mood",
      confidence: 0.75,
      source: `overallMood:${emotions.overallMood.toFixed(2)}`,
    });
  }

  return signals;
}

/**
 * Detect risk from audio features
 */
function detectRiskFromAudio(features: AudioFeatures): RiskSignal[] {
  const signals: RiskSignal[] = [];

  // Very low pitch + very slow tempo = potential depression
  if (features.pitch < 100 && features.tempo < 80) {
    signals.push({
      type: "audio",
      severity: "medium",
      description: "Very low pitch and slow speech rate (potential depression indicator)",
      confidence: 0.65,
      source: `pitch:${features.pitch.toFixed(0)}Hz, tempo:${features.tempo.toFixed(0)}wpm`,
    });
  }

  // High pitch variation + frequent pauses = anxiety/stress
  if (features.pitchVariation > 35 && features.pauseFrequency > 12) {
    signals.push({
      type: "audio",
      severity: "medium",
      description: "High pitch variation and frequent pauses (anxiety indicator)",
      confidence: 0.6,
      source: `pitchVariation:${features.pitchVariation.toFixed(1)}, pauses:${features.pauseFrequency.toFixed(1)}/min`,
    });
  }

  return signals;
}

/**
 * AI-based risk pattern detection
 */
async function detectRiskPatterns(
  request: HIPAACompliantAIRequest & {
    transcript: string;
  }
): Promise<RiskSignal[]> {
  const result = await processWithAI(request, async (deidentifiedTranscript) => {
    const orchestrator = getAIOrchestrator();
    
    const prompt = `Analyze this therapy session transcript for risk indicators. Look for:
1. Suicide ideation or self-harm thoughts
2. Severe depression or hopelessness
3. Violence or harm to others
4. Substance abuse or dangerous behaviors

Transcript:
${deidentifiedTranscript}

Return JSON array of risk signals:
[
  {
    "type": "pattern",
    "severity": "critical|high|medium|low",
    "description": "Risk description",
    "confidence": 0.0-1.0,
    "source": "pattern identifier"
  }
]

Only return signals if there is genuine concern. Be conservative to avoid false positives.`;

    const response = await orchestrator.processWithGemini(prompt);
    
    try {
      const jsonMatch = response.match(/\[[\s\S]*\]/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]) as RiskSignal[];
      }
      return [];
    } catch (error) {
      console.error("Failed to parse risk pattern detection:", error);
      return [];
    }
  });

  if (!result.success || !result.result) {
    return [];
  }

  return result.result as RiskSignal[];
}

/**
 * Calculate risk score from signals
 */
function calculateRiskScore(signals: RiskSignal[]): {
  riskLevel: RiskLevel;
  riskScore: number;
  confidence: number;
} {
  if (signals.length === 0) {
    return {
      riskLevel: "low",
      riskScore: 0,
      confidence: 1.0,
    };
  }

  // Weight signals by severity
  const weights = {
    critical: 100,
    high: 70,
    medium: 40,
    low: 10,
  };

  // Calculate weighted score
  let totalScore = 0;
  let totalWeight = 0;
  let maxSeverity: RiskLevel = "low";

  for (const signal of signals) {
    const weight = weights[signal.severity];
    const weightedScore = weight * signal.confidence;
    totalScore += weightedScore;
    totalWeight += weight;

    // Track highest severity
    const severityOrder: RiskLevel[] = ["low", "medium", "high", "critical"];
    if (severityOrder.indexOf(signal.severity) > severityOrder.indexOf(maxSeverity)) {
      maxSeverity = signal.severity;
    }
  }

  const riskScore = totalWeight > 0 ? Math.min(100, (totalScore / totalWeight) * 100) : 0;
  
  // Determine risk level
  let riskLevel: RiskLevel;
  if (riskScore >= 80) {
    riskLevel = "critical";
  } else if (riskScore >= 60) {
    riskLevel = "high";
  } else if (riskScore >= 30) {
    riskLevel = "medium";
  } else {
    riskLevel = "low";
  }

  // Overall confidence (average of signal confidences)
  const avgConfidence = signals.reduce((sum, s) => sum + s.confidence, 0) / signals.length;

  return {
    riskLevel,
    riskScore,
    confidence: avgConfidence,
  };
}

/**
 * Multi-signal risk detection
 * CRITICAL: False positive reduction through multiple signals
 */
export async function detectRiskMultiSignal(
  request: HIPAACompliantAIRequest & {
    transcript: string;
    emotions?: EmotionScores;
    audioFeatures?: AudioFeatures;
  }
): Promise<RiskDetectionResult> {
  const signals: RiskSignal[] = [];

  // 1. Keyword detection
  const keywordSignals = detectRiskKeywords(request.transcript);
  signals.push(...keywordSignals);

  // 2. Emotion-based detection
  let emotions: EmotionScores;
  if (request.emotions) {
    emotions = request.emotions;
  } else {
    // Detect emotions if not provided
    const emotionResult = await detectEmotionsHybrid({
      ...request,
      transcript: request.transcript,
      audioFeatures: request.audioFeatures,
    });
    emotions = emotionResult.emotions;
  }

  const emotionSignals = detectRiskFromEmotions(emotions);
  signals.push(...emotionSignals);

  // 3. Audio feature detection
  if (request.audioFeatures) {
    const audioSignals = detectRiskFromAudio(request.audioFeatures);
    signals.push(...audioSignals);
  }

  // 4. AI pattern detection (only if other signals exist)
  if (signals.length > 0 || request.transcript.length > 100) {
    const patternSignals = await detectRiskPatterns({
      ...request,
      transcript: request.transcript,
    });
    signals.push(...patternSignals);
  }

  // Calculate risk score
  const { riskLevel, riskScore, confidence } = calculateRiskScore(signals);

  // False positive reduction: Require multiple signals for high/critical risk
  let finalRiskLevel = riskLevel;
  let finalRiskScore = riskScore;
  let requiresImmediateAttention = false;

  if (riskLevel === "critical") {
    // Critical risk requires at least 2 signals OR 1 critical keyword
    const criticalSignals = signals.filter((s) => s.severity === "critical");
    const criticalKeywords = signals.filter((s) => s.type === "keyword" && s.severity === "critical");
    
    if (criticalKeywords.length === 0 && signals.length < 2) {
      // Downgrade to high if insufficient signals
      finalRiskLevel = "high";
      finalRiskScore = Math.min(79, riskScore);
    } else {
      requiresImmediateAttention = true;
    }
  } else if (riskLevel === "high") {
    // High risk requires at least 2 signals
    if (signals.length < 2) {
      finalRiskLevel = "medium";
      finalRiskScore = Math.min(59, riskScore);
    }
  }

  // Generate recommendations
  const recommendations = generateRecommendations(finalRiskLevel, signals);

  return {
    riskLevel: finalRiskLevel,
    riskScore: finalRiskScore,
    signals,
    confidence,
    requiresImmediateAttention,
    recommendations,
    timestamp: Date.now(),
  };
}

/**
 * Generate recommendations based on risk level
 */
function generateRecommendations(riskLevel: RiskLevel, signals: RiskSignal[]): string[] {
  const recommendations: string[] = [];

  if (riskLevel === "critical") {
    recommendations.push("🚨 ACİL DURUM: Hemen müdahale gerekiyor");
    recommendations.push("Acil servisleri arayın veya kriz hattını kullanın");
    recommendations.push("Hastayı yalnız bırakmayın");
    recommendations.push("Durumu dokümente edin ve süpervizöre bildirin");
  } else if (riskLevel === "high") {
    recommendations.push("Yüksek risk tespit edildi - dikkatli olun");
    recommendations.push("Sonraki seansta konuyu derinlemesine ele alın");
    recommendations.push("Hastayla iletişim kurun ve destek sağlayın");
    recommendations.push("Durumu süpervizöre bildirin");
  } else if (riskLevel === "medium") {
    recommendations.push("Orta risk seviyesi - izleme gerekiyor");
    recommendations.push("Sonraki seansta konuyu ele alın");
    recommendations.push("Hastanın durumunu takip edin");
  } else {
    recommendations.push("Düşük risk seviyesi - normal takip");
  }

  return recommendations;
}






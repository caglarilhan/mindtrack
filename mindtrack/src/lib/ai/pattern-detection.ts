/**
 * Pattern Detection Engine
 * Privacy-preserving pattern detection for session analysis
 */

import { processWithAI, type HIPAACompliantAIRequest } from "./hipaa-compliant-processor";
import { getAIOrchestrator } from "./orchestrator";

export interface Pattern {
  type: "repetitive_topic" | "symptom_trend" | "relationship_change" | "mood_pattern" | "other";
  description: string;
  confidence: number; // 0-1
  detectedAt: Date;
  sessions: string[]; // Session IDs where pattern was detected
  metadata?: Record<string, unknown>;
}

export interface PatternDetectionResult {
  patterns: Pattern[];
  summary: string;
  recommendations?: string[];
}

/**
 * Detect patterns across multiple sessions
 * HIPAA-compliant: Uses de-identified data
 */
export async function detectPatterns(
  request: HIPAACompliantAIRequest & {
    sessionIds: string[];
    sessionData: Array<{ id: string; transcript: string; date: string }>;
  }
): Promise<PatternDetectionResult> {
  // Combine session data
  const combinedData = request.sessionData
    .map((session) => `Session ${session.id} (${session.date}): ${session.transcript}`)
    .join("\n\n");

  // Process with AI (de-identified)
  const result = await processWithAI(
    {
      ...request,
      data: combinedData,
    },
    async (deidentifiedData) => {
      const orchestrator = getAIOrchestrator();
      
      const prompt = `Analyze the following therapy sessions and detect patterns. Look for:
1. Repetitive topics (patient keeps returning to same issue)
2. Symptom trends (improving or worsening symptoms)
3. Relationship changes (changes in relationship dynamics)
4. Mood patterns (mood fluctuations over time)

Sessions:
${deidentifiedData}

Return a JSON object with:
- patterns: array of detected patterns with type, description, confidence (0-1), and relevant session IDs
- summary: overall summary of patterns detected
- recommendations: optional recommendations for therapist

Format:
{
  "patterns": [
    {
      "type": "repetitive_topic",
      "description": "Patient repeatedly discusses work stress",
      "confidence": 0.85,
      "sessions": ["session1", "session2"]
    }
  ],
  "summary": "Overall pattern summary",
  "recommendations": ["Recommendation 1", "Recommendation 2"]
}`;

      const response = await orchestrator.processWithGemini(prompt);
      
      try {
        // Extract JSON from response
        const jsonMatch = response.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          return JSON.parse(jsonMatch[0]) as PatternDetectionResult;
        }
        throw new Error("No JSON found in response");
      } catch (error) {
        console.error("Failed to parse pattern detection response:", error);
        // Return fallback
        return {
          patterns: [],
          summary: "Pattern detection completed but parsing failed",
        };
      }
    }
  );

  if (!result.success || !result.result) {
    return {
      patterns: [],
      summary: "Pattern detection failed",
    };
  }

  const detectionResult = result.result as PatternDetectionResult;

  // Add detectedAt timestamps
  detectionResult.patterns = detectionResult.patterns.map((pattern) => ({
    ...pattern,
    detectedAt: new Date(),
  }));

  return detectionResult;
}

/**
 * Detect repetitive topics
 */
export async function detectRepetitiveTopics(
  request: HIPAACompliantAIRequest & {
    sessionData: Array<{ id: string; transcript: string }>;
  }
): Promise<Pattern[]> {
  const result = await detectPatterns({
    ...request,
    sessionIds: request.sessionData.map((s) => s.id),
    sessionData: request.sessionData.map((s) => ({
      id: s.id,
      transcript: s.transcript,
      date: new Date().toISOString(),
    })),
  });

  return result.patterns.filter((p) => p.type === "repetitive_topic");
}

/**
 * Detect symptom trends
 */
export async function detectSymptomTrends(
  request: HIPAACompliantAIRequest & {
    sessionData: Array<{ id: string; transcript: string; date: string }>;
  }
): Promise<Pattern[]> {
  const result = await detectPatterns({
    ...request,
    sessionIds: request.sessionData.map((s) => s.id),
    sessionData: request.sessionData,
  });

  return result.patterns.filter((p) => p.type === "symptom_trend");
}






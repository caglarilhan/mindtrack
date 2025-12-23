/**
 * Emotional Journey Mapping
 * Tracks emotional progression over time
 */

import { processWithAI, type HIPAACompliantAIRequest } from "./hipaa-compliant-processor";
import { getAIOrchestrator } from "./orchestrator";

export interface EmotionPoint {
  date: string;
  sessionId: string;
  emotions: {
    sadness: number; // 0-1
    anxiety: number;
    anger: number;
    happiness: number;
    fear: number;
    hope: number;
  };
  overallMood: number; // -1 (very negative) to 1 (very positive)
  triggerEvents?: string[];
}

export interface EmotionalJourney {
  points: EmotionPoint[];
  trends: {
    overall: "improving" | "declining" | "stable" | "fluctuating";
    description: string;
  };
  triggerEvents: Array<{
    date: string;
    description: string;
    impact: "positive" | "negative" | "neutral";
  }>;
  recommendations?: string[];
}

/**
 * Map emotional journey from sessions
 */
export async function mapEmotionalJourney(
  request: HIPAACompliantAIRequest & {
    sessionData: Array<{ id: string; transcript: string; date: string }>;
  }
): Promise<EmotionalJourney> {
  // Sort sessions by date
  const sortedSessions = [...request.sessionData].sort(
    (a, b) => new Date(a.date).getTime() - new Date(b.date).getTime()
  );

  // Combine session data with dates
  const combinedData = sortedSessions
    .map((session) => `Date: ${session.date}\nSession: ${session.transcript}`)
    .join("\n\n---\n\n");

  // Process with AI
  const result = await processWithAI(
    {
      ...request,
      data: combinedData,
    },
    async (deidentifiedData) => {
      const orchestrator = getAIOrchestrator();
      
      const prompt = `Analyze the emotional journey across these therapy sessions. For each session, extract:
1. Emotions: sadness, anxiety, anger, happiness, fear, hope (0-1 scale)
2. Overall mood: -1 (very negative) to 1 (very positive)
3. Trigger events: significant events mentioned

Sessions:
${deidentifiedData}

Return JSON:
{
  "points": [
    {
      "date": "2024-01-01",
      "sessionId": "session1",
      "emotions": {
        "sadness": 0.7,
        "anxiety": 0.8,
        "anger": 0.2,
        "happiness": 0.1,
        "fear": 0.6,
        "hope": 0.3
      },
      "overallMood": -0.5,
      "triggerEvents": ["Work stress", "Family conflict"]
    }
  ],
  "trends": {
    "overall": "improving",
    "description": "Overall emotional state is improving over time"
  },
  "triggerEvents": [
    {
      "date": "2024-01-15",
      "description": "Job loss",
      "impact": "negative"
    }
  ],
  "recommendations": ["Focus on coping strategies", "Address work-related stress"]
}`;

      const response = await orchestrator.processWithGemini(prompt);
      
      try {
        const jsonMatch = response.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          return JSON.parse(jsonMatch[0]) as EmotionalJourney;
        }
        throw new Error("No JSON found in response");
      } catch (error) {
        console.error("Failed to parse emotional journey response:", error);
        return {
          points: [],
          trends: {
            overall: "stable",
            description: "Analysis completed but parsing failed",
          },
          triggerEvents: [],
        };
      }
    }
  );

  if (!result.success || !result.result) {
    return {
      points: [],
      trends: {
        overall: "stable",
        description: "Emotional journey mapping failed",
      },
      triggerEvents: [],
    };
  }

  return result.result as EmotionalJourney;
}

/**
 * Get emotional trend summary
 */
export function getEmotionalTrendSummary(journey: EmotionalJourney): string {
  if (journey.points.length === 0) {
    return "No emotional data available";
  }

  const firstMood = journey.points[0].overallMood;
  const lastMood = journey.points[journey.points.length - 1].overallMood;
  const change = lastMood - firstMood;

  if (change > 0.3) {
    return "Significant improvement in emotional state";
  } else if (change < -0.3) {
    return "Significant decline in emotional state";
  } else if (change > 0.1) {
    return "Moderate improvement in emotional state";
  } else if (change < -0.1) {
    return "Moderate decline in emotional state";
  } else {
    return "Stable emotional state";
  }
}






/**
 * Session Quality Score
 * Evaluates session quality based on engagement and effectiveness
 */

import { processWithAI, type HIPAACompliantAIRequest } from "./hipaa-compliant-processor";
import { getAIOrchestrator } from "./orchestrator";

export interface SessionQualityMetrics {
  patientEngagement: number; // 0-1
  therapistIntervention: number; // 0-1
  progressIndicators: number; // 0-1
  overallScore: number; // 0-1
  breakdown: {
    patientParticipation: number;
    therapistEffectiveness: number;
    sessionStructure: number;
    therapeuticAlliance: number;
  };
  feedback: {
    strengths: string[];
    areasForImprovement: string[];
  };
}

/**
 * Calculate session quality score
 */
export async function calculateSessionQuality(
  request: HIPAACompliantAIRequest & {
    transcript: string;
    sessionDuration?: number; // in minutes
  }
): Promise<SessionQualityMetrics> {
  const result = await processWithAI(
    request,
    async (deidentifiedData) => {
      const orchestrator = getAIOrchestrator();
      
      const prompt = `Analyze this therapy session transcript and calculate quality metrics.

Session Transcript:
${deidentifiedData}

${request.sessionDuration ? `Session Duration: ${request.sessionDuration} minutes` : ""}

Evaluate:
1. Patient Engagement (0-1): How engaged was the patient? Did they participate actively?
2. Therapist Intervention (0-1): How effective were therapist interventions?
3. Progress Indicators (0-1): Are there signs of progress or positive change?
4. Breakdown:
   - Patient Participation (0-1)
   - Therapist Effectiveness (0-1)
   - Session Structure (0-1)
   - Therapeutic Alliance (0-1)

Return JSON:
{
  "patientEngagement": 0.8,
  "therapistIntervention": 0.75,
  "progressIndicators": 0.7,
  "overallScore": 0.75,
  "breakdown": {
    "patientParticipation": 0.8,
    "therapistEffectiveness": 0.75,
    "sessionStructure": 0.7,
    "therapeuticAlliance": 0.8
  },
  "feedback": {
    "strengths": ["Patient was very open", "Good rapport"],
    "areasForImprovement": ["Could explore deeper", "More structure needed"]
  }
}`;

      const response = await orchestrator.processWithGemini(prompt);
      
      try {
        const jsonMatch = response.match(/\{[\s\S]*\}/);
        if (jsonMatch) {
          const parsed = JSON.parse(jsonMatch[0]) as SessionQualityMetrics;
          
          // Calculate overall score if not provided
          if (!parsed.overallScore) {
            parsed.overallScore = (
              parsed.patientEngagement +
              parsed.therapistIntervention +
              parsed.progressIndicators
            ) / 3;
          }
          
          return parsed;
        }
        throw new Error("No JSON found in response");
      } catch (error) {
        console.error("Failed to parse session quality response:", error);
        return {
          patientEngagement: 0.5,
          therapistIntervention: 0.5,
          progressIndicators: 0.5,
          overallScore: 0.5,
          breakdown: {
            patientParticipation: 0.5,
            therapistEffectiveness: 0.5,
            sessionStructure: 0.5,
            therapeuticAlliance: 0.5,
          },
          feedback: {
            strengths: [],
            areasForImprovement: ["Analysis failed"],
          },
        };
      }
    }
  );

  if (!result.success || !result.result) {
    return {
      patientEngagement: 0.5,
      therapistIntervention: 0.5,
      progressIndicators: 0.5,
      overallScore: 0.5,
      breakdown: {
        patientParticipation: 0.5,
        therapistEffectiveness: 0.5,
        sessionStructure: 0.5,
        therapeuticAlliance: 0.5,
      },
      feedback: {
        strengths: [],
        areasForImprovement: ["Quality calculation failed"],
      },
    };
  }

  return result.result as SessionQualityMetrics;
}

/**
 * Get quality score label
 */
export function getQualityScoreLabel(score: number): {
  label: string;
  color: string;
  description: string;
} {
  if (score >= 0.8) {
    return {
      label: "Excellent",
      color: "green",
      description: "High-quality session with strong engagement and progress",
    };
  } else if (score >= 0.6) {
    return {
      label: "Good",
      color: "blue",
      description: "Good session with solid engagement and some progress",
    };
  } else if (score >= 0.4) {
    return {
      label: "Fair",
      color: "yellow",
      description: "Adequate session but could benefit from more engagement",
    };
  } else {
    return {
      label: "Needs Improvement",
      color: "red",
      description: "Session quality below expectations, review recommended",
    };
  }
}






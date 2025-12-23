/**
 * Emotion Detection Engine
 * Hybrid model: Transcript-based + Audio feature-based emotion detection
 */

import { processWithAI, type HIPAACompliantAIRequest } from "./hipaa-compliant-processor";
import { getAIOrchestrator } from "./orchestrator";
import { extractEmotionIndicators, type AudioFeatures } from "../audio/audio-features";

export interface EmotionScores {
  sadness: number; // 0-1
  anxiety: number;
  anger: number;
  happiness: number;
  fear: number;
  hope: number;
  overallMood: number; // -1 (very negative) to 1 (very positive)
}

export interface EmotionDetectionResult {
  emotions: EmotionScores;
  confidence: number; // 0-1
  source: "transcript" | "audio" | "hybrid";
  timestamp: number;
  metadata?: {
    transcriptLength?: number;
    audioFeatures?: AudioFeatures;
  };
}

/**
 * Detect emotions from transcript (AI-based)
 */
export async function detectEmotionsFromTranscript(
  request: HIPAACompliantAIRequest & {
    transcript: string;
  }
): Promise<EmotionScores> {
  const result = await processWithAI(request, async (deidentifiedTranscript) => {
    const orchestrator = getAIOrchestrator();
    
    const prompt = `Analyze the emotional state from this therapy session transcript. Return a JSON object with emotion scores (0-1) and overall mood (-1 to 1).

Transcript:
${deidentifiedTranscript}

Return JSON:
{
  "sadness": 0.0-1.0,
  "anxiety": 0.0-1.0,
  "anger": 0.0-1.0,
  "happiness": 0.0-1.0,
  "fear": 0.0-1.0,
  "hope": 0.0-1.0,
  "overallMood": -1.0 to 1.0
}`;

    const response = await orchestrator.processWithGemini(prompt);
    
    try {
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        const parsed = JSON.parse(jsonMatch[0]) as EmotionScores;
        
        // Validate and normalize scores
        return {
          sadness: Math.max(0, Math.min(1, parsed.sadness || 0)),
          anxiety: Math.max(0, Math.min(1, parsed.anxiety || 0)),
          anger: Math.max(0, Math.min(1, parsed.anger || 0)),
          happiness: Math.max(0, Math.min(1, parsed.happiness || 0)),
          fear: Math.max(0, Math.min(1, parsed.fear || 0)),
          hope: Math.max(0, Math.min(1, parsed.hope || 0)),
          overallMood: Math.max(-1, Math.min(1, parsed.overallMood || 0)),
        };
      }
      throw new Error("No JSON found in response");
    } catch (error) {
      console.error("Failed to parse emotion detection response:", error);
      // Return neutral scores
      return {
        sadness: 0.5,
        anxiety: 0.5,
        anger: 0.5,
        happiness: 0.5,
        fear: 0.5,
        hope: 0.5,
        overallMood: 0,
      };
    }
  });

  if (!result.success || !result.result) {
    // Return neutral scores on error
    return {
      sadness: 0.5,
      anxiety: 0.5,
      anger: 0.5,
      happiness: 0.5,
      fear: 0.5,
      hope: 0.5,
      overallMood: 0,
    };
  }

  return result.result as EmotionScores;
}

/**
 * Detect emotions from audio features
 */
export function detectEmotionsFromAudio(features: AudioFeatures): EmotionScores {
  const audioEmotions = extractEmotionIndicators(features);
  
  // Convert to full EmotionScores format
  return {
    sadness: audioEmotions.sadness,
    anxiety: audioEmotions.anxiety,
    anger: audioEmotions.anger,
    happiness: audioEmotions.happiness,
    fear: audioEmotions.fear,
    hope: 0.5, // Audio features don't provide hope score
    overallMood: calculateOverallMoodFromAudio(features),
  };
}

/**
 * Calculate overall mood from audio features
 */
function calculateOverallMoodFromAudio(features: AudioFeatures): number {
  // Simplified mood calculation based on audio features
  // Low pitch + slow tempo = negative mood
  // High pitch + fast tempo = positive mood
  
  const pitchScore = (features.pitch - 85) / (255 - 85); // Normalize to 0-1
  const tempoScore = Math.min(features.tempo / 200, 1); // Normalize to 0-1
  
  // Combine scores (-1 to 1)
  const mood = (pitchScore * 0.6 + tempoScore * 0.4) * 2 - 1;
  
  return Math.max(-1, Math.min(1, mood));
}

/**
 * Hybrid emotion detection (transcript + audio)
 */
export async function detectEmotionsHybrid(
  request: HIPAACompliantAIRequest & {
    transcript: string;
    audioFeatures?: AudioFeatures;
  }
): Promise<EmotionDetectionResult> {
  const transcriptEmotions = await detectEmotionsFromTranscript({
    ...request,
    transcript: request.transcript,
  });

  let audioEmotions: EmotionScores | null = null;
  let audioFeatures: AudioFeatures | undefined = request.audioFeatures;

  if (audioFeatures) {
    audioEmotions = detectEmotionsFromAudio(audioFeatures);
  }

  // Combine emotions (weighted average)
  // Transcript: 70% weight (more reliable)
  // Audio: 30% weight (supplementary)
  const weights = {
    transcript: 0.7,
    audio: 0.3,
  };

  let finalEmotions: EmotionScores;
  let confidence: number;
  let source: "transcript" | "audio" | "hybrid";

  if (audioEmotions && audioFeatures) {
    // Hybrid: Combine both
    finalEmotions = {
      sadness: transcriptEmotions.sadness * weights.transcript + audioEmotions.sadness * weights.audio,
      anxiety: transcriptEmotions.anxiety * weights.transcript + audioEmotions.anxiety * weights.audio,
      anger: transcriptEmotions.anger * weights.transcript + audioEmotions.anger * weights.audio,
      happiness: transcriptEmotions.happiness * weights.transcript + audioEmotions.happiness * weights.audio,
      fear: transcriptEmotions.fear * weights.transcript + audioEmotions.fear * weights.audio,
      hope: transcriptEmotions.hope, // Hope only from transcript
      overallMood: transcriptEmotions.overallMood * weights.transcript + audioEmotions.overallMood * weights.audio,
    };
    
    // Higher confidence with both sources
    confidence = 0.85;
    source = "hybrid";
  } else {
    // Transcript only
    finalEmotions = transcriptEmotions;
    confidence = 0.75;
    source = "transcript";
  }

  // Normalize scores
  finalEmotions = {
    sadness: Math.max(0, Math.min(1, finalEmotions.sadness)),
    anxiety: Math.max(0, Math.min(1, finalEmotions.anxiety)),
    anger: Math.max(0, Math.min(1, finalEmotions.anger)),
    happiness: Math.max(0, Math.min(1, finalEmotions.happiness)),
    fear: Math.max(0, Math.min(1, finalEmotions.fear)),
    hope: Math.max(0, Math.min(1, finalEmotions.hope)),
    overallMood: Math.max(-1, Math.min(1, finalEmotions.overallMood)),
  };

  return {
    emotions: finalEmotions,
    confidence,
    source,
    timestamp: Date.now(),
    metadata: {
      transcriptLength: request.transcript.length,
      audioFeatures,
    },
  };
}

/**
 * Get dominant emotion
 */
export function getDominantEmotion(emotions: EmotionScores): {
  emotion: keyof Omit<EmotionScores, "overallMood">;
  score: number;
} {
  const emotionScores = {
    sadness: emotions.sadness,
    anxiety: emotions.anxiety,
    anger: emotions.anger,
    happiness: emotions.happiness,
    fear: emotions.fear,
    hope: emotions.hope,
  };

  const entries = Object.entries(emotionScores) as Array<[keyof typeof emotionScores, number]>;
  const [dominantEmotion, score] = entries.reduce((max, [emotion, value]) => {
    return value > max[1] ? [emotion, value] : max;
  }, entries[0]);

  return {
    emotion: dominantEmotion,
    score,
  };
}

/**
 * Get emotion label
 */
export function getEmotionLabel(emotion: keyof Omit<EmotionScores, "overallMood">): string {
  const labels: Record<keyof Omit<EmotionScores, "overallMood">, string> = {
    sadness: "Üzgün",
    anxiety: "Kaygılı",
    anger: "Öfkeli",
    happiness: "Mutlu",
    fear: "Korkulu",
    hope: "Umutlu",
  };

  return labels[emotion] || emotion;
}






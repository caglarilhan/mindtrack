/**
 * Voice Emotion Analysis API
 * HIPAA-compliant real-time emotion and risk analysis
 */

import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";
import { detectEmotionsHybrid } from "@/lib/ai/emotion-detection";
import { detectRiskMultiSignal } from "@/lib/risk/voice-risk-detection";
import { logDataAccess, logDataModification } from "@/lib/hipaa/audit-log";
import { hasAccess } from "@/lib/hipaa/access-control";
import type { AudioFeatures } from "@/lib/audio/audio-features";
import type { EmotionScores } from "@/lib/ai/emotion-detection";

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const {
      clientId,
      sessionId,
      transcript,
      audioFeatures,
      emotions, // Optional: pre-calculated emotions
      includeRiskAnalysis = true,
    } = body;

    if (!clientId || !transcript) {
      return NextResponse.json(
        { error: "clientId and transcript are required" },
        { status: 400 }
      );
    }

    const ipAddress = request.headers.get("x-forwarded-for") || undefined;
    const userAgent = request.headers.get("user-agent") || undefined;

    // Check access
    const hasAccessToClient = await hasAccess(user.id, "clients", "read", clientId);
    if (!hasAccessToClient) {
      await logDataAccess(user.id, "clients", clientId, ipAddress, userAgent, false);
      return NextResponse.json({ error: "Access denied" }, { status: 403 });
    }

    // Log access
    await logDataAccess(user.id, "clients", clientId, ipAddress, userAgent, true);

    // Detect emotions
    const emotionResult = emotions
      ? { emotions: emotions as EmotionScores, confidence: 0.8, source: "provided" as const, timestamp: Date.now() }
      : await detectEmotionsHybrid({
          userId: user.id,
          resourceType: "clients",
          resourceId: clientId,
          ipAddress,
          userAgent,
          transcript,
          audioFeatures: audioFeatures as AudioFeatures | undefined,
        });

    // Detect risk (if requested)
    let riskResult = null;
    if (includeRiskAnalysis) {
      riskResult = await detectRiskMultiSignal({
        userId: user.id,
        resourceType: "clients",
        resourceId: clientId,
        ipAddress,
        userAgent,
        transcript,
        emotions: emotionResult.emotions,
        audioFeatures: audioFeatures as AudioFeatures | undefined,
      });

      // Log risk detection
      if (riskResult.riskLevel !== "low") {
        await logDataModification(
          user.id,
          "create",
          "risk_detection",
          sessionId || clientId,
          ipAddress,
          userAgent,
          true,
          {
            riskLevel: riskResult.riskLevel,
            riskScore: riskResult.riskScore,
            signalsCount: riskResult.signals.length,
          }
        );
      }
    }

    // Log emotion analysis
    await logDataModification(
      user.id,
      "create",
      "emotion_analysis",
      sessionId || clientId,
      ipAddress,
      userAgent,
      true,
      {
        dominantEmotion: Object.entries(emotionResult.emotions)
          .filter(([key]) => key !== "overallMood")
          .reduce((max, [emotion, score]) => {
            return score > max[1] ? [emotion, score] : max;
          }, ["", 0])[0],
        overallMood: emotionResult.emotions.overallMood,
      }
    );

    return NextResponse.json({
      success: true,
      clientId,
      sessionId,
      emotions: emotionResult.emotions,
      emotionConfidence: emotionResult.confidence,
      emotionSource: emotionResult.source,
      risk: riskResult,
      timestamp: new Date().toISOString(),
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Voice emotion analysis error:", error);
    return NextResponse.json(
      {
        error: "Failed to analyze emotions",
        details: errorMessage,
      },
      { status: 500 }
    );
  }
}






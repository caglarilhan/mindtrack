/**
 * AI Session Insights API
 * HIPAA-compliant session analysis
 */

import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";
import { detectPatterns } from "@/lib/ai/pattern-detection";
import { mapEmotionalJourney } from "@/lib/ai/emotional-journey";
import { calculateSessionQuality } from "@/lib/ai/session-quality";
import { validateAIRequest } from "@/lib/ai/hipaa-compliant-processor";
import { logDataAccess } from "@/lib/hipaa/audit-log";

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
      sessionIds,
      analysisType, // "patterns" | "emotional_journey" | "quality" | "all"
      sessionId, // For quality analysis
      transcript, // For quality analysis
      sessionDuration,
    } = body;

    if (!clientId) {
      return NextResponse.json({ error: "clientId is required" }, { status: 400 });
    }

    const ipAddress = request.headers.get("x-forwarded-for") || undefined;
    const userAgent = request.headers.get("user-agent") || undefined;

    // Log access
    await logDataAccess(user.id, "clients", clientId, ipAddress, userAgent, true);

    // Get session data
    let sessionData: Array<{ id: string; transcript: string; date: string }> = [];

    if (sessionIds && sessionIds.length > 0) {
      const { data: sessions, error: sessionsError } = await supabase
        .from("session_notes")
        .select("id, soap_subjective, created_at")
        .in("id", sessionIds)
        .eq("client_id", clientId)
        .order("created_at", { ascending: true });

      if (sessionsError) {
        return NextResponse.json(
          { error: "Failed to fetch sessions", details: sessionsError.message },
          { status: 500 }
        );
      }

      sessionData = (sessions || []).map((session) => ({
        id: session.id,
        transcript: session.soap_subjective || "",
        date: session.created_at,
      }));
    }

    const aiRequest = {
      userId: user.id,
      resourceType: "clients",
      resourceId: clientId,
      ipAddress,
      userAgent,
      sessionIds: sessionIds || [],
      sessionData,
    };

    // Validate request
    const validation = validateAIRequest(aiRequest);
    if (!validation.valid) {
      return NextResponse.json(
        { error: "Invalid request", details: validation.errors },
        { status: 400 }
      );
    }

    const results: Record<string, unknown> = {};

    // Pattern Detection
    if (analysisType === "patterns" || analysisType === "all") {
      if (sessionData.length > 0) {
        const patterns = await detectPatterns(aiRequest);
        results.patterns = patterns;
      }
    }

    // Emotional Journey
    if (analysisType === "emotional_journey" || analysisType === "all") {
      if (sessionData.length > 0) {
        const journey = await mapEmotionalJourney(aiRequest);
        results.emotionalJourney = journey;
      }
    }

    // Session Quality
    if (analysisType === "quality" || analysisType === "all") {
      if (transcript && sessionId) {
        const quality = await calculateSessionQuality({
          ...aiRequest,
          transcript,
          sessionDuration,
        });
        results.quality = quality;
      } else if (sessionData.length > 0) {
        // Use latest session
        const latestSession = sessionData[sessionData.length - 1];
        const quality = await calculateSessionQuality({
          ...aiRequest,
          transcript: latestSession.transcript,
          sessionDuration,
        });
        results.quality = quality;
      }
    }

    return NextResponse.json({
      success: true,
      clientId,
      analysisType,
      results,
      timestamp: new Date().toISOString(),
    });
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Session insights API error:", error);
    return NextResponse.json(
      {
        error: "Failed to generate session insights",
        details: errorMessage,
      },
      { status: 500 }
    );
  }
}






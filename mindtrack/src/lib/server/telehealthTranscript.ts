import { createClient } from "@supabase/supabase-js";
import type { TranscriptSegment, RiskTickerEvent } from "./telehealthRiskTicker";
import { analyzeTranscriptSegment, processTranscriptStream } from "./telehealthRiskTicker";

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

function getAdminClient() {
  if (!SUPABASE_URL || !SERVICE_ROLE_KEY) {
    return null;
  }
  return createClient(SUPABASE_URL, SERVICE_ROLE_KEY, {
    auth: { autoRefreshToken: false, persistSession: false },
  });
}

export interface TranscriptSnippet {
  sessionId: string;
  speaker: "patient" | "provider" | "caregiver" | "system";
  snippet: string;
  startTime: number;
  endTime: number;
  riskTags?: string[];
  sentimentScore?: number;
}

export async function saveTranscriptSnippet(input: TranscriptSnippet, region: "us" | "eu" = "us") {
  const adminClient = getAdminClient();
  if (!adminClient) {
    throw new Error("Service role client unavailable");
  }

  const segment: TranscriptSegment = {
    timestamp: input.startTime,
    speaker: input.speaker === "caregiver" ? "patient" : input.speaker,
    text: input.snippet,
    duration: input.endTime - input.startTime,
  };

  const risk = analyzeTranscriptSegment(segment, region);

  const { error: transcriptError } = await adminClient.from("telehealth_transcripts").insert({
    session_id: input.sessionId,
    speaker: input.speaker,
    snippet: input.snippet,
    start_time: input.startTime,
    end_time: input.endTime,
    risk_tags: risk ? [risk.category] : null,
    sentiment_score: input.sentimentScore ?? null,
  });

  if (transcriptError) {
    console.error("[telehealth-transcript] save error", transcriptError);
  }

  if (risk) {
    const { error: riskError } = await adminClient.from("telehealth_risk_events").insert({
      session_id: input.sessionId,
      severity: risk.severity,
      category: risk.category,
      message: risk.message,
      transcript_excerpt: risk.transcriptSegment,
      recommended_action: risk.recommendedAction,
      region,
    });

    if (riskError) {
      console.error("[telehealth-transcript] risk event save error", riskError);
    }
  }

  return { success: true, riskDetected: !!risk };
}

export async function getSessionTranscripts(sessionId: string) {
  const adminClient = getAdminClient();
  if (!adminClient) {
    return [];
  }

  const { data, error } = await adminClient
    .from("telehealth_transcripts")
    .select("*")
    .eq("session_id", sessionId)
    .order("start_time", { ascending: true });

  if (error) {
    console.error("[telehealth-transcript] fetch error", error);
    return [];
  }

  return data || [];
}

export async function getSessionRiskEvents(sessionId: string) {
  const adminClient = getAdminClient();
  if (!adminClient) {
    return [];
  }

  const { data, error } = await adminClient
    .from("telehealth_risk_events")
    .select("*")
    .eq("session_id", sessionId)
    .order("created_at", { ascending: true });

  if (error) {
    console.error("[telehealth-transcript] risk events fetch error", error);
    return [];
  }

  return data || [];
}

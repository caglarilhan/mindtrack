import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { saveTranscriptSnippet } from "@/lib/server/telehealthTranscript";

interface WorkerInput {
  sessionId: string;
  transcript: string;
  speaker?: "patient" | "provider" | "caregiver" | "system";
  region?: "us" | "eu";
  startTimeSec?: number;
  wordsPerSecond?: number;
}

function splitSentences(text: string): string[] {
  return text
    .split(/(?<=[.!?])\s+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

export async function POST(request: NextRequest) {
  try {
    await requirePermission("telehealth:link:create");
    const body = (await request.json()) as WorkerInput;
    const sessionId = body.sessionId;
    const speaker = body.speaker || "patient";
    const region = body.region || "us";
    const wps = body.wordsPerSecond || 2.5; // approx words/sec
    const startBase = body.startTimeSec || 0;

    if (!sessionId || !body.transcript) {
      return NextResponse.json({ error: "sessionId ve transcript gerekli" }, { status: 400 });
    }

    const sentences = splitSentences(body.transcript);
    if (sentences.length === 0) {
      return NextResponse.json({ error: "Transcript boş" }, { status: 400 });
    }

    let cursor = startBase;
    let saved = 0;
    let riskCount = 0;

    for (const sentence of sentences) {
      const words = sentence.split(/\s+/).filter(Boolean).length;
      const duration = Math.max(1, Math.round(words / wps));
      const startTime = cursor;
      const endTime = cursor + duration;
      cursor = endTime;

      const res = await saveTranscriptSnippet(
        {
          sessionId,
          speaker,
          snippet: sentence,
          startTime,
          endTime,
        },
        region,
      );
      saved += 1;
      if (res.riskDetected) riskCount += 1;
    }

    return NextResponse.json({
      success: true,
      saved,
      riskDetected: riskCount,
    });
  } catch (error) {
    console.error("[telehealth-transcripts-worker] POST error", error);
    return NextResponse.json({ error: "Transcript işlenemedi" }, { status: 500 });
  }
}











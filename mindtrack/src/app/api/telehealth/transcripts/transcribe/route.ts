import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { transcribeAudioFromUrl } from "@/lib/server/telehealthTranscribe";
import { saveTranscriptSnippet } from "@/lib/server/telehealthTranscript";

export async function POST(request: NextRequest) {
  try {
    await requirePermission("telehealth:link:create");
    const body = await request.json();
    const sessionId = body?.sessionId as string | undefined;
    const audioUrl = body?.audioUrl as string | undefined;
    const speaker = (body?.speaker as "patient" | "provider" | "caregiver" | "system") || "patient";
    const region = (body?.region as "us" | "eu") || "us";

    if (!sessionId || !audioUrl) {
      return NextResponse.json({ error: "sessionId ve audioUrl gerekli" }, { status: 400 });
    }

    const result = await transcribeAudioFromUrl({ audioUrl, speaker });
    if (!result.text) {
      return NextResponse.json({ error: "Transcription boş döndü" }, { status: 500 });
    }

    // Tek blok olarak kaydet; istenirse worker/ingest üzerinden cümle kırpılabilir.
    const saveRes = await saveTranscriptSnippet(
      {
        sessionId,
        speaker,
        snippet: result.text,
        startTime: body?.startTimeSec ?? 0,
        endTime: (body?.startTimeSec ?? 0) + Math.max(1, Math.round((result.text.split(/\s+/).length || 1) / 2.5)),
      },
      region,
    );

    return NextResponse.json({
      success: true,
      transcript: result.text,
      confidence: result.confidence,
      words: result.words?.length || 0,
      riskDetected: saveRes.riskDetected,
    });
  } catch (error: any) {
    console.error("[telehealth-transcripts-transcribe] POST error", error);
    return NextResponse.json({ error: error?.message || "Transcription başarısız" }, { status: 500 });
  }
}











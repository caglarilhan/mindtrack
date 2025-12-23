import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { saveTranscriptSnippet } from "@/lib/server/telehealthTranscript";

type IngestSegment = {
  speaker: "patient" | "provider" | "caregiver" | "system";
  text: string;
  startTime?: number;
  endTime?: number;
  sentimentScore?: number;
};

export async function POST(request: NextRequest) {
  try {
    await requirePermission("telehealth:link:create");
    const body = await request.json();
    const sessionId = body?.sessionId as string | undefined;
    const region = (body?.region as "us" | "eu") || "us";
    const segments = (body?.segments as IngestSegment[] | undefined) || [];

    if (!sessionId) {
      return NextResponse.json({ error: "sessionId gerekli" }, { status: 400 });
    }
    if (!Array.isArray(segments) || segments.length === 0) {
      return NextResponse.json({ error: "segments boş olamaz" }, { status: 400 });
    }

    let saved = 0;
    let riskCount = 0;

    for (const seg of segments) {
      if (!seg.text || !seg.speaker) continue;
      const res = await saveTranscriptSnippet(
        {
          sessionId,
          speaker: seg.speaker,
          snippet: seg.text,
          startTime: seg.startTime ?? 0,
          endTime: seg.endTime ?? (seg.startTime ?? 0),
          sentimentScore: seg.sentimentScore,
        },
        region,
      );
      saved += 1;
      if (res.riskDetected) riskCount += 1;
    }

    return NextResponse.json({ success: true, saved, riskDetected: riskCount });
  } catch (error) {
    console.error("[telehealth-transcripts-ingest] POST error", error);
    return NextResponse.json({ error: "İşleme sırasında hata oluştu" }, { status: 500 });
  }
}











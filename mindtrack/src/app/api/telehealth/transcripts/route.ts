import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { saveTranscriptSnippet, getSessionTranscripts, getSessionRiskEvents } from "@/lib/server/telehealthTranscript";

export async function POST(request: NextRequest) {
  try {
    await requirePermission("telehealth:link:create");
    const body = await request.json();
    const { sessionId, speaker, snippet, startTime, endTime, sentimentScore, region } = body;

    if (!sessionId || !speaker || !snippet) {
      return NextResponse.json({ error: "sessionId, speaker ve snippet gerekli" }, { status: 400 });
    }

    const result = await saveTranscriptSnippet(
      {
        sessionId,
        speaker,
        snippet,
        startTime: startTime || 0,
        endTime: endTime || 0,
        sentimentScore,
      },
      region || "us",
    );

    return NextResponse.json(result);
  } catch (error) {
    console.error("[telehealth-transcript] POST error", error);
    return NextResponse.json({ error: "Transcript kaydedilemedi" }, { status: 500 });
  }
}

export async function GET(request: NextRequest) {
  try {
    await requirePermission("telehealth:link:create");
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get("sessionId");
    const includeRisks = searchParams.get("includeRisks") === "true";

    if (!sessionId) {
      return NextResponse.json({ error: "sessionId gerekli" }, { status: 400 });
    }

    const [transcripts, riskEvents] = await Promise.all([
      getSessionTranscripts(sessionId),
      includeRisks ? getSessionRiskEvents(sessionId) : Promise.resolve([]),
    ]);

    return NextResponse.json({ transcripts, riskEvents: includeRisks ? riskEvents : undefined });
  } catch (error) {
    console.error("[telehealth-transcript] GET error", error);
    return NextResponse.json({ error: "Transcript alınamadı" }, { status: 500 });
  }
}

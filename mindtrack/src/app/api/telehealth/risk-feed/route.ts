import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { getSessionRiskEvents } from "@/lib/server/telehealthTranscript";

export async function GET(request: NextRequest) {
  try {
    await requirePermission("telehealth:link:create");
    const { searchParams } = new URL(request.url);
    const sessionId = searchParams.get("sessionId");
    const patientId = searchParams.get("patientId");
    const region = (searchParams.get("region") as "us" | "eu") || "us";

    if (!sessionId && !patientId) {
      return NextResponse.json({ error: "sessionId veya patientId gerekli" }, { status: 400 });
    }

    let riskEvents: any[] = [];

    if (sessionId) {
      riskEvents = await getSessionRiskEvents(sessionId);
    } else if (patientId) {
      // Patient bazlı risk feed (son 24 saat)
      const supabase = await import("@/lib/supabaseClient").then((m) => m.createSupabaseServerClient());
      const client = await supabase();
      const cutoff = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();

      const { data: sessions } = await client
        .from("video_sessions")
        .select("id")
        .eq("patient_id", patientId)
        .gte("start_time", cutoff);

      if (sessions && sessions.length > 0) {
        const sessionIds = sessions.map((s) => s.id);
        const allEvents = await Promise.all(sessionIds.map((sid) => getSessionRiskEvents(sid)));
        riskEvents = allEvents.flat();
      }
    }

    const critical = riskEvents.filter((e) => e.severity === "critical" || e.severity === "high");
    const recent = riskEvents.slice(-10);

    return NextResponse.json({
      events: recent,
      criticalCount: critical.length,
      totalCount: riskEvents.length,
      region,
    });
  } catch (error) {
    console.error("[telehealth-risk-feed] GET error", error);
    return NextResponse.json({ error: "Risk feed alınamadı" }, { status: 500 });
  }
}

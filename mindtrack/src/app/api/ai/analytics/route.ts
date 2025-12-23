import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";
import { calculateSOAPAnalytics, calculateTrendData, calculateUsageStats } from "@/lib/ai/analytics";

export async function GET(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const clientId = searchParams.get("clientId");
    const days = parseInt(searchParams.get("days") || "30", 10);

    // Fetch notes - optimized query with limit
    let notesQuery = supabase
      .from("notes")
      .select("id, created_at, content_encrypted, metadata, session_id, client_id")
      .eq("type", "SOAP")
      .order("created_at", { ascending: false })
      .limit(1000); // Limit to prevent huge queries

    if (clientId) {
      notesQuery = notesQuery.eq("client_id", clientId);
    }

    const { data: notes, error: notesError } = await notesQuery;

    if (notesError) {
      console.error("Analytics notes error:", notesError);
      return NextResponse.json({ error: "Notes fetch failed" }, { status: 500 });
    }

    // Fetch sessions - optimized query
    let sessionsQuery = supabase
      .from("therapy_sessions")
      .select("id, created_at, client_id")
      .limit(1000); // Limit to prevent huge queries

    if (clientId) {
      sessionsQuery = sessionsQuery.eq("client_id", clientId);
    }

    const { data: sessions, error: sessionsError } = await sessionsQuery;

    if (sessionsError) {
      console.error("Analytics sessions error:", sessionsError);
      return NextResponse.json({ error: "Sessions fetch failed" }, { status: 500 });
    }

    // Calculate analytics
    const analytics = await calculateSOAPAnalytics(notes || []);
    const trends = calculateTrendData(notes || [], days);
    const usageStats = calculateUsageStats(sessions || [], notes || []);

    return NextResponse.json({
      success: true,
      analytics,
      trends,
      usageStats,
    });
  } catch (error: any) {
    console.error("Analytics API error:", error);
    return NextResponse.json(
      { error: "Internal server error", details: error.message },
      { status: 500 }
    );
  }
}


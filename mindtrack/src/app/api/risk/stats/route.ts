import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";
import { getRiskStats } from "@/lib/ai/risk-logging";

export async function GET(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const clientId = searchParams.get("clientId");
    const days = parseInt(searchParams.get("days") || "30");

    if (!clientId) {
      return NextResponse.json(
        { error: "clientId gerekli" },
        { status: 400 }
      );
    }

    // Client'ın sahibi olduğunu kontrol et
    const { data: client, error: clientError } = await supabase
      .from("clients")
      .select("owner_id")
      .eq("id", clientId)
      .single();

    if (clientError || !client || client.owner_id !== user.id) {
      return NextResponse.json(
        { error: "Unauthorized - Bu client'a erişim yetkiniz yok" },
        { status: 403 }
      );
    }

    const stats = await getRiskStats(clientId, days);

    if (!stats) {
      return NextResponse.json(
        { error: "Risk istatistikleri alınamadı" },
        { status: 500 }
      );
    }

    return NextResponse.json({
      success: true,
      stats,
    });
  } catch (error: any) {
    console.error("Risk stats API error:", error);
    return NextResponse.json(
      { error: "Internal server error", details: error.message },
      { status: 500 }
    );
  }
}






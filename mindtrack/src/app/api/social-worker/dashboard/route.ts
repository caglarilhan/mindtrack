import { NextRequest, NextResponse } from "next/server";
import { fetchSocialWorkerDashboard } from "@/lib/server/social-worker";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const regionParam = (searchParams.get("region") as "us" | "eu") || "us";
    const data = await fetchSocialWorkerDashboard(regionParam);
    return NextResponse.json({ data });
  } catch (error) {
    console.error("[social-worker] dashboard api error", error);
    return NextResponse.json({ error: "Dashboard getirilemedi" }, { status: 500 });
  }
}

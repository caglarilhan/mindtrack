import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { listDeniedClaimsWithEvents } from "@/lib/server/clearinghouse";

export async function GET(request: NextRequest) {
  try {
    await requirePermission("analytics:appointments:read");
    const { searchParams } = new URL(request.url);
    const limit = Number(searchParams.get("limit") || 50);
    const items = await listDeniedClaimsWithEvents(limit);
    return NextResponse.json({ claims: items });
  } catch (error) {
    console.error("[era-denials] GET error", error);
    return NextResponse.json({ error: "Denial listesi alınamadı" }, { status: 500 });
  }
}











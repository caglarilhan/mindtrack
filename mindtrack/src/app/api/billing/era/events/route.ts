import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { listEraEvents } from "@/lib/server/clearinghouse";

export async function GET(request: NextRequest) {
  try {
    await requirePermission("analytics:appointments:read");
    const { searchParams } = new URL(request.url);
    const claimId = searchParams.get("claimId") || undefined;
    const claimNumber = searchParams.get("claimNumber") || undefined;
    const limit = Number(searchParams.get("limit") || 50);

    const events = await listEraEvents({ claimId, claimNumber, limit });
    return NextResponse.json({ events });
  } catch (error) {
    console.error("[era-events] GET error", error);
    return NextResponse.json({ error: "ERA event listesi alınamadı" }, { status: 500 });
  }
}











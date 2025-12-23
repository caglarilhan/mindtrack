import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { fetchIntegrationHealth } from "@/lib/server/integrations";

export async function GET(request: NextRequest) {
  try {
    await requirePermission("settings:integrations:read");
    const { searchParams } = new URL(request.url);
    const clinicId = searchParams.get("clinicId") || "demo-clinic";
    const health = await fetchIntegrationHealth(clinicId);
    return NextResponse.json({ health });
  } catch (error) {
    console.error("[integrations] health api error", error);
    return NextResponse.json({ error: "Health bilgisi alınamadı" }, { status: 500 });
  }
}

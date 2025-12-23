import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { fetchIntegrationCatalog, fetchIntegrationConnections } from "@/lib/server/integrations";

export async function GET(request: NextRequest) {
  try {
    await requirePermission("settings:integrations:read");
    const { searchParams } = new URL(request.url);
    const clinicId = searchParams.get("clinicId") || "demo-clinic";

    const [catalog, connections] = await Promise.all([
      fetchIntegrationCatalog(),
      fetchIntegrationConnections(clinicId),
    ]);

    return NextResponse.json({ catalog, connections });
  } catch (error) {
    console.error("[integrations] catalog api error", error);
    return NextResponse.json({ error: "Catalog alınamadı" }, { status: 500 });
  }
}

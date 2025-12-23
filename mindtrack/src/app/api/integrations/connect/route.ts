import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { upsertIntegrationConnection } from "@/lib/server/integrations";

export async function POST(request: NextRequest) {
  try {
    await requirePermission("settings:integrations:write");
    const { clinicId, integrationSlug, status, settings } = await request.json();
    if (!clinicId || !integrationSlug || !status) {
      return NextResponse.json({ error: "clinicId, integrationSlug ve status gerekli" }, { status: 400 });
    }
    const result = await upsertIntegrationConnection({ clinicId, integrationSlug, status, settings });
    if (!result.success) {
      return NextResponse.json({ error: result.error || "Güncellenemedi" }, { status: 400 });
    }
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("[integrations] connect api error", error);
    return NextResponse.json({ error: "Bağlantı kaydedilemedi" }, { status: 500 });
  }
}

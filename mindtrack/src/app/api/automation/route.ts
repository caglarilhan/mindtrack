import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { fetchAutomationRules, saveAutomationRule } from "@/lib/server/integrations";

export async function GET(request: NextRequest) {
  try {
    await requirePermission("settings:integrations:read");
    const { searchParams } = new URL(request.url);
    const clinicId = searchParams.get("clinicId") || "demo-clinic";
    const rules = await fetchAutomationRules(clinicId);
    return NextResponse.json({ rules });
  } catch (error) {
    console.error("[automation] GET error", error);
    return NextResponse.json({ error: "Kurallar alınamadı" }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    await requirePermission("settings:integrations:write");
    const body = await request.json();
    const clinicId = body?.clinicId as string | undefined;
    if (!clinicId) {
      return NextResponse.json({ error: "clinicId gerekli" }, { status: 400 });
    }
    const payload = {
      id: body?.id,
      clinicId,
      name: body?.name || "Untitled",
      trigger: body?.trigger || {},
      conditions: body?.conditions || [],
      actions: body?.actions || [],
      enabled: body?.enabled ?? true,
    };
    const res = await saveAutomationRule(payload);
    if (!res.success) {
      return NextResponse.json({ error: res.error || "Kaydedilemedi" }, { status: 400 });
    }
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("[automation] POST error", error);
    return NextResponse.json({ error: "Kaydetme başarısız" }, { status: 500 });
  }
}











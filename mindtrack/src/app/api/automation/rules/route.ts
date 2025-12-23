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
    await requirePermission("automation:rules:write");
    const body = await request.json();
    if (!body?.clinicId || !body?.name || !body?.trigger || !body?.actions) {
      return NextResponse.json({ error: "Eksik alanlar" }, { status: 400 });
    }
    const result = await saveAutomationRule(body);
    if (!result.success) {
      return NextResponse.json({ error: result.error || "Kaydedilemedi" }, { status: 400 });
    }
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("[automation] POST error", error);
    return NextResponse.json({ error: "Kural kaydedilemedi" }, { status: 500 });
  }
}

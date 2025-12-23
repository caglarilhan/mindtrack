import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { fetchTelehealthBranding, upsertTelehealthBranding } from "@/lib/server/telehealthBranding";

// Clinic ID şu anlık kullanıcı metadata'sından veya query param'dan geliyor (MVP)
function resolveClinic(request: NextRequest): string {
  const clinicId = request.headers.get("x-clinic-id") || "default-clinic";
  return clinicId;
}

export async function GET(request: NextRequest) {
  try {
    await requirePermission("settings:communications:read");
    const clinicId = resolveClinic(request);
    const branding = await fetchTelehealthBranding(clinicId);
    return NextResponse.json({ branding });
  } catch (error) {
    console.error("[telehealth-branding] GET error", error);
    return NextResponse.json({ error: "Branding alınamadı" }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    await requirePermission("settings:communications:write");
    const clinicId = resolveClinic(request);
    const body = await request.json();
    const result = await upsertTelehealthBranding({
      clinicId,
      logoUrl: body.logoUrl,
      accentColor: body.accentColor,
      waitingRoomMessage: body.waitingRoomMessage,
      helpLinks: body.helpLinks,
      allowCaregiverJoin: body.allowCaregiverJoin,
      defaultRegion: body.defaultRegion,
    });
    if (!result.success) {
      return NextResponse.json({ error: result.error || "Branding kaydedilemedi" }, { status: 500 });
    }
    const branding = await fetchTelehealthBranding(clinicId);
    return NextResponse.json({ branding });
  } catch (error) {
    console.error("[telehealth-branding] POST error", error);
    return NextResponse.json({ error: "Branding kaydedilemedi" }, { status: 500 });
  }
}

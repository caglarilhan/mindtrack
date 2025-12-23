import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { fetchClientPortalData } from "@/lib/server/portal";

export async function GET(request: NextRequest) {
  try {
    await requirePermission("patient:anamnesis:read");
    const { searchParams } = new URL(request.url);
    const patientId = searchParams.get("patientId");
    const region = (searchParams.get("region") as "us" | "eu") || "us";
    if (!patientId) {
      return NextResponse.json({ error: "patientId gerekli" }, { status: 400 });
    }
    const data = await fetchClientPortalData(patientId, region);
    return NextResponse.json({ data });
  } catch (error) {
    console.error("[caregiver-summary-internal] error", error);
    return NextResponse.json({ error: "Caregiver özeti alınamadı" }, { status: 500 });
  }
}

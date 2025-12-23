import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import {
  createCaregiverToken,
  listCaregiverTokens,
} from "@/lib/server/caregiverTokens";

export async function GET() {
  try {
    await requirePermission("caregiver:tokens:manage");
    const tokens = await listCaregiverTokens();
    return NextResponse.json({ tokens });
  } catch (error) {
    console.error("[caregiver-tokens] GET error", error);
    return NextResponse.json({ error: "Token listesi alınamadı" }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    await requirePermission("caregiver:tokens:manage");
    const body = await request.json();
    const label = (body?.label as string)?.trim();
    const allowedRegions = Array.isArray(body?.allowedRegions) ? body.allowedRegions : undefined;
    const expiresAt = body?.expiresAt ?? null;

    if (!label) {
      return NextResponse.json({ error: "label gerekli" }, { status: 400 });
    }

    const result = await createCaregiverToken({ label, allowedRegions, expiresAt });
    return NextResponse.json(result);
  } catch (error) {
    console.error("[caregiver-tokens] POST error", error);
    return NextResponse.json({ error: "Token oluşturulamadı" }, { status: 500 });
  }
}

import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { deleteCaregiverToken, updateCaregiverToken } from "@/lib/server/caregiverTokens";

export async function PATCH(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    await requirePermission("caregiver:tokens:manage");
    const { id } = params;
    const body = await request.json();
    const { label, active, allowedRegions, expiresAt } = body ?? {};

    if (!label && active === undefined && !allowedRegions && expiresAt === undefined) {
      return NextResponse.json({ error: "Güncellenecek alan yok" }, { status: 400 });
    }

    const record = await updateCaregiverToken({
      id,
      label,
      active,
      allowedRegions,
      expiresAt: expiresAt ?? undefined,
    });
    return NextResponse.json({ record });
  } catch (error) {
    console.error("[caregiver-tokens] PATCH error", error);
    return NextResponse.json({ error: "Token güncellenemedi" }, { status: 500 });
  }
}

export async function DELETE(_request: NextRequest, { params }: { params: { id: string } }) {
  try {
    await requirePermission("caregiver:tokens:manage");
    const { id } = params;
    await deleteCaregiverToken(id);
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("[caregiver-tokens] DELETE error", error);
    return NextResponse.json({ error: "Token silinemedi" }, { status: 500 });
  }
}

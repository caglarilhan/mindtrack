import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { rotateCaregiverToken } from "@/lib/server/caregiverTokens";

export async function POST(_request: NextRequest, { params }: { params: { id: string } }) {
  try {
    await requirePermission("caregiver:tokens:manage");
    const { id } = params;
    const result = await rotateCaregiverToken(id);
    return NextResponse.json(result);
  } catch (error) {
    console.error("[caregiver-tokens] ROTATE error", error);
    return NextResponse.json({ error: "Token yenilenemedi" }, { status: 500 });
  }
}

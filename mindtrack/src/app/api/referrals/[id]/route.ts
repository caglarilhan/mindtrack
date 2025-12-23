import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { updateReferralStatus } from "@/lib/server/referrals";

export async function PATCH(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    await requirePermission("referrals:write");
    const body = await request.json();
    if (!body?.status) {
      return NextResponse.json({ error: "status alanı gerekli" }, { status: 400 });
    }
    const referral = await updateReferralStatus(params.id, body.status);
    return NextResponse.json({ referral });
  } catch (error) {
    console.error("[referrals] PATCH error", error);
    return NextResponse.json({ error: "Referral güncellenemedi" }, { status: 500 });
  }
}

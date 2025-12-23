import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { fetchReferralStats } from "@/lib/server/referrals";

const DEFAULT_CLINIC = process.env.NEXT_PUBLIC_DEFAULT_CLINIC_ID || "demo-clinic";

export async function GET(request: NextRequest) {
  try {
    await requirePermission("referrals:read");
    const { searchParams } = new URL(request.url);
    const clinicId = searchParams.get("clinicId") || DEFAULT_CLINIC;
    const stats = await fetchReferralStats(clinicId);
    return NextResponse.json({ stats });
  } catch (error) {
    console.error("[referrals] stats error", error);
    return NextResponse.json({ error: "Referral istatistikleri alınamadı" }, { status: 500 });
  }
}

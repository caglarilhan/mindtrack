import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { fetchReferralContacts, fetchReferrals, createReferral } from "@/lib/server/referrals";

const DEFAULT_CLINIC = process.env.NEXT_PUBLIC_DEFAULT_CLINIC_ID || "demo-clinic";

export async function GET(request: NextRequest) {
  try {
    await requirePermission("referrals:read");
    const { searchParams } = new URL(request.url);
    const clinicId = searchParams.get("clinicId") || DEFAULT_CLINIC;
    const region = searchParams.get("region") || undefined;
    const status = searchParams.get("status") || undefined;
    const search = searchParams.get("search") || undefined;

    const [contacts, referrals] = await Promise.all([
      fetchReferralContacts(clinicId, { region, search }),
      fetchReferrals(clinicId, { status: status || undefined }),
    ]);

    return NextResponse.json({ contacts, referrals });
  } catch (error) {
    console.error("[referrals] GET error", error);
    return NextResponse.json({ error: "Referral kayıtları alınamadı" }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    await requirePermission("referrals:write");
    const body = await request.json();
    if (!body?.contactId || !body?.reason) {
      return NextResponse.json({ error: "contactId ve reason gerekli" }, { status: 400 });
    }
    const clinicId = body.clinicId || DEFAULT_CLINIC;
    const region = body.region || "us";
    const referral = await createReferral({
      clinicId,
      contactId: body.contactId,
      reason: body.reason,
      priority: body.priority,
      region,
      patientHash: body.patientHash || null,
    });
    return NextResponse.json({ referral });
  } catch (error) {
    console.error("[referrals] POST error", error);
    return NextResponse.json({ error: "Referral oluşturulamadı" }, { status: 500 });
  }
}

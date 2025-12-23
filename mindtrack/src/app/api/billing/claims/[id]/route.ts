import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { getClaimDetail, resubmitClaim, logEraEvent, updateClaimStatus } from "@/lib/server/clearinghouse";

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } },
) {
  try {
    await requirePermission("analytics:appointments:read");
    const detail = await getClaimDetail(params.id);
    return NextResponse.json(detail);
  } catch (error) {
    console.error("[billing-claims-detail] GET error", error);
    return NextResponse.json({ error: "Claim detay alınamadı" }, { status: 500 });
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } },
) {
  try {
    await requirePermission("appointments:write");
    const { action, note, code, description } = await request.json();
    if (action === "resubmit") {
      const data = await resubmitClaim(params.id);
      return NextResponse.json({ claim: data });
    }
    if (action === "appeal") {
      // Appeal notu ERA event olarak da loglanabilir
      await logEraEvent(params.id, code || "APPEAL", description || "Appeal submitted", 0, {
        note: note || description,
      });
      await updateClaimStatus(params.id, "submitted", { statusMessage: description || "Appeal submitted" });
      return NextResponse.json({ success: true });
    }
    return NextResponse.json({ error: "Geçersiz aksiyon" }, { status: 400 });
  } catch (error) {
    console.error("[billing-claims-detail] POST error", error);
    return NextResponse.json({ error: "İşlem başarısız" }, { status: 500 });
  }
}

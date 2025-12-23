import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { enqueueClaim, listClaims, build837Payload } from "@/lib/server/clearinghouse";

export async function GET(request: NextRequest) {
  try {
    await requirePermission("analytics:appointments:read");
    const { searchParams } = new URL(request.url);
    const status = searchParams.get("status") as any;
    const claims = await listClaims(status);
    return NextResponse.json({ claims });
  } catch (error) {
    console.error("[billing-claims] GET error", error);
    return NextResponse.json({ error: "Claim listesi alınamadı" }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    await requirePermission("appointments:write");
    const body = await request.json();
    const { claimNumber, patientId, providerId, payload, payerConnectionId, region } = body;
    if (!claimNumber || !patientId || !providerId || !payload) {
      return NextResponse.json({ error: "claimNumber, patientId, providerId, payload gerekli" }, { status: 400 });
    }

    const normalizedPayload = typeof payload === "string" ? JSON.parse(payload) : payload;
    const enrichedPayload = { ...normalizedPayload, document: build837Payload(normalizedPayload) };

    const record = await enqueueClaim({
      claimNumber,
      patientId,
      providerId,
      payerConnectionId: payerConnectionId || null,
      payload: enrichedPayload,
      region,
    });

    return NextResponse.json({ claim: record });
  } catch (error) {
    console.error("[billing-claims] POST error", error);
    return NextResponse.json({ error: "Claim kuyruğa alınamadı" }, { status: 500 });
  }
}

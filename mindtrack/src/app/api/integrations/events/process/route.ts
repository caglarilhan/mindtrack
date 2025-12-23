import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { processPendingIntegrationEvents } from "@/lib/server/integrations";

export async function POST(request: NextRequest) {
  try {
    await requirePermission("settings:integrations:write");
    const body = await request.json().catch(() => ({}));
    const clinicId = body?.clinicId as string | undefined;
    const result = await processPendingIntegrationEvents({ clinicId, limit: body?.limit ?? 10 });
    return NextResponse.json({ success: true, processed: result.processed });
  } catch (error) {
    console.error("[integrations] process events error", error);
    return NextResponse.json({ error: "Event işleme başarısız" }, { status: 500 });
  }
}

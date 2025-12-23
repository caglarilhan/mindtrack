import { NextRequest, NextResponse } from "next/server";
import { logIntegrationEvent } from "@/lib/server/integrations";

const DEFAULT_SECRET = process.env.INTEGRATION_WEBHOOK_SECRET;

export async function POST(request: NextRequest) {
  try {
    const slug = request.headers.get("x-integration-slug") || "unknown";
    const secret = request.headers.get("x-integration-secret");
    if (!DEFAULT_SECRET) {
      return NextResponse.json({ error: "Webhook secret missing" }, { status: 500 });
    }
    if (secret !== DEFAULT_SECRET) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
    const body = await request.json();
    const clinicId = body?.clinicId || null;
    const status = body?.status || "queued";
    await logIntegrationEvent({
      clinicId,
      integrationSlug: slug,
      eventType: body?.eventType || "webhook",
      payload: body || {},
      status,
      error: body?.error,
    });
    return NextResponse.json({ success: true });
  } catch (error) {
    console.error("[integrations] webhook error", error);
    return NextResponse.json({ error: "Webhook işlem hatası" }, { status: 500 });
  }
}

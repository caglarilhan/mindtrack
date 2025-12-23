import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { logEraEvent, updateClaimStatus, getClaimByNumber } from "@/lib/server/clearinghouse";

const CRON_SECRET = process.env.CRON_SECRET;

/**
 * Basit cron/pull endpoint'i: harici kaynaklardan gelen ERA event'lerini cron ile aktar.
 * Not: Gerçek polling yerine, cron job buraya payload post edebilir.
 */
export async function POST(request: NextRequest) {
  try {
    // İki katman: header secret veya RBAC
    const provided = request.headers.get("x-cron-secret");
    if (CRON_SECRET && provided !== CRON_SECRET) {
      // Cron secret tanımlıysa RBAC kontrolü yerine secret öncelikli
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }
    if (!CRON_SECRET) {
      await requirePermission("settings:integrations:write");
    }

    const body = await request.json().catch(() => ({}));
    const events = body?.events || [];
    if (!Array.isArray(events) || events.length === 0) {
      return NextResponse.json({ error: "events array required" }, { status: 400 });
    }

    const responses: any[] = [];
    for (const ev of events) {
      if (!ev?.claimNumber) {
        responses.push({ status: "skipped", reason: "claimNumber missing" });
        continue;
      }
      const claim = await getClaimByNumber(ev.claimNumber);
      if (!claim) {
        responses.push({ status: "skipped", claimNumber: ev.claimNumber, reason: "claim not found" });
        continue;
      }
      await logEraEvent(claim.id, ev.code || "ERA", ev.description || "", ev.amount || 0, ev);
      if (ev.status) {
        await updateClaimStatus(claim.id, mapEraStatus(ev.status), {
          statusMessage: ev.description,
          code: ev.code,
        });
      }
      responses.push({ status: "ok", claimNumber: ev.claimNumber });
    }

    return NextResponse.json({ ingested: responses });
  } catch (error) {
    console.error("[cron-era-pull] error", error);
    return NextResponse.json({ error: "Cron ingest failed" }, { status: 500 });
  }
}

function mapEraStatus(status: "denied" | "paid" | "acknowledged" | "submitted" | "error" | string) {
  switch (status) {
    case "paid":
      return "paid";
    case "acknowledged":
      return "acknowledged";
    case "denied":
      return "denied";
    case "error":
      return "error";
    default:
      return "submitted";
  }
}











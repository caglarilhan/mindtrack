import { NextRequest, NextResponse } from "next/server";
import { logEraEvent, getClaimByNumber, updateClaimStatus } from "@/lib/server/clearinghouse";
import { sendTransactionalEmail } from "@/lib/server/notifications";

const ERA_SECRET = process.env.ERA_WEBHOOK_SECRET;
const BILLING_ALERT_EMAIL = process.env.BILLING_ALERT_EMAIL || process.env.SUPPORT_EMAIL;

interface EraEventPayload {
  claimNumber: string;
  code: string;
  description: string;
  amount?: number;
  status?: "denied" | "paid" | "acknowledged" | "submitted" | "error";
  region?: "us" | "eu";
}

export async function POST(request: NextRequest) {
  try {
    if (!ERA_SECRET) {
      return NextResponse.json({ error: "ERA secret missing" }, { status: 500 });
    }
    const provided = request.headers.get("x-era-secret");
    if (provided !== ERA_SECRET) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { events } = await request.json();
    if (!Array.isArray(events) || events.length === 0) {
      return NextResponse.json({ error: "events array required" }, { status: 400 });
    }

    const responses: any[] = [];

    for (const event of events as EraEventPayload[]) {
      if (!event.claimNumber) {
        responses.push({ status: "skipped", reason: "claimNumber missing" });
        continue;
      }

      const claim = await getClaimByNumber(event.claimNumber);
      if (!claim) {
        responses.push({ status: "skipped", claimNumber: event.claimNumber, reason: "claim not found" });
        continue;
      }

      await logEraEvent(claim.id, event.code || "ERA", event.description || "", event.amount || 0, event);

      if (event.status) {
        await updateClaimStatus(claim.id, mapEraStatus(event.status), {
          statusMessage: event.description,
          code: event.code,
        });
      }

      if (event.status === "denied" && BILLING_ALERT_EMAIL) {
        await sendTransactionalEmail({
          to: BILLING_ALERT_EMAIL,
          subject: `Claim ${event.claimNumber} denied`,
          html: `<p>Claim ${event.claimNumber} for patient ${claim.patient_id} was denied.</p><p>${event.description}</p>`,
        });
      }

      responses.push({ status: "ok", claimNumber: event.claimNumber });
    }

    return NextResponse.json({ ingested: responses });
  } catch (error) {
    console.error("[era-ingest] error", error);
    return NextResponse.json({ error: "Ingest failed" }, { status: 500 });
  }
}

function mapEraStatus(status: EraEventPayload["status"]): "queued" | "submitted" | "acknowledged" | "denied" | "paid" | "error" {
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

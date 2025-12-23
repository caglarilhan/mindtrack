import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { fetchSocialWorkerTasks, fetchSocialWorkerHandoffs } from "@/lib/server/social-worker";

const DEFAULT_CLINIC = process.env.NEXT_PUBLIC_DEFAULT_CLINIC_ID || "demo-clinic";

export async function GET(request: NextRequest) {
  try {
    await requirePermission("social:cases:read");
    const { searchParams } = new URL(request.url);
    const clinicId = searchParams.get("clinicId") || DEFAULT_CLINIC;
    const region = searchParams.get("region") || undefined;

    const [tasks, handoffs] = await Promise.all([
      fetchSocialWorkerTasks({ clinicId, region }),
      fetchSocialWorkerHandoffs({ clinicId }),
    ]);

    return NextResponse.json({ tasks, handoffs });
  } catch (error) {
    console.error("[social-worker] tasks GET error", error);
    return NextResponse.json({ error: "Social worker verisi alınamadı" }, { status: 500 });
  }
}

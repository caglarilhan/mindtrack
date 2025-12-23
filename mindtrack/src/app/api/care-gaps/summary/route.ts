import { NextRequest, NextResponse } from "next/server";
import { computeCareGaps } from "@/lib/server/careGaps";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { patientIds, region } = body as { patientIds?: string[]; region?: "us" | "eu" };

    if (!patientIds || !Array.isArray(patientIds) || patientIds.length === 0) {
      return NextResponse.json({ error: "patientIds array gerekli" }, { status: 400 });
    }

    const uniqueIds = Array.from(new Set(patientIds));
    const results: Record<string, any[]> = {};

    await Promise.all(
      uniqueIds.map(async (id) => {
        const gaps = await computeCareGaps(id, region || "us");
        results[id] = gaps;
      })
    );

    return NextResponse.json({ careGaps: results });
  } catch (err) {
    console.error("POST /api/care-gaps/summary error:", err);
    return NextResponse.json({ error: "Bilinmeyen hata" }, { status: 500 });
  }
}

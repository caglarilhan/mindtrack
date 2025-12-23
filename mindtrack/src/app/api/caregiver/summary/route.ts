import { NextRequest, NextResponse } from "next/server";
import { computeCareGaps } from "@/lib/server/careGaps";
import { fetchSafetySummaryByPatients } from "@/lib/server/safety";

// NOT: Şu an için auth/token doğrulaması placeholder.
// Gerçek deploy'da caregiver token'ı Supabase veya ayrı bir tablo üzerinden doğrulanmalı.

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const patientId = searchParams.get("patientId");
    const region = (searchParams.get("region") as "us" | "eu") || "us";

    if (!patientId) {
      return NextResponse.json({ error: "patientId gerekli" }, { status: 400 });
    }

    // Klinik notları paylaşmadan sadece durum özeti döndür.
    const [gaps, safetyMap] = await Promise.all([
      computeCareGaps(patientId, region),
      fetchSafetySummaryByPatients([patientId], region),
    ]);

    const safety = safetyMap[patientId];

    return NextResponse.json({
      patientId,
      highestRisk: safety?.highestSeverity ?? "none",
      careGaps: gaps.map((g) => ({
        title: g.title,
        category: g.category,
        severity: g.severity,
        recommendedAction: g.recommendedAction,
      })),
    });
  } catch (err) {
    console.error("GET /api/caregiver/summary error:", err);
    return NextResponse.json({ error: "Bilinmeyen hata" }, { status: 500 });
  }
}

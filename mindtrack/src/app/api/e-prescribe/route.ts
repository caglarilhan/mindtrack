import { NextRequest, NextResponse } from "next/server";
import { submitEPrescription } from "@/lib/server/ePrescribe";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { patientId, medicationName, dosage, frequency } = body;

    if (!patientId || !medicationName || !dosage || !frequency) {
      return NextResponse.json({ error: "patientId, medicationName, dosage, frequency gerekli" }, { status: 400 });
    }

    const result = await submitEPrescription(body);
    if (!result.success) {
      return NextResponse.json({ error: result.error || "Gönderim başarısız" }, { status: 500 });
    }

    return NextResponse.json({ order: result.order });
  } catch (err) {
    console.error("POST /api/e-prescribe error", err);
    return NextResponse.json({ error: "Bilinmeyen hata" }, { status: 500 });
  }
}

import { NextRequest, NextResponse } from "next/server";
import { scheduleLabProtocol } from "@/lib/server/ePrescribe";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { patientId, testName, protocol, dueDate } = body;

    if (!patientId || !testName || !protocol || !dueDate) {
      return NextResponse.json({ error: "patientId, testName, protocol, dueDate gerekli" }, { status: 400 });
    }

    const result = await scheduleLabProtocol(body);
    if (!result.success) {
      return NextResponse.json({ error: result.error || "Lab kaydı başarısız" }, { status: 500 });
    }

    return NextResponse.json({ order: result.order });
  } catch (err) {
    console.error("POST /api/lab-protocol error", err);
    return NextResponse.json({ error: "Bilinmeyen hata" }, { status: 500 });
  }
}

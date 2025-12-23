import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";
import { getAIOrchestrator } from "@/lib/ai/orchestrator";
import type { ProcessingMode } from "@/lib/ai/orchestrator";
import { rateLimit, getRateLimitIdentifier, validateTranscript, logAuditEvent } from "@/lib/ai/security";

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    // Rate limiting
    const identifier = getRateLimitIdentifier(request, user.id);
    const rateLimitResult = rateLimit(identifier, 20, 60000); // 20 request/dakika
    
    if (!rateLimitResult.allowed) {
      return NextResponse.json(
        { 
          error: "Rate limit aşıldı", 
          resetTime: rateLimitResult.resetTime 
        },
        { 
          status: 429,
          headers: {
            'X-RateLimit-Limit': '20',
            'X-RateLimit-Remaining': '0',
            'X-RateLimit-Reset': rateLimitResult.resetTime.toString(),
          }
        }
      );
    }

    const body = await request.json();
    const { 
      transcript, 
      sessionId, 
      clientId, 
      mode = "standard" as ProcessingMode,
      patientData 
    } = body;

    // Input validation
    const validation = validateTranscript(transcript);
    if (!validation.valid) {
      return NextResponse.json(
        { error: validation.error || "Geçersiz transkript" },
        { status: 400 }
      );
    }

    // Audit log
    await logAuditEvent('soap_generate', user.id, {
      mode,
      clientId,
      transcriptLength: validation.sanitized.length,
    });

    // AI Orchestrator kullan (sanitized transcript ile)
    const orchestrator = getAIOrchestrator();
    
    const soap = await orchestrator.processSOAP(
      validation.sanitized,
      mode,
      patientData
    );

    // Firestore'a kaydet (opsiyonel)
    if (sessionId) {
      try {
        await supabase
          .from("session_notes")
          .upsert({
            session_id: sessionId,
            client_id: clientId,
            soap_subjective: soap.subjective,
            soap_objective: soap.objective,
            soap_assessment: soap.assessment,
            soap_plan: soap.plan,
            created_at: new Date().toISOString(),
            created_by: user.id,
          });
      } catch (dbError) {
        console.warn("⚠️ SOAP notu veritabanına kaydedilemedi:", dbError);
        // Devam et, SOAP notu oluşturuldu
      }
    }

    return NextResponse.json({
      success: true,
      soap: {
        subjective: soap.subjective,
        objective: soap.objective,
        assessment: soap.assessment,
        plan: soap.plan,
      },
      mode: mode,
      timestamp: new Date().toISOString(),
    }, {
      headers: {
        'X-RateLimit-Limit': '20',
        'X-RateLimit-Remaining': rateLimitResult.remaining.toString(),
        'X-RateLimit-Reset': rateLimitResult.resetTime.toString(),
      }
    });
  } catch (error: any) {
    console.error("SOAP generation API error:", error);
    return NextResponse.json(
      { 
        error: "SOAP notu oluşturulamadı", 
        details: error.message 
      },
      { status: 500 }
    );
  }
}


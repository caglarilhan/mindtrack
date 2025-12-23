import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";

export async function POST(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const body = await request.json();
    const { soapId, sessionId, rating, feedback, timestamp } = body;

    if (!rating || rating < 1 || rating > 5) {
      return NextResponse.json({ error: "Invalid rating" }, { status: 400 });
    }

    // Save feedback to database
    const { error: insertError } = await supabase
      .from("ai_feedback")
      .insert({
        user_id: user.id,
        soap_id: soapId || null,
        session_id: sessionId || null,
        rating,
        feedback: feedback || null,
        created_at: timestamp || new Date().toISOString(),
      });

    if (insertError) {
      console.error("Feedback insert error:", insertError);
      // Continue anyway - feedback is not critical
    }

    return NextResponse.json({
      success: true,
      message: "Feedback saved",
    });
  } catch (error: unknown) {
    console.error("Feedback API error:", error);
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    return NextResponse.json(
      { error: "Internal server error", details: errorMessage },
      { status: 500 }
    );
  }
}


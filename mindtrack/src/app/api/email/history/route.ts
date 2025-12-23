/**
 * Email history API endpoint
 * Get email history and statistics
 */

import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/utils/supabase/server";
import { getEmailHistory, getEmailStats } from "@/lib/email/history";

export async function GET(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get("limit") || "20", 10);
    const offset = parseInt(searchParams.get("offset") || "0", 10);
    const emailType = searchParams.get("emailType") as "soap" | "risk" | "appointment" | "share" | "other" | null;
    const status = searchParams.get("status") as "pending" | "sent" | "delivered" | "bounced" | "failed" | "opened" | "clicked" | null;
    const relatedId = searchParams.get("relatedId") || undefined;
    const includeStats = searchParams.get("includeStats") === "true";

    const history = await getEmailHistory(user.id, {
      limit,
      offset,
      emailType: emailType || undefined,
      status: status || undefined,
      relatedId,
    });

    const response: {
      success: true;
      data: typeof history.data;
      total: number;
      stats?: Awaited<ReturnType<typeof getEmailStats>>;
    } = {
      success: true,
      data: history.data,
      total: history.total,
    };

    if (includeStats) {
      response.stats = await getEmailStats(user.id);
    }

    return NextResponse.json(response);
  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Get email history error:", error);
    return NextResponse.json({
      error: errorMessage,
    }, { status: 500 });
  }
}






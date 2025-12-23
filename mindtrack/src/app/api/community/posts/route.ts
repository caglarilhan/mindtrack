import { NextRequest, NextResponse } from "next/server";
import { requirePermission } from "@/lib/rbac";
import { fetchCommunityPosts, createCommunityPost } from "@/lib/server/community";

const DEFAULT_CLINIC = process.env.NEXT_PUBLIC_DEFAULT_CLINIC_ID || "demo-clinic";

export async function GET(request: NextRequest) {
  try {
    await requirePermission("community:read");
    const { searchParams } = new URL(request.url);
    const clinicId = searchParams.get("clinicId") || DEFAULT_CLINIC;
    const region = searchParams.get("region") || undefined;
    const posts = await fetchCommunityPosts(clinicId, { region });
    return NextResponse.json({ posts });
  } catch (error) {
    console.error("[community] GET error", error);
    return NextResponse.json({ error: "Community postları alınamadı" }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    await requirePermission("community:write");
    const body = await request.json();
    if (!body?.title || !body?.body) {
      return NextResponse.json({ error: "title ve body gerekli" }, { status: 400 });
    }
    const clinicId = body.clinicId || DEFAULT_CLINIC;
    const region = body.region || "us";
    const post = await createCommunityPost({
      clinicId,
      title: body.title,
      body: body.body,
      tag: body.tag,
      region,
    });
    return NextResponse.json({ post });
  } catch (error) {
    console.error("[community] POST error", error);
    return NextResponse.json({ error: "Community post oluşturulamadı" }, { status: 500 });
  }
}

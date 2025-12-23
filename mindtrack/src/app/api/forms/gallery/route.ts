import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";

function getAdminClient() {
  const url = process.env.NEXT_PUBLIC_SUPABASE_URL!;
  const key = process.env.SUPABASE_SERVICE_ROLE_KEY!;
  return createClient(url, key);
}

export async function GET(request: NextRequest) {
  try {
    const supabase = getAdminClient();
    const { searchParams } = new URL(request.url);
    const category = searchParams.get("category");
    const q = searchParams.get("q");
    const limit = Number(searchParams.get("limit") || 20);

    let query = supabase
      .from("form_template_gallery")
      .select(
        `id, title, description, category, tags, is_featured, download_count, rating, review_count, template_id,
         form_templates:template_id (id, name, description, fields, category, tags)`
      )
      .order("is_featured", { ascending: false })
      .order("rating", { ascending: false })
      .limit(limit);

    if (category) {
      query = query.eq("category", category);
    }
    if (q) {
      query = query.or(
        `title.ilike.%${q}%,description.ilike.%${q}%,form_templates.name.ilike.%${q}%`
      );
    }

    const { data, error } = await query;
    if (error) throw error;

    const items = (data || []).map((row) => ({
      id: row.id,
      title: row.title,
      description: row.description,
      category: row.category,
      tags: row.tags || [],
      rating: row.rating,
      reviewCount: row.review_count,
      downloadCount: row.download_count,
      templateId: row.template_id,
      template: row.form_templates,
    }));

    return NextResponse.json({ items });
  } catch (error) {
    console.error("[forms-gallery] GET error", error);
    return NextResponse.json({ error: "Gallery alınamadı" }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const supabase = getAdminClient();
    const body = await request.json();
    const { galleryId, clinicId, name } = body || {};
    if (!galleryId || !clinicId) {
      return NextResponse.json({ error: "galleryId ve clinicId gerekli" }, { status: 400 });
    }

    const { data: gallery, error: galleryError } = await supabase
      .from("form_template_gallery")
      .select(
        `id, title, description, category, tags, download_count, template_id,
         form_templates:template_id (fields, description, name)`
      )
      .eq("id", galleryId)
      .single();

    if (galleryError || !gallery) {
      return NextResponse.json({ error: "Gallery kaydı bulunamadı" }, { status: 404 });
    }

    const payload = {
      clinic_id: clinicId,
      name: name || gallery.title,
      description: gallery.description || gallery.form_templates?.description,
      version: 1,
      fields: gallery.form_templates?.fields || [],
      category: gallery.category,
      tags: gallery.tags || [],
      is_published: false,
    };

    const { data: template, error: insertError } = await supabase
      .from("form_templates")
      .insert(payload)
      .select()
      .single();

    if (insertError) throw insertError;

    await supabase
      .from("form_template_gallery")
      .update({ download_count: (gallery.download_count || 0) + 1 })
      .eq("id", galleryId);

    return NextResponse.json({ template });
  } catch (error) {
    console.error("[forms-gallery] POST error", error);
    return NextResponse.json({ error: "Gallery import başarısız" }, { status: 500 });
  }
}

import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabaseClient';
import { requirePermission } from '@/lib/rbac';

export async function GET(request: NextRequest) {
  try {
    await requirePermission('patient:education:read');
    
    const supabase = await createSupabaseServerClient();
    
    // Eğitim materyallerini getir
    const { data, error } = await supabase
      .from('education_materials')
      .select('*')
      .eq('is_active', true)
      .order('created_at', { ascending: false });

    if (error) {
      throw error;
    }

    return NextResponse.json({ materials: data || [] });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'Failed to fetch education materials' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    await requirePermission('patient:education:write');
    
    const { title, type, description, content, readTime, category } = await request.json();
    
    if (!title || !type || !description) {
      return NextResponse.json({ error: 'Title, type, and description are required' }, { status: 400 });
    }

    const supabase = await createSupabaseServerClient();
    
    const { data, error } = await supabase
      .from('education_materials')
      .insert({
        title,
        type,
        description,
        content: content || null,
        read_time_minutes: readTime || null,
        category: category || 'general',
        is_active: true
      })
      .select('id')
      .single();

    if (error) {
      throw error;
    }

    return NextResponse.json({ success: true, id: data.id });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'Failed to create education material' }, { status: 500 });
  }
}



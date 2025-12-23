import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabaseClient';
import { requirePermission } from '@/lib/rbac';

export async function GET(request: NextRequest) {
  try {
    await requirePermission('analytics:appointments:read'); // veya 'audit:read' permission
    
    const { searchParams } = new URL(request.url);
    const userId = searchParams.get('userId');
    const patientId = searchParams.get('patientId');
    const action = searchParams.get('action');
    const limit = parseInt(searchParams.get('limit') || '50');
    const offset = parseInt(searchParams.get('offset') || '0');
    const startDate = searchParams.get('startDate');
    const endDate = searchParams.get('endDate');
    
    const supabase = await createSupabaseServerClient();
    
    let query = supabase
      .from('audit_logs')
      .select(`
        id,
        action,
        user_id,
        patient_id,
        appointment_id,
        ip,
        user_agent,
        context,
        created_at,
        user_profiles!inner(full_name, role)
      `)
      .order('created_at', { ascending: false })
      .range(offset, offset + limit - 1);
    
    if (userId) {
      query = query.eq('user_id', userId);
    }
    
    if (patientId) {
      query = query.eq('patient_id', patientId);
    }
    
    if (action) {
      query = query.eq('action', action);
    }
    
    if (startDate) {
      query = query.gte('created_at', startDate);
    }
    
    if (endDate) {
      query = query.lte('created_at', endDate);
    }
    
    const { data, error } = await query;
    
    if (error) {
      console.error('[audit-logs] fetch error', error);
      return NextResponse.json({ error: 'Audit logları alınamadı' }, { status: 500 });
    }
    
    return NextResponse.json({
      logs: data || [],
      pagination: {
        limit,
        offset,
        hasMore: (data?.length || 0) === limit
      }
    });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'Failed to fetch audit logs' }, { status: 500 });
  }
}











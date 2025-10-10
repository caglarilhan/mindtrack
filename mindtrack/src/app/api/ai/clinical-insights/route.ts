import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/utils/supabase/server';

export async function GET(request: NextRequest) {
  try {
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const patientId = searchParams.get('patientId');

    if (!patientId) {
      return NextResponse.json({ error: 'Patient ID is required' }, { status: 400 });
    }

    const { data: insights, error } = await supabase
      .from('ai_clinical_insights')
      .select('*')
      .eq('patient_id', patientId)
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Error fetching clinical insights:', error);
      return NextResponse.json({ error: 'Failed to fetch clinical insights' }, { status: 500 });
    }

    return NextResponse.json({ insights });
  } catch (error) {
    console.error('Error in clinical insights API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabaseClient';
import { requirePermission } from '@/lib/rbac';
import { writeAudit } from '@/lib/audit';

interface LabResult {
  id: string;
  patientId: string;
  testName: string;
  testCode: string;
  value: string | number;
  unit: string;
  referenceRange: string;
  status: 'normal' | 'abnormal' | 'critical';
  labDate: string;
  orderedBy: string;
  labProvider: string;
  notes?: string;
}

interface LabIntegrationRequest {
  patientId: string;
  testCodes?: string[];
  dateRange?: {
    start: string;
    end: string;
  };
  includeAbnormal?: boolean;
}

export async function GET(request: NextRequest) {
  try {
    await requirePermission('lab:results:read');
    
    const { searchParams } = new URL(request.url);
    const patientId = searchParams.get('patientId');
    const testCodes = searchParams.get('testCodes')?.split(',');
    const includeAbnormal = searchParams.get('includeAbnormal') === 'true';
    
    if (!patientId) {
      return NextResponse.json({ error: 'Patient ID is required' }, { status: 400 });
    }

    const supabase = await createSupabaseServerClient();
    
    // Fetch lab results from database
    let query = supabase
      .from('lab_results')
      .select('*')
      .eq('patient_id', patientId)
      .order('lab_date', { ascending: false });

    if (testCodes && testCodes.length > 0) {
      query = query.in('test_code', testCodes);
    }

    if (includeAbnormal) {
      query = query.in('status', ['abnormal', 'critical']);
    }

    const { data: results, error } = await query;

    if (error) {
      throw error;
    }

    // Audit log
    await writeAudit({
      action: 'lab.results.read',
      details: { 
        patientId,
        resultCount: results?.length || 0,
        testCodes: testCodes || 'all'
      },
      userId: 'system'
    });

    return NextResponse.json({
      success: true,
      results: results || [],
      summary: {
        totalResults: results?.length || 0,
        abnormalResults: results?.filter(r => r.status === 'abnormal').length || 0,
        criticalResults: results?.filter(r => r.status === 'critical').length || 0
      }
    });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'Failed to fetch lab results' }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    await requirePermission('lab:results:write');
    
    const labResult: LabResult = await request.json();
    
    if (!labResult.patientId || !labResult.testName || !labResult.value) {
      return NextResponse.json({ error: 'Patient ID, test name, and value are required' }, { status: 400 });
    }

    const supabase = await createSupabaseServerClient();
    
    // Insert lab result
    const { data, error } = await supabase
      .from('lab_results')
      .insert({
        patient_id: labResult.patientId,
        test_name: labResult.testName,
        test_code: labResult.testCode,
        value: labResult.value,
        unit: labResult.unit,
        reference_range: labResult.referenceRange,
        status: labResult.status,
        lab_date: labResult.labDate,
        ordered_by: labResult.orderedBy,
        lab_provider: labResult.labProvider,
        notes: labResult.notes
      })
      .select('id')
      .single();

    if (error) {
      throw error;
    }

    // Audit log
    await writeAudit({
      action: 'lab.results.create',
      details: { 
        labResultId: data.id,
        patientId: labResult.patientId,
        testName: labResult.testName,
        status: labResult.status
      },
      userId: 'system'
    });

    return NextResponse.json({
      success: true,
      labResultId: data.id
    });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'Failed to create lab result' }, { status: 500 });
  }
}

// Mock lab integration endpoint for testing
export async function PUT(request: NextRequest) {
  try {
    await requirePermission('lab:integration:sync');
    
    const { patientId, labProvider } = await request.json();
    
    if (!patientId) {
      return NextResponse.json({ error: 'Patient ID is required' }, { status: 400 });
    }

    // Mock lab integration - simulate fetching results from external lab
    const mockLabResults: LabResult[] = [
      {
        id: 'lab-001',
        patientId,
        testName: 'Complete Blood Count',
        testCode: 'CBC',
        value: 'Normal',
        unit: '',
        referenceRange: 'Normal',
        status: 'normal',
        labDate: new Date().toISOString(),
        orderedBy: 'Dr. Ahmet Yılmaz',
        labProvider: labProvider || 'Acibadem Lab',
        notes: 'Rutin kontrol'
      },
      {
        id: 'lab-002',
        patientId,
        testName: 'Lithium Level',
        testCode: 'LITH',
        value: 0.8,
        unit: 'mEq/L',
        referenceRange: '0.6-1.2',
        status: 'normal',
        labDate: new Date().toISOString(),
        orderedBy: 'Dr. Ahmet Yılmaz',
        labProvider: labProvider || 'Acibadem Lab',
        notes: 'Lithium tedavisi takibi'
      },
      {
        id: 'lab-003',
        patientId,
        testName: 'Liver Function Tests',
        testCode: 'LFT',
        value: 'Elevated ALT',
        unit: '',
        referenceRange: 'Normal',
        status: 'abnormal',
        labDate: new Date().toISOString(),
        orderedBy: 'Dr. Ahmet Yılmaz',
        labProvider: labProvider || 'Acibadem Lab',
        notes: 'İlaç yan etkisi kontrolü'
      }
    ];

    const supabase = await createSupabaseServerClient();
    
    // Insert mock results
    const { data, error } = await supabase
      .from('lab_results')
      .insert(mockLabResults.map(result => ({
        patient_id: result.patientId,
        test_name: result.testName,
        test_code: result.testCode,
        value: result.value,
        unit: result.unit,
        reference_range: result.referenceRange,
        status: result.status,
        lab_date: result.labDate,
        ordered_by: result.orderedBy,
        lab_provider: result.labProvider,
        notes: result.notes
      })))
      .select('id');

    if (error) {
      throw error;
    }

    // Audit log
    await writeAudit({
      action: 'lab.integration.sync',
      details: { 
        patientId,
        labProvider: labProvider || 'Acibadem Lab',
        syncedResults: data?.length || 0
      },
      userId: 'system'
    });

    return NextResponse.json({
      success: true,
      syncedResults: data?.length || 0,
      results: mockLabResults
    });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'Failed to sync lab results' }, { status: 500 });
  }
}



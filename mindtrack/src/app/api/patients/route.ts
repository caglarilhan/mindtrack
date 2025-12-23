import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/utils/supabase/server';
import { requirePermission } from '@/lib/rbac';

export type PatientMode = 'full' | 'lite';

interface CreatePatientRequest {
  mode: PatientMode;
  // Full mode fields
  firstName?: string;
  lastName?: string;
  email?: string;
  phone?: string;
  dateOfBirth?: string;
  address?: string;
  emergencyContact?: string;
  insuranceInfo?: Record<string, any>;
  medicalHistory?: string[];
  allergies?: string[];
  medications?: string[];
  // Lite mode fields
  pseudoName?: string; // e.g., "Client #14"
  ageRange?: string; // e.g., "25-30"
  gender?: string; // optional
  encryptedLocalNotes?: boolean; // default true for lite
  // Common fields
  therapistId?: string;
  clinicId?: string;
}

export async function POST(request: NextRequest) {
  try {
    await requirePermission('patients:write');
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const body: CreatePatientRequest = await request.json();
    const { mode } = body;

    if (!mode || !['full', 'lite'].includes(mode)) {
      return NextResponse.json({ error: 'mode must be "full" or "lite"' }, { status: 400 });
    }

    // Validation based on mode
    if (mode === 'full') {
      if (!body.firstName || !body.lastName || !body.email) {
        return NextResponse.json({ 
          error: 'Full mode requires firstName, lastName, and email' 
        }, { status: 400 });
      }
    } else if (mode === 'lite') {
      // Lite mode: pseudoName is optional, can be auto-generated
      if (!body.pseudoName) {
        // Generate pseudo name: "Client #" + random number
        body.pseudoName = `Client #${Math.floor(Math.random() * 10000)}`;
      }
    }

    // Get user's clinic_id
    const { data: userProfile } = await supabase
      .from('user_profiles')
      .select('clinic_id')
      .eq('user_id', user.id)
      .single();

    const clinicId = body.clinicId || userProfile?.clinic_id;

    // Build patient payload based on mode
    const patientPayload: any = {
      mode,
      clinic_id: clinicId,
      created_by: user.id,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };

    if (mode === 'full') {
      patientPayload.first_name = body.firstName;
      patientPayload.last_name = body.lastName;
      patientPayload.email = body.email;
      patientPayload.phone = body.phone || null;
      patientPayload.date_of_birth = body.dateOfBirth || null;
      patientPayload.address = body.address || null;
      patientPayload.emergency_contact = body.emergencyContact || null;
      patientPayload.insurance_info = body.insuranceInfo || {};
      patientPayload.medical_history = body.medicalHistory || [];
      patientPayload.allergies = body.allergies || [];
      patientPayload.medications = body.medications || [];
      patientPayload.pseudo_name = null;
      patientPayload.encrypted_local_notes = false;
    } else {
      // Lite mode
      patientPayload.pseudo_name = body.pseudoName;
      patientPayload.age_range = body.ageRange || null;
      patientPayload.gender = body.gender || null;
      patientPayload.encrypted_local_notes = body.encryptedLocalNotes !== false; // default true
      // Full mode fields are null
      patientPayload.first_name = null;
      patientPayload.last_name = null;
      patientPayload.email = null;
      patientPayload.phone = null;
      patientPayload.date_of_birth = null;
      patientPayload.address = null;
      patientPayload.emergency_contact = null;
    }

    const { data: patient, error } = await supabase
      .from('patients')
      .insert(patientPayload)
      .select()
      .single();

    if (error) {
      console.error('Error creating patient:', error);
      return NextResponse.json({ error: 'Failed to create patient' }, { status: 500 });
    }

    return NextResponse.json({ 
      success: true,
      patient: {
        id: patient.id,
        mode: patient.mode,
        name: mode === 'full' 
          ? `${patient.first_name} ${patient.last_name}` 
          : patient.pseudo_name,
        email: patient.email,
        createdAt: patient.created_at
      }
    });
  } catch (error) {
    console.error('Error in patient creation API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function GET(request: NextRequest) {
  try {
    await requirePermission('patients:read');
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { searchParams } = new URL(request.url);
    const clinicId = searchParams.get('clinicId');
    const mode = searchParams.get('mode') as PatientMode | null;
    const limit = parseInt(searchParams.get('limit') || '50');
    const offset = parseInt(searchParams.get('offset') || '0');

    let query = supabase
      .from('patients')
      .select('id, mode, first_name, last_name, pseudo_name, email, phone, created_at, clinic_id')
      .order('created_at', { ascending: false })
      .range(offset, offset + limit - 1);

    if (clinicId) {
      query = query.eq('clinic_id', clinicId);
    }

    if (mode) {
      query = query.eq('mode', mode);
    }

    const { data: patients, error } = await query;

    if (error) {
      console.error('Error fetching patients:', error);
      return NextResponse.json({ error: 'Failed to fetch patients' }, { status: 500 });
    }

    // Format response based on mode
    const formattedPatients = patients?.map(p => ({
      id: p.id,
      mode: p.mode,
      name: p.mode === 'full' 
        ? `${p.first_name} ${p.last_name}` 
        : p.pseudo_name,
      email: p.email,
      phone: p.phone,
      createdAt: p.created_at
    })) || [];

    return NextResponse.json({ 
      patients: formattedPatients,
      pagination: {
        limit,
        offset,
        hasMore: (patients?.length || 0) === limit
      }
    });
  } catch (error) {
    console.error('Error in patient list API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}











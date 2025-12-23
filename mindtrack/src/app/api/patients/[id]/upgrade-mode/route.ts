import { NextRequest, NextResponse } from 'next/server';
import { createClient } from '@/utils/supabase/server';
import { requirePermission } from '@/lib/rbac';

export async function POST(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    await requirePermission('patients:write');
    const supabase = await createClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();

    if (authError || !user) {
      return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
    }

    const { id } = params;
    const body = await request.json();
    const { firstName, lastName, email, phone, dateOfBirth, address, emergencyContact, insuranceInfo } = body;

    // Get current patient
    const { data: patient, error: fetchError } = await supabase
      .from('patients')
      .select('*')
      .eq('id', id)
      .single();

    if (fetchError || !patient) {
      return NextResponse.json({ error: 'Patient not found' }, { status: 404 });
    }

    if (patient.mode === 'full') {
      return NextResponse.json({ error: 'Patient is already in full mode' }, { status: 400 });
    }

    // Validate required fields for full mode
    if (!firstName || !lastName || !email) {
      return NextResponse.json({ 
        error: 'Upgrade to full mode requires firstName, lastName, and email' 
      }, { status: 400 });
    }

    // Upgrade to full mode
    const { data: updatedPatient, error: updateError } = await supabase
      .from('patients')
      .update({
        mode: 'full',
        first_name: firstName,
        last_name: lastName,
        email,
        phone: phone || null,
        date_of_birth: dateOfBirth || null,
        address: address || null,
        emergency_contact: emergencyContact || null,
        insurance_info: insuranceInfo || {},
        // Keep pseudo_name for reference, but it's no longer primary
        updated_at: new Date().toISOString(),
        mode_upgraded_at: new Date().toISOString(),
        mode_upgraded_by: user.id
      })
      .eq('id', id)
      .select()
      .single();

    if (updateError) {
      console.error('Error upgrading patient mode:', updateError);
      return NextResponse.json({ error: 'Failed to upgrade patient mode' }, { status: 500 });
    }

    // Log the upgrade in audit logs
    await supabase.from('audit_logs').insert({
      action: 'patient.mode.upgrade',
      user_id: user.id,
      patient_id: id,
      context: {
        from: 'lite',
        to: 'full',
        previousPseudoName: patient.pseudo_name
      },
      created_at: new Date().toISOString()
    }).catch(() => {}); // Ignore audit log errors

    return NextResponse.json({ 
      success: true,
      patient: {
        id: updatedPatient.id,
        mode: updatedPatient.mode,
        name: `${updatedPatient.first_name} ${updatedPatient.last_name}`,
        email: updatedPatient.email,
        upgradedAt: updatedPatient.mode_upgraded_at
      },
      message: 'Patient successfully upgraded to full mode. GDPR consent may be required.'
    });
  } catch (error) {
    console.error('Error in patient mode upgrade API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}











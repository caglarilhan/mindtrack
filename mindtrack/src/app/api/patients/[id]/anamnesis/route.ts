import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabaseClient';
import { encryptAnamnesis, decryptAnamnesisWithPassphrase, decryptAnamnesisAsAdmin, type EncryptedAnamnesis } from '@/lib/crypto-anamnesis';
import { requirePermission } from '@/lib/rbac';
import { writeAudit } from '@/lib/audit';

type EncryptionMode = 'record' | 'patient' | 'clinic';

// POST: save encrypted anamnesis
export async function POST(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    await requirePermission('patient:anamnesis:write');
    const supabase = await createSupabaseServerClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const patientId = params.id;
    const body = await req.json();
    const plaintext = String(body?.text || '');
    const passphrase = String(body?.passphrase || '');
    const mode: EncryptionMode = (body?.mode as EncryptionMode) || 'record';
    if (!plaintext || !passphrase) return NextResponse.json({ error: 'text and passphrase required' }, { status: 400 });

    const payload = encryptAnamnesis(plaintext, passphrase);
    const { error } = await supabase
      .from('patient_anamnesis')
      .upsert({ patient_id: patientId, payload, mode }, { onConflict: 'patient_id' });
    if (error) throw error;
    await writeAudit({ action: 'patient.anamnesis.write', patientId, ip: req.ip, userAgent: req.headers.get('user-agent') });
    return NextResponse.json({ success: true, mode });
  } catch (error) {
    console.error('POST anamnesis error', error);
    return NextResponse.json({ error: 'Failed to save anamnesis' }, { status: 500 });
  }
}

// GET: masked preview (no decryption)
export async function GET(
  _req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    await requirePermission('patient:anamnesis:read');
    const supabase = await createSupabaseServerClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const patientId = params.id;
    const { data, error } = await supabase
      .from('patient_anamnesis')
      .select('payload, mode')
      .eq('patient_id', patientId)
      .single();
    if (error && error.code !== 'PGRST116') throw error;
    const payload = data?.payload as EncryptedAnamnesis | undefined;
    if (!payload) return NextResponse.json({ exists: false });
    // masked: return only ciphertext length and first chars shuffled
    const ct = Buffer.from(payload.ciphertextB64, 'base64').toString('base64');
    const masked = ct.slice(0, 24).split('').sort(() => Math.random() - 0.5).join('');
    await writeAudit({ action: 'patient.anamnesis.read', patientId, ip: _req.ip, userAgent: _req.headers.get('user-agent') });
    return NextResponse.json({ exists: true, maskedPreview: `${masked}…`, length: ct.length, mode: data?.mode || 'record' });
  } catch (error) {
    console.error('GET anamnesis error', error);
    return NextResponse.json({ error: 'Failed to fetch anamnesis' }, { status: 500 });
  }
}

// POST /decrypt: user passphrase or admin
export async function PUT(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    await requirePermission('patient:anamnesis:decrypt:user');
    const supabase = await createSupabaseServerClient();
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    if (authError || !user) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

    const patientId = params.id;
    const body = await req.json();
    const asAdmin = body?.asAdmin === true;
    const passphrase = body?.passphrase as string | undefined;
    const mode: EncryptionMode | undefined = body?.mode as EncryptionMode | undefined;

    const { data, error } = await supabase
      .from('patient_anamnesis')
      .select('payload, mode')
      .eq('patient_id', patientId)
      .single();
    if (error) throw error;
    const payload = data?.payload as EncryptedAnamnesis;
    if (!payload) return NextResponse.json({ error: 'No anamnesis' }, { status: 404 });

    let plaintext = '';
    if (asAdmin) {
      await requirePermission('patient:anamnesis:decrypt:admin');
      // Admin görür, kullanıcı bilmez
      plaintext = decryptAnamnesisAsAdmin(payload);
      await writeAudit({ action: 'patient.anamnesis.decrypt.admin', patientId, ip: req.ip, userAgent: req.headers.get('user-agent') });
    } else {
      if (!passphrase) return NextResponse.json({ error: 'passphrase required' }, { status: 400 });
      plaintext = decryptAnamnesisWithPassphrase(payload, passphrase);
      await writeAudit({ action: 'patient.anamnesis.decrypt.user', patientId, ip: req.ip, userAgent: req.headers.get('user-agent') });
    }
    return NextResponse.json({ success: true, text: plaintext, mode: mode || data?.mode || 'record' });
  } catch (error: any) {
    console.error('PUT anamnesis decrypt error', error);
    return NextResponse.json({ error: error?.message || 'Failed to decrypt' }, { status: 500 });
  }
}



import { NextRequest, NextResponse } from 'next/server';
import { generateTelehealthLink, type TelehealthProvider } from '@/lib/telehealth';
import { requirePermission } from '@/lib/rbac';
import { writeAudit } from '@/lib/audit';

export async function POST(request: NextRequest) {
  try {
    await requirePermission('telehealth:link:create');
    const { provider, customUrl } = await request.json();
    const prov = (provider as TelehealthProvider) || 'custom';
    const result = generateTelehealthLink({ provider: prov, customUrl });
    await writeAudit({ action: 'telehealth.link.create', ip: request.ip, userAgent: request.headers.get('user-agent') });
    return NextResponse.json({ success: true, ...result });
  } catch (error) {
    console.error('telehealth/link error', error);
    return NextResponse.json({ success: false, error: 'Failed to generate link' }, { status: 500 });
  }
}





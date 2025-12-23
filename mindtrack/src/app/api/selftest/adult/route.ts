import { NextRequest, NextResponse } from 'next/server';
import { encryptAnamnesis, decryptAnamnesisWithPassphrase } from '@/lib/crypto-anamnesis';
import { generateTelehealthLink } from '@/lib/telehealth';
import { selectForPatientAndAppointment } from '@/lib/notifications/autoSelect';
import { enqueueDelivery } from '@/lib/queue';

export async function GET(_req: NextRequest) {
  try {
    // Crypto test
    const sample = 'Deneme anamnez metni';
    const enc = encryptAnamnesis(sample, 'test-pass');
    const dec = decryptAnamnesisWithPassphrase(enc, 'test-pass');

    // Telehealth test
    const link = generateTelehealthLink({ provider: 'custom' });

    // Auto-select (dummy patient)
    const auto = await selectForPatientAndAppointment('test-patient');

    // Queue test
    await enqueueDelivery({ channel: 'email', payload: { to: process.env.TEST_EMAIL || 'test@example.com', subject: 'Selftest', body: 'Hello from queue' }, delaySeconds: 1 });

    // Appointment create test (if possible)
    // Not: DB izinleri varsa bir dummy randevu oluşturur
    let createdAppt: string | null = null;
    try {
      const res = await fetch(new URL('/api/appointments/create', 'http://localhost:3000'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ patientId: 'test-p-1', startAt: new Date(Date.now()+3600_000).toISOString(), type: 'consult', location: 'Telehealth' }) });
      const j = await res.json();
      if (j?.success) createdAppt = j.id;
    } catch (_) {}

    // Expand recurrence: weekly 2 copies
    let expanded = 0;
    if (createdAppt) {
      try {
        const res2 = await fetch(new URL('/api/appointments/expand', 'http://localhost:3000'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ baseId: createdAppt, freq: 'WEEKLY', count: 2 }) });
        const e2 = await res2.json();
        if (e2?.success) expanded = (e2.created || []).length;
      } catch (_) {}
    }

    // Update status
    let statusUpdated = false;
    if (createdAppt) {
      try {
        const res3 = await fetch(new URL('/api/appointments/status', 'http://localhost:3000'), { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: createdAppt, status: 'completed' }) });
        const s3 = await res3.json();
        statusUpdated = !!s3?.success;
      } catch (_) {}
    }

    // Test education materials API
    let educationOk = false;
    try {
      const eduRes = await fetch(new URL('/api/education-materials', 'http://localhost:3000'), { method: 'GET' });
      const eduData = await eduRes.json();
      educationOk = Array.isArray(eduData?.materials);
    } catch (_) {}

    // Test patient messages API
    let messagesOk = false;
    try {
      const msgRes = await fetch(new URL('/api/patient-messages?patientId=test-p-1', 'http://localhost:3000'), { method: 'GET' });
      const msgData = await msgRes.json();
      messagesOk = Array.isArray(msgData?.messages);
    } catch (_) {}

    // Test analytics APIs
    let analyticsOk = { patients: false, appointments: false, medications: false, compliance: false };
    try {
      const analyticsRes = await Promise.all([
        fetch(new URL('/api/analytics/patients?period=30d', 'http://localhost:3000')),
        fetch(new URL('/api/analytics/appointments?period=30d', 'http://localhost:3000')),
        fetch(new URL('/api/analytics/medications?period=30d', 'http://localhost:3000')),
        fetch(new URL('/api/analytics/compliance?period=30d', 'http://localhost:3000'))
      ]);
      
      const analyticsData = await Promise.all(analyticsRes.map(res => res.json()));
      analyticsOk = {
        patients: !!analyticsData[0]?.summary,
        appointments: !!analyticsData[1]?.summary,
        medications: !!analyticsData[2]?.summary,
        compliance: !!analyticsData[3]?.overallScore
      };
    } catch (_) {}

    // Test advanced features APIs
    let advancedOk = { clinical: false, interactions: false, lab: false };
    try {
      // Test AI Clinical Decision
      const clinicalRes = await fetch(new URL('/api/ai/clinical-decision', 'http://localhost:3000'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patientAge: 35,
          patientGender: 'female',
          symptoms: ['kaygı', 'uyku bozukluğu'],
          currentMedications: ['Sertraline'],
          medicalHistory: ['depresyon']
        })
      });
      const clinicalData = await clinicalRes.json();
      advancedOk.clinical = !!clinicalData?.recommendation;

      // Test Drug Interactions
      const interactionsRes = await fetch(new URL('/api/medications/interactions', 'http://localhost:3000'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          medications: ['Sertraline', 'Fluoxetine'],
          patientAge: 35
        })
      });
      const interactionsData = await interactionsRes.json();
      advancedOk.interactions = !!interactionsData?.result;

      // Test Lab Integration
      const labRes = await fetch(new URL('/api/lab/results', 'http://localhost:3000'), {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patientId: 'test-patient-001',
          labProvider: 'Acibadem Lab'
        })
      });
      const labData = await labRes.json();
      advancedOk.lab = !!labData?.success;
    } catch (_) {}

    return NextResponse.json({
      crypto: { ok: dec === sample },
      telehealth: { url: link.url },
      autoSelect: { language: auto.language, email: !!auto.email, sms: !!auto.sms },
      queue: { enqueued: true },
      appointmentCreate: { ok: !!createdAppt, id: createdAppt },
      recurrence: { expanded },
      status: { updated: statusUpdated },
      education: { ok: educationOk },
      messages: { ok: messagesOk },
      analytics: analyticsOk,
      advanced: advancedOk
    });
  } catch (e: any) {
    return NextResponse.json({ error: e?.message || 'selftest failed' }, { status: 500 });
  }
}



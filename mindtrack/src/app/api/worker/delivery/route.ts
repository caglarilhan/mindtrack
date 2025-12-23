import { NextRequest, NextResponse } from 'next/server';
import { claimNextBatch, completeJob, retryJob } from '@/lib/queue';
import { sendEmail } from '@/lib/notifications/email';
import { sendSMS } from '@/lib/notifications/sms';
import { logDelivery } from '@/lib/notifications/log';

export async function POST(_req: NextRequest) {
  const workerId = `worker-${process.pid}-${Date.now()}`;
  const jobs = await claimNextBatch(workerId, 10);
  for (const j of jobs) {
    try {
      if (j.channel === 'email') {
        await sendEmail({ to: j.payload.to, subject: j.payload.subject, text: j.payload.body, html: `<p>${j.payload.body}</p>` });
        await logDelivery({ channel: 'email', provider: 'sendgrid', to: j.payload.to, subject: j.payload.subject, body: j.payload.body, status: 'sent' });
      } else {
        await sendSMS({ to: j.payload.to, body: j.payload.body, provider: j.payload.provider });
        await logDelivery({ channel: 'sms', provider: j.payload.provider || 'twilio', to: j.payload.to, body: j.payload.body, status: 'sent' });
      }
      await completeJob(j.id);
    } catch (e: any) {
      const attempts = j.attempts || 0;
      await logDelivery({ channel: j.channel, provider: j.payload.provider || 'unknown', to: j.payload.to, subject: j.payload.subject, body: j.payload.body, status: 'failed', error: e?.message });
      await retryJob(j.id, attempts, Math.min(300, (attempts + 1) * 60));
    }
  }
  return NextResponse.json({ success: true, processed: jobs.length });
}





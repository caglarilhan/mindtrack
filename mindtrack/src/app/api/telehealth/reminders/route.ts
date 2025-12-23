import { NextRequest, NextResponse } from 'next/server';
import { sendEmail } from '@/lib/notifications/email';
import { sendSMS } from '@/lib/notifications/sms';
import { selectForPatientAndAppointment } from '@/lib/notifications/autoSelect';
import { requirePermission } from '@/lib/rbac';
import { writeAudit } from '@/lib/audit';
import { renderTemplate } from '@/lib/templates';
import { logDelivery } from '@/lib/notifications/log';

export async function POST(request: NextRequest) {
  try {
    await requirePermission('telehealth:reminder:send');
    const { email, phone, subject, message, link, patientId, appointmentId } = await request.json();
    const tasks: Promise<any>[] = [];

    if (patientId) {
      const auto = await selectForPatientAndAppointment(patientId, appointmentId);
      const vars = { link: link || '', language: auto.language } as Record<string, string>;
      const resolvedSubject = renderTemplate(auto.email?.subject || subject || 'Tele‑seans Hatırlatma', vars);
      const resolvedEmailText = renderTemplate(message || auto.email?.text || 'Seansınız yakında başlayacaktır. Bağlantı: {{link}}', vars);
      const resolvedSMSText = renderTemplate(message || auto.sms?.body || 'Seansınız yakında başlayacaktır. Bağlantı: {{link}}', vars);

      if (auto.email?.to) {
        tasks.push(
          sendEmail({ to: auto.email.to, subject: resolvedSubject, text: resolvedEmailText, html: `<p>${resolvedEmailText}</p>` })
            .then(() => logDelivery({ channel: 'email', provider: 'sendgrid', to: auto.email!.to, subject: resolvedSubject, body: resolvedEmailText, status: 'sent' }))
            .catch((e) => logDelivery({ channel: 'email', provider: 'sendgrid', to: auto.email!.to, subject: resolvedSubject, body: resolvedEmailText, status: 'failed', error: e?.message }))
        );
      }
      if (auto.sms?.to) {
        tasks.push(
          sendSMS({ to: auto.sms.to, body: resolvedSMSText, provider: auto.sms.provider as any })
            .then(() => logDelivery({ channel: 'sms', provider: auto.sms!.provider, to: auto.sms!.to, body: resolvedSMSText, status: 'sent' }))
            .catch(async (e) => {
              await logDelivery({ channel: 'sms', provider: auto.sms!.provider, to: auto.sms!.to, body: resolvedSMSText, status: 'failed', error: e?.message });
              // fallback: Twilio -> MessageBird -> Vonage sırası
              const providers: any[] = ['twilio', 'messagebird', 'vonage'];
              const startIdx = providers.indexOf(auto.sms!.provider);
              for (let i = 1; i < providers.length; i++) {
                const p = providers[(startIdx + i) % providers.length];
                try {
                  await sendSMS({ to: auto.sms!.to, body: resolvedSMSText, provider: p });
                  await logDelivery({ channel: 'sms', provider: p, to: auto.sms!.to, body: resolvedSMSText, status: 'sent' });
                  break;
                } catch (err: any) {
                  await logDelivery({ channel: 'sms', provider: p, to: auto.sms!.to, body: resolvedSMSText, status: 'failed', error: err?.message });
                }
              }
            })
        );
      }
    }

    if (email) {
      tasks.push(
        sendEmail({
          to: email,
          subject: subject || 'Telehealth Session Reminder',
          html: `<p>${message || 'Your session is scheduled soon.'}</p>${link ? `<p><a href="${link}">Join Session</a></p>` : ''}`,
          text: `${message || 'Your session is scheduled soon.'}${link ? `\nJoin: ${link}` : ''}`
        })
      );
    }

    if (phone) {
      tasks.push(
        sendSMS({
          to: phone,
          body: `${message || 'Your session is scheduled soon.'}${link ? `\nJoin: ${link}` : ''}`
        })
      );
    }

    if (tasks.length === 0) {
      return NextResponse.json({ error: 'email or phone required' }, { status: 400 });
    }

    await Promise.all(tasks);
    await writeAudit({ action: 'telehealth.reminder.send', patientId, appointmentId, ip: request.ip, userAgent: request.headers.get('user-agent') });
    return NextResponse.json({ success: true });
  } catch (error: any) {
    console.error('telehealth/reminders error', error);
    return NextResponse.json({ success: false, error: error?.message || 'Failed to send reminders' }, { status: 500 });
  }
}



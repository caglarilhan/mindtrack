import sendgrid from '@sendgrid/mail';

const apiKey = process.env.SENDGRID_API_KEY;
if (apiKey) {
  sendgrid.setApiKey(apiKey);
}

export interface SendEmailInput {
  to: string;
  subject: string;
  html?: string;
  text?: string;
  from?: string;
}

export async function sendEmail(input: SendEmailInput) {
  if (!apiKey) throw new Error('SENDGRID_API_KEY is not configured');
  const from = input.from || process.env.EMAIL_FROM || 'no-reply@mindtrack.app';
  const msg = {
    to: input.to,
    from,
    subject: input.subject,
    text: input.text,
    html: input.html || input.text || ''
  };
  await sendgrid.send(msg);
}






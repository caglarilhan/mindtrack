import Twilio from 'twilio';
import { sendSMSMessageBird } from './messagebird';
import { sendSMSVonage } from './vonage';

const accountSid = process.env.TWILIO_ACCOUNT_SID;
const authToken = process.env.TWILIO_AUTH_TOKEN;
const fromNumber = process.env.TWILIO_FROM_NUMBER;

let client: Twilio.Twilio | null = null;
if (accountSid && authToken) {
  client = Twilio(accountSid, authToken);
}

export interface SendSMSInput {
  to: string;
  body: string;
  provider?: 'twilio' | 'messagebird' | 'vonage' | 'sinch';
}

export async function sendSMS(input: SendSMSInput) {
  // Provider seçimi
  if (input.provider === 'messagebird') {
    return sendSMSMessageBird(input.to, input.body);
  }
  if (input.provider === 'vonage') {
    return sendSMSVonage(input.to, input.body);
  }
  // default Twilio
  if (!client || !fromNumber) throw new Error('Twilio not configured');
  await client.messages.create({ to: input.to, from: fromNumber, body: input.body });
}



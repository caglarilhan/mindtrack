/**
 * Email templates index
 * Centralized template exports
 */

import { renderSOAPTemplate, renderSOAPTextTemplate, type SOAPEmailData } from "./soap";
import { renderRiskTemplate, renderRiskTextTemplate, type RiskEmailData } from "./risk";
import { renderAppointmentTemplate, renderAppointmentTextTemplate, type AppointmentEmailData } from "./appointment";
import { renderShareTemplate, renderShareTextTemplate, type ShareEmailData } from "./share";

export type { SOAPEmailData, RiskEmailData, AppointmentEmailData, ShareEmailData };

export const EMAIL_TEMPLATES = {
  soapNote: (data: SOAPEmailData) => ({
    subject: `SOAP Notu - ${data.clientName}`,
    html: renderSOAPTemplate(data),
    text: renderSOAPTextTemplate(data),
  }),
  
  riskAlert: (data: RiskEmailData) => ({
    subject: `⚠️ Risk Uyarısı - ${data.clientName}`,
    html: renderRiskTemplate(data),
    text: renderRiskTextTemplate(data),
  }),
  
  appointmentReminder: (data: AppointmentEmailData) => ({
    subject: `Randevu Hatırlatması - ${data.clientName}`,
    html: renderAppointmentTemplate(data),
    text: renderAppointmentTextTemplate(data),
  }),
  
  shareLink: (data: ShareEmailData) => ({
    subject: `Paylaşım Linki - ${data.itemType}`,
    html: renderShareTemplate(data),
    text: renderShareTextTemplate(data),
  }),
} as const;






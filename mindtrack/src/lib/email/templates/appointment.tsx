/**
 * Appointment reminder email template
 */

import { BaseEmailTemplate } from "./base";

export interface AppointmentEmailData {
  clientName: string;
  appointmentDate: string;
  appointmentTime: string;
  therapistName: string;
  telehealthLink?: string;
  cancelLink?: string;
  location?: string;
  notes?: string;
}

export function renderAppointmentTemplate(data: AppointmentEmailData): string {
  const content = `
    <p>Merhaba <strong>${data.clientName}</strong>,</p>
    <p>Randevunuz hakkında hatırlatma:</p>
    
    <div style="margin: 20px 0; padding: 20px; background-color: #f3f4f6; border-radius: 8px;">
      <h2 style="margin-top: 0; color: #4f46e5;">📅 Randevu Detayları</h2>
      <p style="margin: 10px 0;"><strong>Tarih:</strong> ${new Date(data.appointmentDate).toLocaleDateString("tr-TR", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}</p>
      <p style="margin: 10px 0;"><strong>Saat:</strong> ${data.appointmentTime}</p>
      <p style="margin: 10px 0;"><strong>Terapist:</strong> ${data.therapistName}</p>
      ${data.location ? `<p style="margin: 10px 0;"><strong>Konum:</strong> ${data.location}</p>` : ""}
    </div>
    
    ${data.telehealthLink ? `
      <div style="margin: 20px 0; padding: 15px; background-color: #eff6ff; border-left: 4px solid #3b82f6; border-radius: 4px;">
        <h3 style="color: #3b82f6; margin-top: 0;">💻 Telehealth Seansı</h3>
        <p>Bu randevu online olarak yapılacaktır. Aşağıdaki linke tıklayarak seansa katılabilirsiniz:</p>
        <p style="word-break: break-all;"><a href="${data.telehealthLink}" style="color: #3b82f6; font-weight: 600;">${data.telehealthLink}</a></p>
      </div>
    ` : ""}
    
    ${data.notes ? `
      <div style="margin: 20px 0;">
        <h3>Notlar:</h3>
        <p style="background-color: #f3f4f6; padding: 15px; border-radius: 4px; white-space: pre-wrap;">
          ${data.notes}
        </p>
      </div>
    ` : ""}
    
    ${data.cancelLink ? `
      <div style="margin: 20px 0; padding: 15px; background-color: #fef2f2; border-left: 4px solid #dc2626; border-radius: 4px;">
        <p style="margin: 0;">Randevuyu iptal etmek isterseniz: <a href="${data.cancelLink}" style="color: #dc2626;">İptal Et</a></p>
      </div>
    ` : ""}
    
    <p style="margin-top: 30px;">
      Randevu saatinden 15 dakika önce hazır olmanızı öneririz.
    </p>
  `;

  return BaseEmailTemplate({
    title: "Randevu Hatırlatması",
    content,
    buttonText: data.telehealthLink ? "Seansa Katıl" : undefined,
    buttonLink: data.telehealthLink,
  });
}

export function renderAppointmentTextTemplate(data: AppointmentEmailData): string {
  return `
Randevu Hatırlatması

Merhaba ${data.clientName},

Randevunuz hakkında hatırlatma:

📅 Randevu Detayları
Tarih: ${new Date(data.appointmentDate).toLocaleDateString("tr-TR", { weekday: "long", year: "numeric", month: "long", day: "numeric" })}
Saat: ${data.appointmentTime}
Terapist: ${data.therapistName}
${data.location ? `Konum: ${data.location}` : ""}

${data.telehealthLink ? `
💻 Telehealth Seansı
Bu randevu online olarak yapılacaktır. Aşağıdaki linke tıklayarak seansa katılabilirsiniz:
${data.telehealthLink}
` : ""}

${data.notes ? `\nNotlar:\n${data.notes}` : ""}

${data.cancelLink ? `\nRandevuyu iptal etmek isterseniz: ${data.cancelLink}` : ""}

Randevu saatinden 15 dakika önce hazır olmanızı öneririz.

---
MindTrack - https://mindtrack.app
  `.trim();
}






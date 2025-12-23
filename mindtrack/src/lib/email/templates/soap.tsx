/**
 * SOAP Note email template
 */

import { BaseEmailTemplate } from "./base";

export interface SOAPEmailData {
  clientName: string;
  date: string;
  soap: {
    subjective: string;
    objective: string;
    assessment: string;
    plan: string;
  };
  riskLevel?: "low" | "medium" | "high" | "critical";
  shareLink?: string;
  pdfUrl?: string;
}

export function renderSOAPTemplate(data: SOAPEmailData): string {
  const riskBadge = data.riskLevel
    ? `<div style="background-color: ${
        data.riskLevel === "critical" ? "#dc2626" :
        data.riskLevel === "high" ? "#ea580c" :
        data.riskLevel === "medium" ? "#f59e0b" : "#10b981"
      }; color: white; padding: 8px 16px; border-radius: 4px; display: inline-block; margin-bottom: 20px; font-weight: 600;">
        Risk Seviyesi: ${data.riskLevel.toUpperCase()}
      </div>`
    : "";

  const content = `
    <p>Merhaba,</p>
    <p><strong>${data.clientName}</strong> için SOAP notu oluşturuldu.</p>
    <p><strong>Tarih:</strong> ${new Date(data.date).toLocaleDateString("tr-TR")}</p>
    
    ${riskBadge}
    
    <div style="margin: 20px 0;">
      <h3 style="color: #4f46e5; border-bottom: 2px solid #4f46e5; padding-bottom: 8px;">
        📝 Subjective (Öznel)
      </h3>
      <p style="background-color: #f3f4f6; padding: 15px; border-radius: 4px; white-space: pre-wrap;">
        ${data.soap.subjective || "(Boş)"}
      </p>
    </div>
    
    <div style="margin: 20px 0;">
      <h3 style="color: #10b981; border-bottom: 2px solid #10b981; padding-bottom: 8px;">
        👁️ Objective (Nesnel)
      </h3>
      <p style="background-color: #f3f4f6; padding: 15px; border-radius: 4px; white-space: pre-wrap;">
        ${data.soap.objective || "(Boş)"}
      </p>
    </div>
    
    <div style="margin: 20px 0;">
      <h3 style="color: #f59e0b; border-bottom: 2px solid #f59e0b; padding-bottom: 8px;">
        🔍 Assessment (Değerlendirme)
      </h3>
      <p style="background-color: #f3f4f6; padding: 15px; border-radius: 4px; white-space: pre-wrap;">
        ${data.soap.assessment || "(Boş)"}
      </p>
    </div>
    
    <div style="margin: 20px 0;">
      <h3 style="color: #8b5cf6; border-bottom: 2px solid #8b5cf6; padding-bottom: 8px;">
        📋 Plan (Plan)
      </h3>
      <p style="background-color: #f3f4f6; padding: 15px; border-radius: 4px; white-space: pre-wrap;">
        ${data.soap.plan || "(Boş)"}
      </p>
    </div>
    
    ${data.shareLink ? `
      <div style="margin: 20px 0; padding: 15px; background-color: #eff6ff; border-radius: 4px; border-left: 4px solid #3b82f6;">
        <p style="margin: 0 0 10px 0;"><strong>Paylaşım Linki:</strong></p>
        <p style="margin: 0; word-break: break-all;"><a href="${data.shareLink}" style="color: #3b82f6;">${data.shareLink}</a></p>
      </div>
    ` : ""}
    
    <p style="margin-top: 30px;">
      <em>Bu email otomatik olarak oluşturulmuştur. Lütfen gizlilik kurallarına dikkat edin.</em>
    </p>
  `;

  return BaseEmailTemplate({
    title: `SOAP Notu - ${data.clientName}`,
    content,
    buttonText: data.shareLink ? "SOAP Notunu Görüntüle" : undefined,
    buttonLink: data.shareLink,
  });
}

export function renderSOAPTextTemplate(data: SOAPEmailData): string {
  return `
SOAP Notu - ${data.clientName}
Tarih: ${new Date(data.date).toLocaleDateString("tr-TR")}

${data.riskLevel ? `Risk Seviyesi: ${data.riskLevel.toUpperCase()}\n` : ""}

📝 Subjective (Öznel)
${data.soap.subjective || "(Boş)"}

👁️ Objective (Nesnel)
${data.soap.objective || "(Boş)"}

🔍 Assessment (Değerlendirme)
${data.soap.assessment || "(Boş)"}

📋 Plan (Plan)
${data.soap.plan || "(Boş)"}

${data.shareLink ? `\nPaylaşım Linki: ${data.shareLink}` : ""}

---
Bu email otomatik olarak oluşturulmuştur.
MindTrack - https://mindtrack.app
  `.trim();
}






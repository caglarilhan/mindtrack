/**
 * Share link email template
 */

import { BaseEmailTemplate } from "./base";

export interface ShareEmailData {
  shareLink: string;
  qrCodeUrl?: string;
  itemType: "SOAP" | "Note" | "Report" | "Other";
  itemName?: string;
  expiresAt?: string;
  securityNote?: string;
}

export function renderShareTemplate(data: ShareEmailData): string {
  const content = `
    <p>Merhaba,</p>
    <p>Size bir ${data.itemType === "SOAP" ? "SOAP notu" : data.itemType === "Note" ? "not" : data.itemType === "Report" ? "rapor" : "dosya"} paylaşıldı.</p>
    
    ${data.itemName ? `<p><strong>İsim:</strong> ${data.itemName}</p>` : ""}
    
    <div style="margin: 20px 0; padding: 20px; background-color: #eff6ff; border-radius: 8px; text-align: center;">
      <h3 style="color: #3b82f6; margin-top: 0;">🔗 Paylaşım Linki</h3>
      <p style="word-break: break-all; font-size: 14px; margin: 15px 0;">
        <a href="${data.shareLink}" style="color: #3b82f6; font-weight: 600; text-decoration: none;">${data.shareLink}</a>
      </p>
      
      ${data.qrCodeUrl ? `
        <div style="margin: 20px 0;">
          <p style="margin-bottom: 10px;">QR Kod:</p>
          <img src="${data.qrCodeUrl}" alt="QR Code" style="max-width: 200px; border: 2px solid #3b82f6; border-radius: 8px; padding: 10px; background-color: white;" />
        </div>
      ` : ""}
    </div>
    
    ${data.expiresAt ? `
      <div style="margin: 20px 0; padding: 15px; background-color: #fffbeb; border-left: 4px solid #f59e0b; border-radius: 4px;">
        <p style="margin: 0;"><strong>⏰ Son Kullanma:</strong> ${new Date(data.expiresAt).toLocaleDateString("tr-TR")}</p>
      </div>
    ` : ""}
    
    ${data.securityNote ? `
      <div style="margin: 20px 0; padding: 15px; background-color: #fef2f2; border-left: 4px solid #dc2626; border-radius: 4px;">
        <h3 style="color: #dc2626; margin-top: 0;">🔒 Güvenlik Notları</h3>
        <p style="margin: 0; white-space: pre-wrap;">${data.securityNote}</p>
      </div>
    ` : `
      <div style="margin: 20px 0; padding: 15px; background-color: #f3f4f6; border-radius: 4px;">
        <h3 style="margin-top: 0;">🔒 Güvenlik Notları</h3>
        <ul style="margin: 10px 0; padding-left: 20px;">
          <li>Bu linki sadece güvendiğiniz kişilerle paylaşın</li>
          <li>Linki başkalarıyla paylaşmayın</li>
          <li>${data.expiresAt ? `Link ${new Date(data.expiresAt).toLocaleDateString("tr-TR")} tarihinde sona erecek` : "Link süresiz geçerlidir"}</li>
        </ul>
      </div>
    `}
    
    <p style="margin-top: 30px;">
      <em>Bu linke tıklayarak içeriği görüntüleyebilirsiniz.</em>
    </p>
  `;

  return BaseEmailTemplate({
    title: "Paylaşım Linki",
    content,
    buttonText: "İçeriği Görüntüle",
    buttonLink: data.shareLink,
  });
}

export function renderShareTextTemplate(data: ShareEmailData): string {
  return `
Paylaşım Linki

Merhaba,

Size bir ${data.itemType === "SOAP" ? "SOAP notu" : data.itemType === "Note" ? "not" : data.itemType === "Report" ? "rapor" : "dosya"} paylaşıldı.

${data.itemName ? `İsim: ${data.itemName}\n` : ""}

🔗 Paylaşım Linki
${data.shareLink}

${data.expiresAt ? `\n⏰ Son Kullanma: ${new Date(data.expiresAt).toLocaleDateString("tr-TR")}` : ""}

🔒 Güvenlik Notları
- Bu linki sadece güvendiğiniz kişilerle paylaşın
- Linki başkalarıyla paylaşmayın
- ${data.expiresAt ? `Link ${new Date(data.expiresAt).toLocaleDateString("tr-TR")} tarihinde sona erecek` : "Link süresiz geçerlidir"}

Bu linke tıklayarak içeriği görüntüleyebilirsiniz.

---
MindTrack - https://mindtrack.app
  `.trim();
}






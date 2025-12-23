/**
 * Risk Alert email template
 */

import { BaseEmailTemplate } from "./base";

export interface RiskEmailData {
  clientName: string;
  riskLevel: "low" | "medium" | "high" | "critical";
  detectedKeywords: string[];
  contextSnippet?: string;
  sessionDate?: string;
  recommendedActions?: string[];
  emergencyContact?: string;
}

export function renderRiskTemplate(data: RiskEmailData): string {
  const riskColors = {
    critical: { bg: "#dc2626", text: "#ffffff", border: "#991b1b" },
    high: { bg: "#ea580c", text: "#ffffff", border: "#c2410c" },
    medium: { bg: "#f59e0b", text: "#ffffff", border: "#d97706" },
    low: { bg: "#10b981", text: "#ffffff", border: "#059669" },
  };

  const colors = riskColors[data.riskLevel];

  const content = `
    <div style="background-color: ${colors.bg}; color: ${colors.text}; padding: 20px; border-radius: 8px; margin-bottom: 20px; text-align: center;">
      <h2 style="margin: 0; font-size: 24px;">⚠️ Risk Uyarısı</h2>
      <p style="margin: 10px 0 0 0; font-size: 18px; font-weight: 600;">
        Risk Seviyesi: ${data.riskLevel.toUpperCase()}
      </p>
    </div>
    
    <p><strong>Danışan:</strong> ${data.clientName}</p>
    ${data.sessionDate ? `<p><strong>Seans Tarihi:</strong> ${new Date(data.sessionDate).toLocaleDateString("tr-TR")}</p>` : ""}
    
    <div style="margin: 20px 0; padding: 15px; background-color: #fef2f2; border-left: 4px solid #dc2626; border-radius: 4px;">
      <h3 style="color: #dc2626; margin-top: 0;">Tespit Edilen Risk Kelimeleri:</h3>
      <ul style="margin: 10px 0; padding-left: 20px;">
        ${data.detectedKeywords.map(keyword => `<li><strong>${keyword}</strong></li>`).join("")}
      </ul>
    </div>
    
    ${data.contextSnippet ? `
      <div style="margin: 20px 0;">
        <h3>Bağlam:</h3>
        <p style="background-color: #f3f4f6; padding: 15px; border-radius: 4px; font-style: italic; white-space: pre-wrap;">
          "${data.contextSnippet}"
        </p>
      </div>
    ` : ""}
    
    ${data.recommendedActions && data.recommendedActions.length > 0 ? `
      <div style="margin: 20px 0; padding: 15px; background-color: #eff6ff; border-left: 4px solid #3b82f6; border-radius: 4px;">
        <h3 style="color: #3b82f6; margin-top: 0;">Önerilen Aksiyonlar:</h3>
        <ul style="margin: 10px 0; padding-left: 20px;">
          ${data.recommendedActions.map(action => `<li>${action}</li>`).join("")}
        </ul>
      </div>
    ` : ""}
    
    ${data.emergencyContact ? `
      <div style="margin: 20px 0; padding: 15px; background-color: #fef2f2; border: 2px solid #dc2626; border-radius: 4px;">
        <h3 style="color: #dc2626; margin-top: 0;">🚨 Acil Durum İletişim:</h3>
        <p style="margin: 0; font-size: 18px; font-weight: 600;">${data.emergencyContact}</p>
      </div>
    ` : ""}
    
    <div style="margin: 30px 0; padding: 15px; background-color: #fffbeb; border-left: 4px solid #f59e0b; border-radius: 4px;">
      <p style="margin: 0;"><strong>⚠️ Önemli:</strong> Bu bir otomatik uyarıdır. Lütfen durumu değerlendirin ve gerekli önlemleri alın.</p>
    </div>
  `;

  return BaseEmailTemplate({
    title: `Risk Uyarısı - ${data.clientName}`,
    content,
  });
}

export function renderRiskTextTemplate(data: RiskEmailData): string {
  return `
⚠️ RİSK UYARISI

Risk Seviyesi: ${data.riskLevel.toUpperCase()}
Danışan: ${data.clientName}
${data.sessionDate ? `Seans Tarihi: ${new Date(data.sessionDate).toLocaleDateString("tr-TR")}\n` : ""}

Tespit Edilen Risk Kelimeleri:
${data.detectedKeywords.map(k => `- ${k}`).join("\n")}

${data.contextSnippet ? `\nBağlam:\n"${data.contextSnippet}"\n` : ""}

${data.recommendedActions && data.recommendedActions.length > 0 ? `
Önerilen Aksiyonlar:
${data.recommendedActions.map(a => `- ${a}`).join("\n")}
` : ""}

${data.emergencyContact ? `\n🚨 Acil Durum İletişim: ${data.emergencyContact}` : ""}

---
⚠️ ÖNEMLİ: Bu bir otomatik uyarıdır. Lütfen durumu değerlendirin ve gerekli önlemleri alın.

MindTrack - https://mindtrack.app
  `.trim();
}






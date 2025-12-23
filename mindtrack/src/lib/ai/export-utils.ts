import { Document, Packer, Paragraph, TextRun, HeadingLevel } from "docx";
import { saveAs } from "file-saver";

export interface SOAPNote {
  subjective: string;
  objective: string;
  assessment: string;
  plan: string;
}

/**
 * SOAP notunu Word (DOCX) formatında export et
 */
export async function exportSOAPToWord(
  soap: SOAPNote,
  clientName?: string,
  date?: Date
): Promise<void> {
  try {
    const doc = new Document({
      sections: [
        {
          properties: {},
          children: [
            // Header
            new Paragraph({
              text: "SOAP Notu",
              heading: HeadingLevel.HEADING_1,
              spacing: { after: 400 },
            }),
            
            // Client info
            ...(clientName
              ? [
                  new Paragraph({
                    text: `Hasta: ${clientName}`,
                    spacing: { after: 200 },
                  }),
                ]
              : []),
            
            // Date
            new Paragraph({
              text: `Tarih: ${(date || new Date()).toLocaleDateString("tr-TR")}`,
              spacing: { after: 400 },
            }),

            // Subjective
            new Paragraph({
              text: "S - Subjective (Öznel)",
              heading: HeadingLevel.HEADING_2,
              spacing: { before: 400, after: 200 },
            }),
            new Paragraph({
              text: soap.subjective || "(Boş)",
              spacing: { after: 400 },
            }),

            // Objective
            new Paragraph({
              text: "O - Objective (Nesnel)",
              heading: HeadingLevel.HEADING_2,
              spacing: { before: 400, after: 200 },
            }),
            new Paragraph({
              text: soap.objective || "(Boş)",
              spacing: { after: 400 },
            }),

            // Assessment
            new Paragraph({
              text: "A - Assessment (Değerlendirme)",
              heading: HeadingLevel.HEADING_2,
              spacing: { before: 400, after: 200 },
            }),
            new Paragraph({
              text: soap.assessment || "(Boş)",
              spacing: { after: 400 },
            }),

            // Plan
            new Paragraph({
              text: "P - Plan (Plan)",
              heading: HeadingLevel.HEADING_2,
              spacing: { before: 400, after: 200 },
            }),
            new Paragraph({
              text: soap.plan || "(Boş)",
              spacing: { after: 400 },
            }),
          ],
        },
      ],
    });

    const blob = await Packer.toBlob(doc);
    const fileName = `SOAP-${clientName || "Hasta"}-${new Date().toISOString().split("T")[0]}.docx`;
    saveAs(blob, fileName);
  } catch (error) {
    console.error("Word export hatası:", error);
    throw new Error("Word dosyası oluşturulamadı");
  }
}

/**
 * Paylaşım linki oluştur (güvenli token ile)
 */
export function generateShareLink(
  soapId: string,
  expiresIn: number = 7 * 24 * 60 * 60 * 1000 // 7 gün
): string {
  // Basit token oluştur (production'da daha güvenli olmalı)
  const token = Buffer.from(`${soapId}-${Date.now() + expiresIn}`).toString("base64");
  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";
  return `${baseUrl}/share/soap/${token}`;
}

/**
 * QR kod için data URL oluştur
 */
export async function generateQRCode(data: string): Promise<string> {
  try {
    // Basit QR kod oluşturma (gerçek implementasyon için qrcode library kullanılmalı)
    const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(data)}`;
    return qrCodeUrl;
  } catch (error) {
    console.error("QR kod oluşturma hatası:", error);
    return "";
  }
}






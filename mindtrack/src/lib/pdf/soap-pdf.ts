/**
 * SOAP Note PDF Generation
 * Uses jsPDF for PDF creation
 */

import { jsPDF } from "jspdf";

export interface SOAPPDFData {
  clientName: string;
  date: string;
  soap: {
    subjective: string;
    objective: string;
    assessment: string;
    plan: string;
  };
  therapistName?: string;
  riskLevel?: "low" | "medium" | "high" | "critical";
  metadata?: Record<string, unknown>;
}

/**
 * Generate PDF from SOAP note data
 */
export async function generateSOAPPDF(data: SOAPPDFData): Promise<Buffer> {
  const doc = new jsPDF({
    orientation: "portrait",
    unit: "mm",
    format: "a4",
  });

  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const margin = 20;
  const maxWidth = pageWidth - 2 * margin;
  let yPos = margin;

  // Helper function to add text with word wrap
  const addWrappedText = (text: string, x: number, y: number, maxWidth: number, fontSize: number = 10) => {
    doc.setFontSize(fontSize);
    const lines = doc.splitTextToSize(text, maxWidth);
    doc.text(lines, x, y);
    return lines.length * (fontSize * 0.5); // Return height used
  };

  // Helper function to check if we need a new page
  const checkNewPage = (requiredHeight: number) => {
    if (yPos + requiredHeight > pageHeight - margin) {
      doc.addPage();
      yPos = margin;
      return true;
    }
    return false;
  };

  // Header
  doc.setFontSize(20);
  doc.setTextColor(79, 70, 229); // Indigo color
  doc.text("SOAP Notu", margin, yPos);
  yPos += 10;

  doc.setFontSize(12);
  doc.setTextColor(0, 0, 0);
  doc.text(`Danışan: ${data.clientName}`, margin, yPos);
  yPos += 7;

  doc.text(`Tarih: ${new Date(data.date).toLocaleDateString("tr-TR")}`, margin, yPos);
  yPos += 7;

  if (data.therapistName) {
    doc.text(`Terapist: ${data.therapistName}`, margin, yPos);
    yPos += 7;
  }

  // Risk Level Badge
  if (data.riskLevel) {
    const riskColors = {
      critical: [220, 38, 38],
      high: [234, 88, 12],
      medium: [245, 158, 11],
      low: [16, 185, 129],
    };

    const colors = riskColors[data.riskLevel];
    doc.setFillColor(colors[0], colors[1], colors[2]);
    doc.roundedRect(margin, yPos - 5, 60, 8, 2, 2, "F");
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(10);
    doc.text(`Risk Seviyesi: ${data.riskLevel.toUpperCase()}`, margin + 3, yPos);
    doc.setTextColor(0, 0, 0);
    yPos += 12;
  }

  yPos += 5;

  // Subjective Section
  doc.setFontSize(14);
  doc.setTextColor(79, 70, 229);
  doc.text("📝 Subjective (Öznel)", margin, yPos);
  yPos += 8;

  doc.setFontSize(10);
  doc.setTextColor(0, 0, 0);
  const subjectiveHeight = addWrappedText(
    data.soap.subjective || "(Boş)",
    margin,
    yPos,
    maxWidth
  );
  yPos += subjectiveHeight + 10;

  checkNewPage(20);

  // Objective Section
  doc.setFontSize(14);
  doc.setTextColor(16, 185, 129);
  doc.text("👁️ Objective (Nesnel)", margin, yPos);
  yPos += 8;

  doc.setFontSize(10);
  doc.setTextColor(0, 0, 0);
  const objectiveHeight = addWrappedText(
    data.soap.objective || "(Boş)",
    margin,
    yPos,
    maxWidth
  );
  yPos += objectiveHeight + 10;

  checkNewPage(20);

  // Assessment Section
  doc.setFontSize(14);
  doc.setTextColor(245, 158, 11);
  doc.text("🔍 Assessment (Değerlendirme)", margin, yPos);
  yPos += 8;

  doc.setFontSize(10);
  doc.setTextColor(0, 0, 0);
  const assessmentHeight = addWrappedText(
    data.soap.assessment || "(Boş)",
    margin,
    yPos,
    maxWidth
  );
  yPos += assessmentHeight + 10;

  checkNewPage(20);

  // Plan Section
  doc.setFontSize(14);
  doc.setTextColor(139, 92, 246);
  doc.text("📋 Plan (Plan)", margin, yPos);
  yPos += 8;

  doc.setFontSize(10);
  doc.setTextColor(0, 0, 0);
  const planHeight = addWrappedText(
    data.soap.plan || "(Boş)",
    margin,
    yPos,
    maxWidth
  );
  yPos += planHeight + 10;

  // Footer on last page
  const totalPages = doc.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    doc.setFontSize(8);
    doc.setTextColor(107, 114, 128);
    doc.text(
      `Sayfa ${i} / ${totalPages}`,
      pageWidth / 2,
      pageHeight - 10,
      { align: "center" }
    );
    doc.text(
      `MindTrack - ${new Date().toLocaleDateString("tr-TR")}`,
      pageWidth / 2,
      pageHeight - 5,
      { align: "center" }
    );
  }

  // Convert to Buffer
  const pdfBlob = doc.output("arraybuffer");
  return Buffer.from(pdfBlob);
}

/**
 * Generate PDF and return as base64 string (for email attachments)
 */
export async function generateSOAPPDFBase64(data: SOAPPDFData): Promise<string> {
  const buffer = await generateSOAPPDF(data);
  return buffer.toString("base64");
}






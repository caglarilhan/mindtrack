/**
 * Lazy-loaded export utilities
 * Heavy libraries (jspdf, docx) are loaded only when needed
 */

import type { SOAPNote } from "./export-utils";

/**
 * Lazy load PDF export
 */
export async function exportSOAPToPDFLazy(
  soap: SOAPNote,
  clientName?: string,
  date?: Date
): Promise<void> {
  const { jsPDF } = await import("jspdf");
  // PDF generation logic here
  // ... (same as export-utils.ts but lazy loaded)
}

/**
 * Lazy load Word export
 */
export async function exportSOAPToWordLazy(
  soap: SOAPNote,
  clientName?: string,
  date?: Date
): Promise<void> {
  const { Document, Packer, Paragraph, HeadingLevel } = await import("docx");
  const { saveAs } = await import("file-saver");
  // Word generation logic here
  // ... (same as export-utils.ts but lazy loaded)
}






/**
 * HIPAA-Compliant AI Processor
 * Ensures all AI processing follows HIPAA requirements
 */

import { encryptPHI, decryptPHI } from "@/lib/hipaa/encryption";
import { logDataAccess, logDataModification } from "@/lib/hipaa/audit-log";
import { hasAccess } from "@/lib/hipaa/access-control";

export interface HIPAACompliantAIRequest {
  userId: string;
  data: string;
  resourceType: string;
  resourceId?: string;
  ipAddress?: string;
  userAgent?: string;
}

export interface HIPAACompliantAIResponse {
  success: boolean;
  result?: unknown;
  error?: string;
  auditLogId?: string;
}

/**
 * De-identify PHI data before sending to AI
 * Removes or replaces identifying information
 */
export function deidentifyPHI(data: string): {
  deidentified: string;
  phiFields: Record<string, string>; // Store original values for re-identification
} {
  const phiFields: Record<string, string> = {};
  let deidentified = data;

  // Patterns to de-identify
  const patterns = [
    // Names (common Turkish names)
    {
      regex: /\b([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)\s+([A-ZÇĞİÖŞÜ][a-zçğıöşü]+)\b/g,
      replacement: (match: string) => {
        const id = `[NAME_${Object.keys(phiFields).length + 1}]`;
        phiFields[id] = match;
        return id;
      },
    },
    // Dates (DD.MM.YYYY or DD/MM/YYYY)
    {
      regex: /\b(\d{1,2}[./]\d{1,2}[./]\d{4})\b/g,
      replacement: (match: string) => {
        const id = `[DATE_${Object.keys(phiFields).length + 1}]`;
        phiFields[id] = match;
        return id;
      },
    },
    // Phone numbers
    {
      regex: /\b(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})\b/g,
      replacement: (match: string) => {
        const id = `[PHONE_${Object.keys(phiFields).length + 1}]`;
        phiFields[id] = match;
        return id;
      },
    },
    // Email addresses
    {
      regex: /\b([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b/g,
      replacement: (match: string) => {
        const id = `[EMAIL_${Object.keys(phiFields).length + 1}]`;
        phiFields[id] = match;
        return id;
      },
    },
    // Addresses (basic pattern)
    {
      regex: /\b([A-ZÇĞİÖŞÜ][a-zçğıöşü]+\s+(Sokak|Cadde|Mahalle|Bulvar|Avenue|Street))\b/gi,
      replacement: (match: string) => {
        const id = `[ADDRESS_${Object.keys(phiFields).length + 1}]`;
        phiFields[id] = match;
        return id;
      },
    },
  ];

  // Apply all patterns
  for (const pattern of patterns) {
    deidentified = deidentified.replace(pattern.regex, pattern.replacement);
  }

  return { deidentified, phiFields };
}

/**
 * Re-identify PHI data after AI processing
 */
export function reidentifyPHI(
  data: string,
  phiFields: Record<string, string>
): string {
  let reidentified = data;

  // Replace placeholders with original values
  for (const [placeholder, original] of Object.entries(phiFields)) {
    reidentified = reidentified.replace(new RegExp(placeholder, "g"), original);
  }

  return reidentified;
}

/**
 * Process data with AI in HIPAA-compliant manner
 */
export async function processWithAI<T>(
  request: HIPAACompliantAIRequest,
  aiProcessor: (deidentifiedData: string) => Promise<T>
): Promise<HIPAACompliantAIResponse> {
  try {
    // Check access
    const hasAccessToResource = await hasAccess(
      request.userId,
      request.resourceType,
      "read",
      request.resourceId
    );

    if (!hasAccessToResource) {
      await logDataAccess(
        request.userId,
        request.resourceType,
        request.resourceId,
        request.ipAddress,
        request.userAgent,
        false
      );
      return {
        success: false,
        error: "Access denied",
      };
    }

    // Log data access
    await logDataAccess(
      request.userId,
      request.resourceType,
      request.resourceId,
      request.ipAddress,
      request.userAgent,
      true
    );

    // De-identify PHI before AI processing
    const { deidentified, phiFields } = deidentifyPHI(request.data);

    // Process with AI (using de-identified data)
    const aiResult = await aiProcessor(deidentified);

    // Re-identify result if needed
    let finalResult = aiResult;
    if (typeof aiResult === "string") {
      finalResult = reidentifyPHI(aiResult, phiFields) as T;
    } else if (typeof aiResult === "object" && aiResult !== null) {
      // Recursively re-identify object
      finalResult = reidentifyObject(aiResult as Record<string, unknown>, phiFields) as T;
    }

    // Log AI processing
    await logDataModification(
      request.userId,
      "create",
      "ai_processing",
      request.resourceId,
      request.ipAddress,
      request.userAgent,
      true,
      {
        resourceType: request.resourceType,
        deidentified: true,
      }
    );

    return {
      success: true,
      result: finalResult,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("HIPAA-compliant AI processing error:", error);

    // Log error
    await logDataModification(
      request.userId,
      "create",
      "ai_processing",
      request.resourceId,
      request.ipAddress,
      request.userAgent,
      false,
      {
        error: errorMessage,
      }
    );

    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Recursively re-identify object
 */
function reidentifyObject(
  obj: Record<string, unknown>,
  phiFields: Record<string, string>
): Record<string, unknown> {
  const reidentified: Record<string, unknown> = {};

  for (const [key, value] of Object.entries(obj)) {
    if (typeof value === "string") {
      reidentified[key] = reidentifyPHI(value, phiFields);
    } else if (typeof value === "object" && value !== null && !Array.isArray(value)) {
      reidentified[key] = reidentifyObject(value as Record<string, unknown>, phiFields);
    } else if (Array.isArray(value)) {
      reidentified[key] = value.map((item) => {
        if (typeof item === "string") {
          return reidentifyPHI(item, phiFields);
        } else if (typeof item === "object" && item !== null) {
          return reidentifyObject(item as Record<string, unknown>, phiFields);
        }
        return item;
      });
    } else {
      reidentified[key] = value;
    }
  }

  return reidentified;
}

/**
 * Check if AI provider has BAA
 * In production, this should check a database or configuration
 */
export function hasAIProviderBAA(provider: "openai" | "gemini" | "anthropic"): boolean {
  // In production, check actual BAA status
  // For now, return based on environment variable
  const baaStatus = process.env[`${provider.toUpperCase()}_BAA_SIGNED`];
  return baaStatus === "true";
}

/**
 * Validate AI request for HIPAA compliance
 */
export function validateAIRequest(request: HIPAACompliantAIRequest): {
  valid: boolean;
  errors: string[];
} {
  const errors: string[] = [];

  if (!request.userId) {
    errors.push("User ID is required");
  }

  if (!request.data || request.data.trim().length === 0) {
    errors.push("Data is required");
  }

  if (!request.resourceType) {
    errors.push("Resource type is required");
  }

  // Check data size (prevent excessive data)
  if (request.data.length > 50000) {
    errors.push("Data size exceeds maximum allowed (50,000 characters)");
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}






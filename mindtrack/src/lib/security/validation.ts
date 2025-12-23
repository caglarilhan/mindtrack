/**
 * Security Validation Utilities
 * Input validation, XSS protection, SQL injection prevention
 */

/**
 * Sanitize string input
 */
export function sanitizeInput(input: string): string {
  if (typeof input !== "string") {
    return "";
  }

  // Remove null bytes
  let sanitized = input.replace(/\0/g, "");

  // Remove script tags
  sanitized = sanitized.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, "");

  // Remove event handlers
  sanitized = sanitized.replace(/on\w+\s*=\s*["'][^"']*["']/gi, "");

  // Remove javascript: protocol
  sanitized = sanitized.replace(/javascript:/gi, "");

  // Remove data: URLs (except images)
  sanitized = sanitized.replace(/data:(?!image\/)/gi, "");

  return sanitized.trim();
}

/**
 * Validate email format
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate UUID format
 */
export function isValidUUID(uuid: string): boolean {
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
  return uuidRegex.test(uuid);
}

/**
 * Validate URL format
 */
export function isValidURL(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * Check for SQL injection patterns
 */
export function containsSQLInjection(input: string): boolean {
  const sqlPatterns = [
    /(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)/i,
    /(--|#|\/\*|\*\/)/,
    /(\b(OR|AND)\s+\d+\s*=\s*\d+)/i,
    /(\b(UNION|JOIN)\b)/i,
    /('|"|;|--|\/\*|\*\/)/,
  ];

  return sqlPatterns.some(pattern => pattern.test(input));
}

/**
 * Check for XSS patterns
 */
export function containsXSS(input: string): boolean {
  const xssPatterns = [
    /<script/i,
    /javascript:/i,
    /on\w+\s*=/i,
    /<iframe/i,
    /<object/i,
    /<embed/i,
    /<link/i,
    /<meta/i,
    /<style/i,
  ];

  return xssPatterns.some(pattern => pattern.test(input));
}

/**
 * Validate and sanitize request body
 */
export function validateRequestBody<T extends Record<string, unknown>>(
  body: unknown,
  schema: Record<keyof T, (value: unknown) => boolean>
): { valid: boolean; sanitized?: T; errors?: string[] } {
  if (typeof body !== "object" || body === null) {
    return { valid: false, errors: ["Invalid request body"] };
  }

  const sanitized = {} as T;
  const errors: string[] = [];

  for (const [key, validator] of Object.entries(schema)) {
    const value = (body as Record<string, unknown>)[key];

    if (typeof value === "string") {
      // Check for SQL injection and XSS
      if (containsSQLInjection(value)) {
        errors.push(`Field '${key}' contains potential SQL injection`);
        continue;
      }

      if (containsXSS(value)) {
        errors.push(`Field '${key}' contains potential XSS`);
        continue;
      }

      // Sanitize string values
      const sanitizedValue = sanitizeInput(value);
      if (!validator(sanitizedValue)) {
        errors.push(`Field '${key}' failed validation`);
        continue;
      }

      sanitized[key as keyof T] = sanitizedValue as T[keyof T];
    } else {
      if (!validator(value)) {
        errors.push(`Field '${key}' failed validation`);
        continue;
      }

      sanitized[key as keyof T] = value as T[keyof T];
    }
  }

  return {
    valid: errors.length === 0,
    sanitized: errors.length === 0 ? sanitized : undefined,
    errors: errors.length > 0 ? errors : undefined,
  };
}

/**
 * Validate API key format
 */
export function isValidAPIKey(key: string): boolean {
  // Basic validation - adjust based on your API key format
  return typeof key === "string" && key.length >= 20 && key.length <= 200;
}

/**
 * Validate file upload
 */
export function validateFileUpload(file: File, options?: {
  maxSize?: number; // in bytes
  allowedTypes?: string[];
}): { valid: boolean; error?: string } {
  const maxSize = options?.maxSize || 10 * 1024 * 1024; // 10MB default
  const allowedTypes = options?.allowedTypes || ["image/jpeg", "image/png", "image/webp", "application/pdf"];

  if (file.size > maxSize) {
    return {
      valid: false,
      error: `File size exceeds maximum allowed size of ${maxSize / 1024 / 1024}MB`,
    };
  }

  if (!allowedTypes.includes(file.type)) {
    return {
      valid: false,
      error: `File type ${file.type} is not allowed. Allowed types: ${allowedTypes.join(", ")}`,
    };
  }

  return { valid: true };
}






import { NextRequest } from "next/server";

// Rate limiting için basit in-memory store (production'da Redis kullanılmalı)
const rateLimitStore = new Map<string, { count: number; resetTime: number }>();

/**
 * Rate limiting middleware
 */
export function rateLimit(
  identifier: string,
  limit: number = 10,
  windowMs: number = 60000 // 1 dakika
): { allowed: boolean; remaining: number; resetTime: number } {
  const now = Date.now();
  const key = identifier;
  
  const record = rateLimitStore.get(key);
  
  if (!record || now > record.resetTime) {
    // Yeni window başlat
    rateLimitStore.set(key, {
      count: 1,
      resetTime: now + windowMs,
    });
    
    // Eski kayıtları temizle (memory leak önleme)
    if (rateLimitStore.size > 1000) {
      for (const [k, v] of rateLimitStore.entries()) {
        if (now > v.resetTime) {
          rateLimitStore.delete(k);
        }
      }
    }
    
    return {
      allowed: true,
      remaining: limit - 1,
      resetTime: now + windowMs,
    };
  }
  
  if (record.count >= limit) {
    return {
      allowed: false,
      remaining: 0,
      resetTime: record.resetTime,
    };
  }
  
  // Count artır
  record.count++;
  rateLimitStore.set(key, record);
  
  return {
    allowed: true,
    remaining: limit - record.count,
    resetTime: record.resetTime,
  };
}

/**
 * Request'ten identifier çıkar (IP veya user ID)
 */
export function getRateLimitIdentifier(request: NextRequest, userId?: string): string {
  if (userId) {
    return `user:${userId}`;
  }
  
  // IP adresi
  const forwarded = request.headers.get('x-forwarded-for');
  const ip = forwarded ? forwarded.split(',')[0] : request.headers.get('x-real-ip') || 'unknown';
  
  return `ip:${ip}`;
}

/**
 * Input validation ve sanitization
 */
export function validateTranscript(transcript: string): { valid: boolean; sanitized: string; error?: string } {
  // Boş kontrolü
  if (!transcript || typeof transcript !== 'string') {
    return {
      valid: false,
      sanitized: '',
      error: 'Transkript gerekli ve string olmalı',
    };
  }
  
  // Uzunluk kontrolü
  if (transcript.length > 50000) {
    return {
      valid: false,
      sanitized: transcript.substring(0, 50000),
      error: 'Transkript çok uzun (max 50000 karakter)',
    };
  }
  
  if (transcript.length < 10) {
    return {
      valid: false,
      sanitized: transcript,
      error: 'Transkript çok kısa (min 10 karakter)',
    };
  }
  
  // XSS koruması
  let sanitized = transcript
    // Script tag'lerini kaldır
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    // JavaScript: protokolünü kaldır
    .replace(/javascript:/gi, '')
    // Event handler'ları kaldır
    .replace(/on\w+\s*=/gi, '')
    // HTML entity'leri decode et
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&quot;/g, '"')
    .replace(/&#x27;/g, "'");
  
  // SQL injection koruması (basit)
  const sqlKeywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'SELECT', 'UNION', '--', ';'];
  for (const keyword of sqlKeywords) {
    if (sanitized.toUpperCase().includes(keyword)) {
      // Sadece uyarı ver, engelleme (çünkü normal metinde de geçebilir)
      console.warn(`⚠️ Potansiyel SQL injection: ${keyword}`);
    }
  }
  
  return {
    valid: true,
    sanitized: sanitized.trim(),
  };
}

/**
 * Audit logging
 */
export async function logAuditEvent(
  event: string,
  userId: string,
  details: Record<string, any>
): Promise<void> {
  try {
    // Audit log kaydet (veritabanına)
    console.log('📝 Audit Log:', {
      event,
      userId,
      details,
      timestamp: new Date().toISOString(),
    });
    
    // TODO: Gerçek audit log tablosuna kaydet
    // await supabase.from('audit_logs').insert({ ... });
  } catch (error) {
    console.error('Audit log hatası:', error);
  }
}

/**
 * API key validation (gelecek için)
 */
export function validateAPIKey(apiKey: string | null): boolean {
  if (!apiKey) {
    return false;
  }
  
  // Basit format kontrolü
  if (apiKey.startsWith('AIza')) {
    // Google Gemini API key formatı
    return apiKey.length > 30;
  }
  
  if (apiKey.startsWith('sk-')) {
    // OpenAI API key formatı
    return apiKey.length > 40;
  }
  
  return false;
}






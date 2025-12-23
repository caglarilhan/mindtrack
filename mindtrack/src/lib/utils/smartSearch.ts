/**
 * Smart Search Utility
 * Automatically detects search type and applies appropriate filters
 */

export interface SmartSearchResult {
  type: 'id' | 'phone' | 'email' | 'diagnosis' | 'risk' | 'text';
  value: string;
  filters?: {
    search?: string;
    riskLevel?: string;
    diagnosis?: string;
  };
}

export function parseSmartSearch(query: string): SmartSearchResult {
  const trimmed = query.trim();
  
  // ID detection (P-XXXX, UUID format, or numeric)
  if (/^P-[A-Z0-9]+$/i.test(trimmed) || /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(trimmed)) {
    return { type: 'id', value: trimmed };
  }
  
  // Phone detection (starts with numbers, contains + or digits)
  if (/^\+?[0-9\s\-()]+$/.test(trimmed) && trimmed.replace(/\D/g, '').length >= 7) {
    return { type: 'phone', value: trimmed };
  }
  
  // Email detection
  if (trimmed.includes('@') && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmed)) {
    return { type: 'email', value: trimmed };
  }
  
  // Risk level detection
  const riskKeywords = ['yüksek risk', 'high risk', 'orta risk', 'medium risk', 'düşük risk', 'low risk'];
  const lowerQuery = trimmed.toLowerCase();
  for (const keyword of riskKeywords) {
    if (lowerQuery.includes(keyword)) {
      let riskLevel = 'low';
      if (lowerQuery.includes('yüksek') || lowerQuery.includes('high')) riskLevel = 'high';
      else if (lowerQuery.includes('orta') || lowerQuery.includes('medium')) riskLevel = 'medium';
      return {
        type: 'risk',
        value: trimmed,
        filters: { riskLevel }
      };
    }
  }
  
  // Diagnosis code detection (F32.1, F41.9, etc.)
  if (/^F\d{2}\.?\d*$/i.test(trimmed) || /^[A-Z]\d{2}\.?\d*$/i.test(trimmed)) {
    return { type: 'diagnosis', value: trimmed, filters: { diagnosis: trimmed } };
  }
  
  // Default text search
  return { type: 'text', value: trimmed };
}











/**
 * React Query utilities
 * Provider component: src/components/providers/react-query-provider.tsx
 */

// Cache keys - merkezi yönetim için
export const queryKeys = {
  // SOAP Notes
  soapNotes: (clientId?: string) => ["soap-notes", clientId] as const,
  soapNote: (noteId: string) => ["soap-note", noteId] as const,
  soapVersions: (noteId: string) => ["soap-versions", noteId] as const,
  
  // Clients
  clients: () => ["clients"] as const,
  client: (clientId: string) => ["client", clientId] as const,
  
  // Sessions
  sessions: (clientId?: string) => ["sessions", clientId] as const,
  session: (sessionId: string) => ["session", sessionId] as const,
  
  // Analytics
  analytics: (clientId?: string, days?: number) => ["analytics", clientId, days] as const,
  
  // Risk
  riskStats: (clientId?: string) => ["risk-stats", clientId] as const,
  
  // Templates
  templates: () => ["templates"] as const,
} as const;


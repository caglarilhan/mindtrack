/**
 * Analytics utilities for SOAP notes and AI features
 */

export interface SOAPAnalytics {
  totalNotes: number;
  notesByMonth: { month: string; count: number }[];
  averageLength: {
    subjective: number;
    objective: number;
    assessment: number;
    plan: number;
  };
  riskDistribution: {
    low: number;
    medium: number;
    high: number;
    critical: number;
  };
  modeUsage: {
    standard: number;
    premium: number;
    consultation: number;
  };
  generationTime: {
    average: number;
    p50: number;
    p95: number;
  };
}

export interface TrendData {
  date: string;
  count: number;
  riskScore: number;
  avgGenerationTime: number;
}

/**
 * Calculate SOAP analytics from notes
 */
interface NoteForAnalytics {
  created_at: string;
  content_encrypted?: string;
  metadata?: Record<string, unknown>;
}

export async function calculateSOAPAnalytics(
  notes: Array<NoteForAnalytics>
): Promise<SOAPAnalytics> {
  const totalNotes = notes.length;
  
  // Notes by month
  const notesByMonth = notes.reduce((acc, note) => {
    const month = new Date(note.created_at).toLocaleDateString('tr-TR', { year: 'numeric', month: 'short' });
    const existing = acc.find((m) => m.month === month);
    if (existing) {
      existing.count++;
    } else {
      acc.push({ month, count: 1 });
    }
    return acc;
  }, [] as { month: string; count: number }[]);

  // Average length (mock - decrypt would be needed)
  const averageLength = {
    subjective: 150,
    objective: 120,
    assessment: 200,
    plan: 180,
  };

  // Risk distribution (from metadata if available)
  const riskDistribution = {
    low: notes.filter((n) => (n.metadata?.riskLevel as string) === 'low').length,
    medium: notes.filter((n) => (n.metadata?.riskLevel as string) === 'medium').length,
    high: notes.filter((n) => (n.metadata?.riskLevel as string) === 'high').length,
    critical: notes.filter((n) => (n.metadata?.riskLevel as string) === 'critical').length,
  };

  // Mode usage
  const modeUsage = {
    standard: notes.filter((n) => (n.metadata?.mode as string) === 'standard').length,
    premium: notes.filter((n) => (n.metadata?.mode as string) === 'premium').length,
    consultation: notes.filter((n) => (n.metadata?.mode as string) === 'consultation').length,
  };

  // Generation time (from metadata)
  const generationTimes = notes
    .map((n) => (n.metadata?.generationTime as number) || 0)
    .filter((t) => t > 0);
  
  const generationTime = {
    average: generationTimes.length > 0 
      ? generationTimes.reduce((a, b) => a + b, 0) / generationTimes.length 
      : 0,
    p50: generationTimes.length > 0 
      ? generationTimes.sort((a, b) => a - b)[Math.floor(generationTimes.length * 0.5)] 
      : 0,
    p95: generationTimes.length > 0 
      ? generationTimes.sort((a, b) => a - b)[Math.floor(generationTimes.length * 0.95)] 
      : 0,
  };

  return {
    totalNotes,
    notesByMonth: notesByMonth.sort((a, b) => a.month.localeCompare(b.month)),
    averageLength,
    riskDistribution,
    modeUsage,
    generationTime,
  };
}

/**
 * Calculate trend data for charts
 */
interface NoteForTrend {
  created_at: string;
  metadata?: Record<string, unknown>;
}

export function calculateTrendData(
  notes: Array<NoteForTrend>,
  days: number = 30
): TrendData[] {
  const now = new Date();
  const startDate = new Date(now.getTime() - days * 24 * 60 * 60 * 1000);
  
  const dailyData: Record<string, { count: number; riskScores: number[]; times: number[] }> = {};
  
  notes.forEach((note) => {
    const date = new Date(note.created_at);
    if (date < startDate) return;
    
    const dateKey = date.toISOString().split('T')[0];
    if (!dailyData[dateKey]) {
      dailyData[dateKey] = { count: 0, riskScores: [], times: [] };
    }
    
    dailyData[dateKey].count++;
    
    const riskLevel = note.metadata?.riskLevel as string;
    const riskScore = riskLevel === 'critical' ? 100 : 
                     riskLevel === 'high' ? 75 : 
                     riskLevel === 'medium' ? 50 : 
                     riskLevel === 'low' ? 25 : 0;
    dailyData[dateKey].riskScores.push(riskScore);
    
    const genTime = (note.metadata?.generationTime as number) || 0;
    if (genTime > 0) {
      dailyData[dateKey].times.push(genTime);
    }
  });

  return Object.entries(dailyData)
    .map(([date, data]) => ({
      date,
      count: data.count,
      riskScore: data.riskScores.length > 0
        ? data.riskScores.reduce((a, b) => a + b, 0) / data.riskScores.length
        : 0,
      avgGenerationTime: data.times.length > 0
        ? data.times.reduce((a, b) => a + b, 0) / data.times.length
        : 0,
    }))
    .sort((a, b) => a.date.localeCompare(b.date));
}

/**
 * Get usage statistics
 */
export interface UsageStats {
  totalSessions: number;
  totalSOAPNotes: number;
  avgNotesPerSession: number;
  mostUsedMode: 'standard' | 'premium' | 'consultation';
  riskDetectionRate: number;
  averageRiskScore: number;
}

interface SessionForStats {
  id: string;
  created_at: string;
}

interface NoteForStats {
  session_id?: string;
  metadata?: Record<string, unknown>;
}

export function calculateUsageStats(
  sessions: Array<SessionForStats>,
  notes: Array<NoteForStats>
): UsageStats {
  const totalSessions = sessions.length;
  const totalSOAPNotes = notes.length;
  const avgNotesPerSession = totalSessions > 0 ? totalSOAPNotes / totalSessions : 0;

  const modeCounts = {
    standard: notes.filter((n) => (n.metadata?.mode as string) === 'standard').length,
    premium: notes.filter((n) => (n.metadata?.mode as string) === 'premium').length,
    consultation: notes.filter((n) => (n.metadata?.mode as string) === 'consultation').length,
  };

  const mostUsedMode = 
    modeCounts.consultation > modeCounts.premium && modeCounts.consultation > modeCounts.standard ? 'consultation' :
    modeCounts.premium > modeCounts.standard ? 'premium' : 'standard';

  const riskDetected = notes.filter((n) => {
    const risk = n.metadata?.riskLevel as string;
    return risk && risk !== 'low';
  }).length;

  const riskDetectionRate = totalSOAPNotes > 0 ? (riskDetected / totalSOAPNotes) * 100 : 0;

  const riskScores = notes
    .map((n) => {
      const risk = n.metadata?.riskLevel as string;
      return risk === 'critical' ? 100 : 
             risk === 'high' ? 75 : 
             risk === 'medium' ? 50 : 
             risk === 'low' ? 25 : 0;
    })
    .filter((s) => s > 0);

  const averageRiskScore = riskScores.length > 0
    ? riskScores.reduce((a, b) => a + b, 0) / riskScores.length
    : 0;

  return {
    totalSessions,
    totalSOAPNotes,
    avgNotesPerSession,
    mostUsedMode,
    riskDetectionRate,
    averageRiskScore,
  };
}


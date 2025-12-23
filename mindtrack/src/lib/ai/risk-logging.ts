import { createClient } from "@/utils/supabase/server";

export interface RiskLog {
  id?: string;
  client_id: string;
  session_id?: string;
  risk_level: 'high' | 'medium' | 'low';
  keywords: string[];
  transcript_snippet: string;
  risk_score?: number;
  created_at?: string;
  created_by?: string;
}

export interface RiskStats {
  total: number;
  high: number;
  medium: number;
  low: number;
  recent: RiskLog[];
}

/**
 * Risk kaydını veritabanına kaydet
 */
export async function logRisk(riskLog: Omit<RiskLog, 'id' | 'created_at'>): Promise<RiskLog | null> {
  try {
    const supabase = await createClient();
    
    const { data, error } = await supabase
      .from('risk_logs')
      .insert({
        client_id: riskLog.client_id,
        session_id: riskLog.session_id || null,
        risk_level: riskLog.risk_level,
        keywords: riskLog.keywords,
        transcript_snippet: riskLog.transcript_snippet.substring(0, 1000), // Max 1000 karakter
        risk_score: riskLog.risk_score || calculateRiskScore(riskLog.risk_level),
        created_by: riskLog.created_by || null,
      })
      .select()
      .single();

    if (error) {
      console.error('Risk loglama hatası:', error);
      // Tablo yoksa oluşturmayı dene (fallback)
      if (error.code === '42P01') {
        console.warn('⚠️ risk_logs tablosu bulunamadı. Migration gerekli.');
      }
      return null;
    }

    return data as RiskLog;
  } catch (error) {
    console.error('Risk loglama exception:', error);
    return null;
  }
}

/**
 * Risk skorunu hesapla
 */
function calculateRiskScore(level: 'high' | 'medium' | 'low'): number {
  switch (level) {
    case 'high':
      return 80;
    case 'medium':
      return 50;
    case 'low':
      return 20;
    default:
      return 0;
  }
}

/**
 * Client için risk istatistiklerini getir
 */
export async function getRiskStats(clientId: string, days: number = 30): Promise<RiskStats | null> {
  try {
    const supabase = await createClient();
    const since = new Date();
    since.setDate(since.getDate() - days);

    const { data, error } = await supabase
      .from('risk_logs')
      .select('*')
      .eq('client_id', clientId)
      .gte('created_at', since.toISOString())
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Risk istatistikleri hatası:', error);
      return null;
    }

    const logs = (data || []) as RiskLog[];
    
    return {
      total: logs.length,
      high: logs.filter(l => l.risk_level === 'high').length,
      medium: logs.filter(l => l.risk_level === 'medium').length,
      low: logs.filter(l => l.risk_level === 'low').length,
      recent: logs.slice(0, 10), // Son 10 kayıt
    };
  } catch (error) {
    console.error('Risk istatistikleri exception:', error);
    return null;
  }
}

/**
 * Yüksek riskli kayıtları getir (bildirim için)
 */
export async function getHighRiskLogs(hours: number = 24): Promise<RiskLog[]> {
  try {
    const supabase = await createClient();
    const since = new Date();
    since.setHours(since.getHours() - hours);

    const { data, error } = await supabase
      .from('risk_logs')
      .select('*')
      .eq('risk_level', 'high')
      .gte('created_at', since.toISOString())
      .order('created_at', { ascending: false });

    if (error) {
      console.error('Yüksek risk kayıtları hatası:', error);
      return [];
    }

    return (data || []) as RiskLog[];
  } catch (error) {
    console.error('Yüksek risk kayıtları exception:', error);
    return [];
  }
}






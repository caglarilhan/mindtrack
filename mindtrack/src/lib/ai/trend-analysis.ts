import { getSOAPVersions, type SOAPVersion } from "./soap-versioning";
import { getRiskStats } from "./risk-logging";

export interface TrendData {
  period: string; // "2024-01", "2024-02", etc.
  riskScore: number;
  sessionCount: number;
  progressIndicators: {
    subjective: number; // Sentiment score (-1 to 1)
    assessment: number; // Improvement score (0 to 1)
  };
}

export interface ProgressAnalysis {
  overallTrend: 'improving' | 'stable' | 'declining';
  riskTrend: 'decreasing' | 'stable' | 'increasing';
  keyFindings: string[];
  recommendations: string[];
  progressScore: number; // 0-100
}

/**
 * Client için trend analizi yap
 */
export async function analyzeTrends(
  clientId: string,
  months: number = 6
): Promise<ProgressAnalysis | null> {
  try {
    // SOAP versiyonlarını al
    const versions = await getSOAPVersions(clientId, 100); // Son 100 versiyon
    
    if (versions.length < 2) {
      return {
        overallTrend: 'stable',
        riskTrend: 'stable',
        keyFindings: ['Yeterli veri yok'],
        recommendations: ['Daha fazla seans verisi gerekli'],
        progressScore: 50,
      };
    }

    // Risk istatistiklerini al
    const riskStats = await getRiskStats(clientId, months * 30);
    
    // Trend hesapla
    const riskTrend = calculateRiskTrend(riskStats);
    const progressTrend = calculateProgressTrend(versions);
    
    // Key findings
    const keyFindings = generateKeyFindings(versions, riskStats);
    
    // Recommendations
    const recommendations = generateRecommendations(progressTrend, riskTrend);
    
    // Progress score
    const progressScore = calculateProgressScore(versions, riskStats);

    return {
      overallTrend: progressTrend,
      riskTrend,
      keyFindings,
      recommendations,
      progressScore,
    };
  } catch (error) {
    console.error('Trend analizi hatası:', error);
    return null;
  }
}

/**
 * Risk trend'ini hesapla
 */
function calculateRiskTrend(riskStats: any): 'decreasing' | 'stable' | 'increasing' {
  if (!riskStats || riskStats.recent.length < 2) {
    return 'stable';
  }

  const recent = riskStats.recent.slice(0, 10);
  const older = riskStats.recent.slice(10, 20);

  const recentHighRisk = recent.filter((r: any) => r.risk_level === 'high').length;
  const olderHighRisk = older.filter((r: any) => r.risk_level === 'high').length;

  if (recentHighRisk > olderHighRisk) {
    return 'increasing';
  } else if (recentHighRisk < olderHighRisk) {
    return 'decreasing';
  }

  return 'stable';
}

/**
 * İlerleme trend'ini hesapla
 */
function calculateProgressTrend(versions: SOAPVersion[]): 'improving' | 'stable' | 'declining' {
  if (versions.length < 2) {
    return 'stable';
  }

  // Basit analiz: Assessment bölümündeki pozitif/negatif kelimeler
  const recent = versions.slice(0, 5);
  const older = versions.slice(5, 10);

  const recentScore = calculateSentimentScore(recent);
  const olderScore = calculateSentimentScore(older);

  if (recentScore > olderScore + 0.1) {
    return 'improving';
  } else if (recentScore < olderScore - 0.1) {
    return 'declining';
  }

  return 'stable';
}

/**
 * Sentiment skoru hesapla
 */
function calculateSentimentScore(versions: SOAPVersion[]): number {
  const positiveWords = ['iyileşme', 'ilerleme', 'iyi', 'daha iyi', 'azaldı', 'düzelme'];
  const negativeWords = ['kötüleşme', 'arttı', 'kötü', 'daha kötü', 'şiddetlendi'];

  let score = 0;
  let total = 0;

  for (const version of versions) {
    const assessment = version.soap_data.assessment.toLowerCase();
    const positive = positiveWords.filter(w => assessment.includes(w)).length;
    const negative = negativeWords.filter(w => assessment.includes(w)).length;
    
    score += (positive - negative);
    total += 1;
  }

  return total > 0 ? score / total : 0;
}

/**
 * Key findings oluştur
 */
function generateKeyFindings(versions: SOAPVersion[], riskStats: any): string[] {
  const findings: string[] = [];

  if (versions.length >= 5) {
    findings.push(`${versions.length} SOAP notu analiz edildi`);
  }

  if (riskStats) {
    if (riskStats.high > 0) {
      findings.push(`${riskStats.high} yüksek risk kaydı tespit edildi`);
    }
    if (riskStats.total > 0) {
      findings.push(`Toplam ${riskStats.total} risk kaydı mevcut`);
    }
  }

  // Son 3 versiyonun ortak temaları
  const recentAssessments = versions.slice(0, 3).map(v => v.soap_data.assessment);
  // Basit keyword analizi
  const commonThemes = findCommonThemes(recentAssessments);
  if (commonThemes.length > 0) {
    findings.push(`Ortak temalar: ${commonThemes.join(', ')}`);
  }

  return findings;
}

/**
 * Ortak temaları bul
 */
function findCommonThemes(assessments: string[]): string[] {
  const themes: string[] = [];
  const keywords = ['kaygı', 'depresyon', 'ilişki', 'iş', 'aile', 'uyku', 'yeme'];

  for (const keyword of keywords) {
    const count = assessments.filter(a => a.toLowerCase().includes(keyword)).length;
    if (count >= 2) {
      themes.push(keyword);
    }
  }

  return themes.slice(0, 3);
}

/**
 * Öneriler oluştur
 */
function generateRecommendations(
  progressTrend: 'improving' | 'stable' | 'declining',
  riskTrend: 'decreasing' | 'stable' | 'increasing'
): string[] {
  const recommendations: string[] = [];

  if (progressTrend === 'declining') {
    recommendations.push('İlerleme durumu dikkat gerektiriyor. Tedavi planını gözden geçirin.');
  }

  if (riskTrend === 'increasing') {
    recommendations.push('Risk seviyesi artıyor. Daha sık takip önerilir.');
  }

  if (progressTrend === 'improving' && riskTrend === 'decreasing') {
    recommendations.push('Pozitif ilerleme görülüyor. Mevcut yaklaşımı sürdürün.');
  }

  if (recommendations.length === 0) {
    recommendations.push('Düzenli takip ve değerlendirme önerilir.');
  }

  return recommendations;
}

/**
 * İlerleme skoru hesapla (0-100)
 */
function calculateProgressScore(versions: SOAPVersion[], riskStats: any): number {
  let score = 50; // Başlangıç

  // Versiyon sayısına göre artır
  if (versions.length >= 10) {
    score += 10;
  } else if (versions.length >= 5) {
    score += 5;
  }

  // Risk durumuna göre azalt
  if (riskStats) {
    const riskRatio = riskStats.high / Math.max(riskStats.total, 1);
    if (riskRatio > 0.3) {
      score -= 20;
    } else if (riskRatio > 0.1) {
      score -= 10;
    }
  }

  // Trend'e göre ayarla
  const trend = calculateProgressTrend(versions);
  if (trend === 'improving') {
    score += 15;
  } else if (trend === 'declining') {
    score -= 15;
  }

  return Math.max(0, Math.min(100, score));
}






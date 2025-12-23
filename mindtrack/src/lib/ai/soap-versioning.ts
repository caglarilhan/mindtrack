import { createClient } from "@/utils/supabase/server";

export interface SOAPVersion {
  id?: string;
  client_id: string;
  session_id?: string;
  version: number;
  soap_data: {
    subjective: string;
    objective: string;
    assessment: string;
    plan: string;
  };
  created_by?: string;
  created_at?: string;
  notes?: string;
}

/**
 * SOAP notu versiyonunu kaydet
 */
export async function saveSOAPVersion(
  clientId: string,
  soapData: SOAPVersion['soap_data'],
  sessionId?: string,
  notes?: string
): Promise<SOAPVersion | null> {
  try {
    const supabase = await createClient();
    
    // Son versiyonu bul
    const { data: lastVersion } = await supabase
      .from('soap_versions')
      .select('version')
      .eq('client_id', clientId)
      .order('version', { ascending: false })
      .limit(1)
      .single();

    const nextVersion = lastVersion ? lastVersion.version + 1 : 1;

    // Yeni versiyonu kaydet
    const { data, error } = await supabase
      .from('soap_versions')
      .insert({
        client_id: clientId,
        session_id: sessionId || null,
        version: nextVersion,
        soap_data: soapData,
        notes: notes || null,
      })
      .select()
      .single();

    if (error) {
      console.error('SOAP versiyonlama hatası:', error);
      if (error.code === '42P01') {
        console.warn('⚠️ soap_versions tablosu bulunamadı. Migration gerekli.');
      }
      return null;
    }

    return data as SOAPVersion;
  } catch (error) {
    console.error('SOAP versiyonlama exception:', error);
    return null;
  }
}

/**
 * Client için tüm versiyonları getir
 */
export async function getSOAPVersions(
  clientId: string,
  limit: number = 10
): Promise<SOAPVersion[]> {
  try {
    const supabase = await createClient();
    
    const { data, error } = await supabase
      .from('soap_versions')
      .select('*')
      .eq('client_id', clientId)
      .order('version', { ascending: false })
      .limit(limit);

    if (error) {
      console.error('SOAP versiyonları hatası:', error);
      return [];
    }

    return (data || []) as SOAPVersion[];
  } catch (error) {
    console.error('SOAP versiyonları exception:', error);
    return [];
  }
}

/**
 * Belirli bir versiyonu getir
 */
export async function getSOAPVersion(
  clientId: string,
  version: number
): Promise<SOAPVersion | null> {
  try {
    const supabase = await createClient();
    
    const { data, error } = await supabase
      .from('soap_versions')
      .select('*')
      .eq('client_id', clientId)
      .eq('version', version)
      .single();

    if (error) {
      console.error('SOAP versiyonu hatası:', error);
      return null;
    }

    return data as SOAPVersion;
  } catch (error) {
    console.error('SOAP versiyonu exception:', error);
    return null;
  }
}

/**
 * İki versiyonu karşılaştır
 */
export function compareVersions(
  version1: SOAPVersion,
  version2: SOAPVersion
): {
  subjective: { changed: boolean; diff: string };
  objective: { changed: boolean; diff: string };
  assessment: { changed: boolean; diff: string };
  plan: { changed: boolean; diff: string };
} {
  return {
    subjective: {
      changed: version1.soap_data.subjective !== version2.soap_data.subjective,
      diff: getDiff(version1.soap_data.subjective, version2.soap_data.subjective),
    },
    objective: {
      changed: version1.soap_data.objective !== version2.soap_data.objective,
      diff: getDiff(version1.soap_data.objective, version2.soap_data.objective),
    },
    assessment: {
      changed: version1.soap_data.assessment !== version2.soap_data.assessment,
      diff: getDiff(version1.soap_data.assessment, version2.soap_data.assessment),
    },
    plan: {
      changed: version1.soap_data.plan !== version2.soap_data.plan,
      diff: getDiff(version1.soap_data.plan, version2.soap_data.plan),
    },
  };
}

/**
 * Basit diff hesaplama (gerçek diff algoritması için library kullanılabilir)
 */
function getDiff(text1: string, text2: string): string {
  if (text1 === text2) return 'Değişiklik yok';
  
  const lines1 = text1.split('\n');
  const lines2 = text2.split('\n');
  
  const maxLines = Math.max(lines1.length, lines2.length);
  const diff: string[] = [];
  
  for (let i = 0; i < maxLines; i++) {
    const line1 = lines1[i] || '';
    const line2 = lines2[i] || '';
    
    if (line1 !== line2) {
      if (line1) diff.push(`- ${line1}`);
      if (line2) diff.push(`+ ${line2}`);
    }
  }
  
  return diff.length > 0 ? diff.join('\n') : 'Değişiklik yok';
}

/**
 * Son versiyonu getir
 */
export async function getLatestSOAPVersion(clientId: string): Promise<SOAPVersion | null> {
  try {
    const supabase = await createClient();
    
    const { data, error } = await supabase
      .from('soap_versions')
      .select('*')
      .eq('client_id', clientId)
      .order('version', { ascending: false })
      .limit(1)
      .single();

    if (error) {
      if (error.code === 'PGRST116') {
        // Kayıt yok
        return null;
      }
      console.error('Son SOAP versiyonu hatası:', error);
      return null;
    }

    return data as SOAPVersion;
  } catch (error) {
    console.error('Son SOAP versiyonu exception:', error);
    return null;
  }
}






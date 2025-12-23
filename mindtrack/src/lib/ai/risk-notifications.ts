import { getHighRiskLogs, type RiskLog } from './risk-logging';
import { createClient } from "@/utils/supabase/server";

export interface NotificationPreferences {
  email: boolean;
  sms: boolean;
  inApp: boolean;
}

/**
 * Risk bildirimleri gönder
 */
export async function sendRiskNotifications(
  riskLog: RiskLog,
  preferences?: NotificationPreferences
): Promise<void> {
  const prefs = preferences || {
    email: true,
    sms: false,
    inApp: true,
  };

  // Yüksek risk için bildirim gönder
  if (riskLog.risk_level === 'high') {
    if (prefs.email) {
      await sendEmailNotification(riskLog);
    }
    if (prefs.sms) {
      await sendSMSNotification(riskLog);
    }
    if (prefs.inApp) {
      await createInAppNotification(riskLog);
    }
  }

  // Orta risk için sadece in-app bildirim
  if (riskLog.risk_level === 'medium' && prefs.inApp) {
    await createInAppNotification(riskLog);
  }
}

/**
 * Email bildirimi gönder
 */
async function sendEmailNotification(riskLog: RiskLog): Promise<void> {
  try {
    const supabase = await createClient();
    
    // Client bilgilerini al
    const { data: client } = await supabase
      .from('clients')
      .select('name, email')
      .eq('id', riskLog.client_id)
      .single();

    if (!client) {
      console.warn('Client bulunamadı, email gönderilemedi');
      return;
    }

    // Email gönderme API'si (örnek - gerçek implementasyon email servisine bağlı)
    const emailContent = {
      to: client.email || 'provider@example.com', // Provider email'i
      subject: `🚨 YÜKSEK RİSK UYARISI - ${client.name}`,
      html: `
        <h2>Yüksek Risk Tespit Edildi</h2>
        <p><strong>Hasta:</strong> ${client.name}</p>
        <p><strong>Risk Seviyesi:</strong> ${riskLog.risk_level.toUpperCase()}</p>
        <p><strong>Tespit Edilen Kelimeler:</strong> ${riskLog.keywords.join(', ')}</p>
        <p><strong>Transkript Özeti:</strong></p>
        <pre>${riskLog.transcript_snippet.substring(0, 500)}</pre>
        <p><strong>Tarih:</strong> ${new Date(riskLog.created_at || Date.now()).toLocaleString('tr-TR')}</p>
        <p><a href="${process.env.NEXT_PUBLIC_APP_URL}/dashboard/psychologist/clients/${riskLog.client_id}">Hasta Detaylarına Git</a></p>
      `,
    };

    // Email gönderme (gerçek implementasyon)
    console.log('📧 Email gönderiliyor:', emailContent);
    
    // TODO: Gerçek email servisi entegrasyonu (SendGrid, Resend, vb.)
    // await sendEmail(emailContent);
    
  } catch (error) {
    console.error('Email bildirimi hatası:', error);
  }
}

/**
 * SMS bildirimi gönder
 */
async function sendSMSNotification(riskLog: RiskLog): Promise<void> {
  try {
    // SMS gönderme (gerçek implementasyon)
    console.log('📱 SMS gönderiliyor:', {
      clientId: riskLog.client_id,
      riskLevel: riskLog.risk_level,
      keywords: riskLog.keywords,
    });
    
    // TODO: Gerçek SMS servisi entegrasyonu (Twilio, MessageBird, vb.)
    // await sendSMS(phoneNumber, message);
    
  } catch (error) {
    console.error('SMS bildirimi hatası:', error);
  }
}

/**
 * In-app bildirim oluştur
 */
async function createInAppNotification(riskLog: RiskLog): Promise<void> {
  try {
    const supabase = await createClient();
    
    // Provider'ı bul (client'in sahibi)
    const { data: client } = await supabase
      .from('clients')
      .select('owner_id')
      .eq('id', riskLog.client_id)
      .single();

    if (!client?.owner_id) {
      console.warn('Provider bulunamadı, in-app bildirim oluşturulamadı');
      return;
    }

    // Bildirim oluştur
    const { error } = await supabase
      .from('notifications')
      .insert({
        user_id: client.owner_id,
        type: 'risk_alert',
        title: `🚨 ${riskLog.risk_level === 'high' ? 'YÜKSEK' : 'ORTA'} RİSK TESPİT EDİLDİ`,
        message: `Hastada risk tespit edildi. Kelimeler: ${riskLog.keywords.join(', ')}`,
        data: {
          client_id: riskLog.client_id,
          risk_level: riskLog.risk_level,
          risk_log_id: riskLog.id,
        },
        read: false,
        created_at: new Date().toISOString(),
      });

    if (error) {
      console.error('In-app bildirim hatası:', error);
      // Tablo yoksa fallback
      if (error.code === '42P01') {
        console.warn('⚠️ notifications tablosu bulunamadı. Migration gerekli.');
      }
    }
  } catch (error) {
    console.error('In-app bildirim exception:', error);
  }
}

/**
 * Periyodik risk kontrolü (cron job için)
 */
export async function checkAndNotifyHighRisks(): Promise<void> {
  try {
    const highRiskLogs = await getHighRiskLogs(24); // Son 24 saat
    
    for (const log of highRiskLogs) {
      // Bildirim gönderilmemişse gönder
      await sendRiskNotifications(log);
    }
    
    console.log(`✅ ${highRiskLogs.length} yüksek risk kaydı kontrol edildi`);
  } catch (error) {
    console.error('Periyodik risk kontrolü hatası:', error);
  }
}






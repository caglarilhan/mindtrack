# 🎯 Sprint 1: Risk & Güvenlik - Detaylı Plan

## 📅 Sprint Bilgileri
- **Süre:** 1 Hafta (5 iş günü)
- **Başlangıç:** Bugün
- **Bitiş:** +7 gün
- **Durum:** 🔄 In Progress

---

## ✅ Tamamlananlar

- [x] Risk analizi fonksiyonu (basit)
- [x] Real-time risk tespiti
- [x] Görsel uyarılar
- [x] Otomatik kaydetme (temel)
- [x] PDF export (temel)

---

## 📋 Kalan Görevler

### Task 1.1: Risk Analizi Sistemi Geliştirme (2 gün)

#### Alt Görevler:
- [ ] Risk loglama sistemi
  - [ ] Veritabanı tablosu oluştur (`risk_logs`)
  - [ ] Risk kayıtları kaydetme
  - [ ] Risk geçmişi görüntüleme
  - [ ] Risk istatistikleri

- [ ] Risk bildirimleri
  - [ ] Email bildirimi (yüksek risk)
  - [ ] SMS bildirimi (opsiyonel)
  - [ ] In-app bildirim
  - [ ] Bildirim ayarları

- [ ] Gelişmiş risk analizi
  - [ ] Context-aware risk analizi
  - [ ] Pattern recognition
  - [ ] Machine learning entegrasyonu (opsiyonel)
  - [ ] Risk skorlama

**Kod Örneği:**
```typescript
// risk-logging.ts
export async function logRisk(
  clientId: string,
  riskLevel: 'high' | 'medium' | 'low',
  keywords: string[],
  transcript: string
) {
  await supabase.from('risk_logs').insert({
    client_id: clientId,
    risk_level: riskLevel,
    keywords: keywords,
    transcript_snippet: transcript.substring(0, 500),
    created_at: new Date().toISOString()
  });
}
```

**Süre:** 2 gün  
**Öncelik:** Yüksek

---

### Task 1.2: Otomatik Kaydetme İyileştirme (1 gün)

#### Alt Görevler:
- [ ] Versiyonlama sistemi
  - [ ] Versiyon numarası
  - [ ] Versiyon geçmişi
  - [ ] Versiyon karşılaştırma

- [ ] Geri alma özelliği
  - [ ] Son versiyona geri dön
  - [ ] Versiyon seçimi
  - [ ] Geri alma onayı

- [ ] Otomatik kaydetme ayarları
  - [ ] Kullanıcı tercihleri
  - [ ] Otomatik kaydetme aç/kapat
  - [ ] Kaydetme sıklığı

**Kod Örneği:**
```typescript
// versioning.ts
export async function saveSOAPVersion(
  clientId: string,
  soapData: SOAPNote,
  version: number
) {
  await supabase.from('soap_versions').insert({
    client_id: clientId,
    version: version,
    soap_data: soapData,
    created_at: new Date().toISOString()
  });
}
```

**Süre:** 1 gün  
**Öncelik:** Orta

---

### Task 1.3: PDF Export İyileştirme (1 gün)

#### Alt Görevler:
- [ ] Gelişmiş formatlama
  - [ ] Header ve footer
  - [ ] Logo ekleme
  - [ ] Sayfa numaraları
  - [ ] Tarih ve saat

- [ ] Çoklu sayfa desteği
  - [ ] Sayfa kırılması
  - [ ] Tablo formatı
  - [ ] Grafik ekleme (opsiyonel)

- [ ] PDF ayarları
  - [ ] Sayfa boyutu
  - [ ] Font ayarları
  - [ ] Renk ayarları
  - [ ] Önizleme

**Kod Örneği:**
```typescript
// pdf-export.ts
export async function exportSOAPToPDF(
  soapData: SOAPNote,
  options: {
    includeLogo?: boolean;
    pageSize?: 'A4' | 'Letter';
    font?: string;
  }
) {
  const doc = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: options.pageSize || 'A4'
  });
  
  // Logo ekle
  if (options.includeLogo) {
    // Logo ekleme kodu
  }
  
  // Header
  doc.setFontSize(16);
  doc.text('SOAP Notu', 20, 20);
  
  // Tarih
  doc.setFontSize(10);
  doc.text(`Tarih: ${new Date().toLocaleDateString('tr-TR')}`, 20, 30);
  
  // SOAP içeriği
  // ...
  
  return doc;
}
```

**Süre:** 1 gün  
**Öncelik:** Orta

---

### Task 1.4: Güvenlik İyileştirmeleri (1 gün)

#### Alt Görevler:
- [ ] Rate limiting
  - [ ] API rate limit
  - [ ] Kullanıcı bazlı limit
  - [ ] IP bazlı limit
  - [ ] Limit aşımı uyarıları

- [ ] Input validation
  - [ ] Transkript validasyonu
  - [ ] XSS koruması
  - [ ] SQL injection koruması
  - [ ] Dosya upload validasyonu

- [ ] API key rotation
  - [ ] Otomatik rotation
  - [ ] Key expiration
  - [ ] Key yedekleme

- [ ] Audit logging
  - [ ] Tüm işlemleri logla
  - [ ] Log analizi
  - [ ] Güvenlik olayları

**Kod Örneği:**
```typescript
// security.ts
export function rateLimitMiddleware(
  req: Request,
  limit: number = 10,
  windowMs: number = 60000
) {
  // Rate limiting logic
}

export function validateTranscript(transcript: string) {
  // XSS koruması
  const sanitized = transcript
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/javascript:/gi, '')
    .replace(/on\w+\s*=/gi, '');
  
  // Uzunluk kontrolü
  if (transcript.length > 50000) {
    throw new Error('Transkript çok uzun');
  }
  
  return sanitized;
}
```

**Süre:** 1 gün  
**Öncelik:** Yüksek

---

## 📊 Günlük Plan

### Gün 1 (Bugün)
- ✅ Risk analizi fonksiyonu (tamamlandı)
- 🔄 Risk loglama sistemi (devam ediyor)
- 📋 Risk bildirimleri (planlandı)

### Gün 2
- 📋 Risk bildirimleri tamamlama
- 📋 Gelişmiş risk analizi
- 📋 Test ve dokümantasyon

### Gün 3
- 📋 Versiyonlama sistemi
- 📋 Geri alma özelliği
- 📋 Otomatik kaydetme ayarları

### Gün 4
- 📋 PDF export iyileştirme
- 📋 Gelişmiş formatlama
- 📋 Çoklu sayfa desteği

### Gün 5
- 📋 Güvenlik iyileştirmeleri
- 📋 Rate limiting
- 📋 Input validation
- 📋 Test ve demo hazırlığı

---

## 🎯 Definition of Done

### Sprint 1 için:
- [x] Risk analizi çalışıyor
- [ ] Risk loglama aktif
- [ ] Risk bildirimleri çalışıyor
- [x] Otomatik kaydetme aktif
- [ ] Versiyonlama çalışıyor
- [x] PDF export çalışıyor
- [ ] PDF formatlama iyileştirildi
- [ ] Güvenlik testleri geçti
- [ ] Dokümantasyon güncellendi
- [ ] Demo hazır

---

## 🚀 Başlangıç

**Şimdi yapılacak:**
1. Risk loglama sistemi oluştur
2. Risk bildirimleri ekle
3. Versiyonlama sistemi kur
4. PDF export iyileştir
5. Güvenlik testleri yap

**Hazır mısın? Başlayalım! 🎯**






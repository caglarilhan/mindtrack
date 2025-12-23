# 🚀 Gemini AI Entegrasyonu - Detaylı Kullanım Kılavuzu

## 📋 İçindekiler
1. [Mevcut Durum](#mevcut-durum)
2. [Frontend Entegrasyonu](#frontend-entegrasyonu)
3. [API Kullanımı](#api-kullanımı)
4. [Test Etme](#test-etme)
5. [Sonraki Adımlar](#sonraki-adımlar)

---

## ✅ Mevcut Durum

### Tamamlananlar:
- ✅ Gemini API key eklendi (`.env.local`)
- ✅ Gemini Service oluşturuldu (`lib/ai/gemini-service.ts`)
- ✅ AI Orchestrator hazır (`lib/ai/orchestrator.ts`)
- ✅ SOAP API route oluşturuldu (`api/telehealth/generate-soap/route.ts`)
- ✅ Test başarılı (SOAP notu oluşturuluyor)

### Şu An Ne Yapabilirsin:
1. **Backend'den direkt kullanım**: Gemini servisini kod içinde çağırabilirsin
2. **API endpoint**: `/api/telehealth/generate-soap` üzerinden SOAP notu oluşturabilirsin
3. **Test scripti**: `npx tsx test-gemini-direct.ts` ile test edebilirsin

---

## 🎯 Frontend Entegrasyonu

### Adım 1: Session Assistant Sayfasını Bul

Session Assistant sayfası muhtemelen şu konumda:
- `/app/dashboard/session/page.tsx` veya
- `/app/dashboard/psychologist/sessions/page.tsx`

Bu sayfada şu özellikler olmalı:
- Ses kaydı başlat/durdur butonu
- Canlı transkript alanı
- SOAP notu sekmesi (S, O, A, P)

### Adım 2: SOAP Oluşturma Butonunu Güncelle

**Mevcut kod muhtemelen şöyle:**
```typescript
// Eski kod (mock veya OpenAI only)
const handleGenerateSOAP = async () => {
  // Mock veya OpenAI çağrısı
};
```

**Yeni kod (Gemini + Orchestrator):**
```typescript
const handleGenerateSOAP = async () => {
  try {
    setLoading(true);
    
    const response = await fetch('/api/telehealth/generate-soap', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        transcript: transcriptText, // Seans transkripti
        mode: 'standard', // veya 'premium', 'consultation'
        sessionId: currentSessionId,
        clientId: currentClientId,
      }),
    });
    
    if (!response.ok) {
      throw new Error('SOAP notu oluşturulamadı');
    }
    
    const data = await response.json();
    
    // SOAP notunu state'e kaydet
    setSoapNotes({
      subjective: data.soap.subjective,
      objective: data.soap.objective,
      assessment: data.soap.assessment,
      plan: data.soap.plan,
    });
    
  } catch (error) {
    console.error('SOAP oluşturma hatası:', error);
    // Hata mesajı göster
  } finally {
    setLoading(false);
  }
};
```

### Adım 3: Mod Seçimi Ekleyin (Opsiyonel)

Premium kullanıcılar için "Derinlemesine Analiz" butonu:

```typescript
const [analysisMode, setAnalysisMode] = useState<'standard' | 'premium' | 'consultation'>('standard');

// UI'da:
<Button 
  onClick={() => setAnalysisMode('premium')}
  variant={analysisMode === 'premium' ? 'default' : 'outline'}
>
  🔬 Derinlemesine Analiz (Premium)
</Button>

<Button 
  onClick={() => setAnalysisMode('consultation')}
  variant={analysisMode === 'consultation' ? 'default' : 'outline'}
>
  👥 İkinci Görüş (Konsültasyon)
</Button>
```

---

## 🔌 API Kullanımı

### Endpoint: `/api/telehealth/generate-soap`

**Method:** `POST`

**Headers:**
```json
{
  "Content-Type": "application/json"
}
```

**Body:**
```json
{
  "transcript": "Terapist: Merhaba...\nDanışan: İyi değilim...",
  "mode": "standard", // "standard" | "premium" | "consultation"
  "sessionId": "123", // Opsiyonel
  "clientId": "456", // Opsiyonel
  "patientData": { // Opsiyonel (karmaşık vakalar için)
    "sessions": [...],
    "rawData": "...",
    "riskFactors": [...],
    "sessionCount": 10
  }
}
```

**Response:**
```json
{
  "success": true,
  "soap": {
    "subjective": "Danışan...",
    "objective": "Gözlemler...",
    "assessment": "Değerlendirme...",
    "plan": "Plan..."
  },
  "mode": "standard",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Modlar:

1. **`standard`** (Varsayılan):
   - Basit vakalar: Sadece Gemini (ücretsiz, hızlı)
   - Karmaşık vakalar: Gemini → OpenAI (hibrit)

2. **`premium`**:
   - Her zaman hibrit mod (Gemini → OpenAI)
   - Daha detaylı analiz

3. **`consultation`**:
   - Paralel işleme (Gemini + OpenAI aynı anda)
   - Model karşılaştırması
   - İkinci görüş özelliği

---

## 🧪 Test Etme

### 1. Backend Testi (Zaten Yaptık)
```bash
cd /Users/caglarilhan/mindtrack/mindtrack
npx tsx test-gemini-direct.ts
```

### 2. API Testi (Postman/curl)
```bash
curl -X POST http://localhost:3000/api/telehealth/generate-soap \
  -H "Content-Type: application/json" \
  -H "Cookie: your-auth-cookie" \
  -d '{
    "transcript": "Terapist: Merhaba, bugün nasılsın?\nDanışan: İyi değilim, çok kaygılıyım.",
    "mode": "standard"
  }'
```

### 3. Frontend Testi
1. Development server'ı başlat: `npm run dev`
2. Session Assistant sayfasına git
3. Bir transkript gir veya ses kaydı yap
4. "SOAP Notu Oluştur" butonuna tıkla
5. Sonuçları kontrol et

---

## 📝 Kod Örnekleri

### Örnek 1: Basit Kullanım (Sadece Gemini)

```typescript
import { getGeminiService } from '@/lib/ai/gemini-service';

const gemini = getGeminiService();
const soap = await gemini.generateSOAP(transcriptText);
console.log(soap.subjective);
```

### Örnek 2: Orchestrator ile (Router + Hybrid)

```typescript
import { getAIOrchestrator } from '@/lib/ai/orchestrator';

const orchestrator = getAIOrchestrator();
const soap = await orchestrator.processSOAP(
  transcriptText,
  'standard', // mode
  patientData // opsiyonel
);
```

### Örnek 3: React Component İçinde

```typescript
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';

export function SOAPGenerator() {
  const [transcript, setTranscript] = useState('');
  const [soap, setSoap] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/telehealth/generate-soap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transcript,
          mode: 'standard',
        }),
      });
      
      const data = await response.json();
      setSoap(data.soap);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <Textarea
        value={transcript}
        onChange={(e) => setTranscript(e.target.value)}
        placeholder="Seans transkriptini buraya yapıştır..."
      />
      <Button onClick={handleGenerate} disabled={loading}>
        {loading ? 'Oluşturuluyor...' : 'SOAP Notu Oluştur'}
      </Button>
      
      {soap && (
        <div>
          <h3>Subjective</h3>
          <p>{soap.subjective}</p>
          {/* Diğer bölümler... */}
        </div>
      )}
    </div>
  );
}
```

---

## 🎯 Sonraki Adımlar

### Hemen Yapılacaklar (Bugün):

1. **Session Assistant sayfasını bul**
   ```bash
   find . -name "session*.tsx" -type f
   ```

2. **SOAP oluşturma fonksiyonunu güncelle**
   - Mevcut kodu bul
   - API endpoint'i çağıracak şekilde değiştir

3. **Test et**
   - Frontend'de bir transkript gir
   - SOAP notu oluştur butonuna tıkla
   - Sonuçları kontrol et

### Bu Hafta Yapılacaklar:

1. **Premium özellik ekle**
   - "Derinlemesine Analiz" butonu
   - Konsültasyon modu

2. **Hata yönetimi**
   - Loading states
   - Error messages
   - Retry mekanizması

3. **UI iyileştirmeleri**
   - Progress bar
   - Sonuçları güzel göster
   - Kopyala/indir butonları

### Gelecek Haftalar:

1. **Hybrid flow testi**
   - OpenAI entegrasyonu
   - Model karşılaştırması

2. **Performans optimizasyonu**
   - Caching
   - Rate limiting
   - Async processing

3. **Analytics**
   - Kullanım istatistikleri
   - Model performansı
   - Maliyet takibi

---

## ❓ Sık Sorulan Sorular

### Q: API key güvenli mi?
A: Evet, `.env.local` dosyasında ve `.gitignore`'da. Production'da environment variable olarak ayarla.

### Q: Maliyet ne kadar?
A: 
- Gemini Free Tier: 1M token/ay ücretsiz
- Standart kullanım: ~$0.05/vaka
- Premium: ~$0.08/vaka (hibrit)
- Konsültasyon: ~$2.05/vaka

### Q: Hangi modu kullanmalıyım?
A: 
- Çoğu vaka için: `standard` (otomatik router)
- Detaylı analiz için: `premium`
- İkinci görüş için: `consultation`

### Q: Hata alırsam ne yapmalıyım?
A: 
1. Console'da hata mesajını kontrol et
2. API key'in doğru olduğundan emin ol
3. Network tab'da request'i kontrol et
4. Backend loglarını kontrol et

---

## 🆘 Yardım

Sorun yaşarsan:
1. `test-gemini-direct.ts` scriptini çalıştır (backend testi)
2. Browser console'u kontrol et (frontend hataları)
3. Network tab'ı kontrol et (API çağrıları)
4. Backend loglarını kontrol et (server hataları)

---

**Hazır! Şimdi Session Assistant sayfasını bulup entegre edebilirsin! 🚀**






# 📝 Adım Adım: Gemini AI Entegrasyonu

## 🎯 Ne Yapacağız?

Session Assistant veya Notes sayfasında, seans transkriptinden otomatik SOAP notu oluşturacağız. Gemini AI kullanarak!

---

## 📋 Adım 1: Hangi Dosyayı Düzenleyeceğiz?

**İki seçenek var:**

### Seçenek A: Notes Tab (Mevcut)
- Dosya: `src/components/tabs/notes-tab.tsx`
- Bu dosyada zaten AI note generation var
- Sadece endpoint'i değiştireceğiz

### Seçenek B: Session Assistant (Yeni sayfa)
- Dosya: `src/app/dashboard/session/page.tsx` (yoksa oluştur)
- Veya: `src/app/dashboard/psychologist/sessions/page.tsx`

**Ben Seçenek A'yı öneriyorum çünkü:**
- ✅ Zaten AI entegrasyonu var
- ✅ SOAP formatı destekleniyor
- ✅ Sadece endpoint değişikliği yeterli

---

## 🔧 Adım 2: Notes Tab'ı Güncelle

### 2.1. Dosyayı Aç
```bash
code src/components/tabs/notes-tab.tsx
```

### 2.2. Mevcut Kodu Bul

Şu satırları bul (yaklaşık 126-159. satırlar):
```typescript
const handleAIGenerate = async () => {
  // ... mevcut kod
  const response = await fetch('/api/ai-notes', {
    method: 'POST',
    // ...
  });
};
```

### 2.3. Yeni Kodu Ekle

**Eski kod:**
```typescript
const response = await fetch('/api/ai-notes', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    action: 'generate',
    data: aiNoteData
  })
});
```

**Yeni kod (Gemini ile):**
```typescript
// Transkript varsa direkt SOAP oluştur
if (transcriptText) {
  const response = await fetch('/api/telehealth/generate-soap', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      transcript: transcriptText,
      mode: 'standard', // veya 'premium'
      sessionId: sessionId,
      clientId: clientId,
    }),
  });
  
  const data = await response.json();
  
  // SOAP notunu state'e kaydet
  setContent(`S: ${data.soap.subjective}\n\nO: ${data.soap.objective}\n\nA: ${data.soap.assessment}\n\nP: ${data.soap.plan}`);
}
```

---

## 🎨 Adım 3: UI'ya Transkript Alanı Ekle

### 3.1. State Ekle

```typescript
const [transcript, setTranscript] = useState('');
const [sessionId, setSessionId] = useState('');
```

### 3.2. Textarea Ekle (UI'da)

```typescript
<div className="space-y-4">
  <div>
    <Label>Seans Transkripti</Label>
    <Textarea
      value={transcript}
      onChange={(e) => setTranscript(e.target.value)}
      placeholder="Seans transkriptini buraya yapıştır..."
      rows={10}
    />
  </div>
  
  <Button 
    onClick={handleGenerateSOAP}
    disabled={!transcript || loading}
  >
    {loading ? 'SOAP Notu Oluşturuluyor...' : '🤖 AI ile SOAP Notu Oluştur'}
  </Button>
</div>
```

---

## 🚀 Adım 4: Tam Fonksiyon Örneği

```typescript
const handleGenerateSOAP = async () => {
  if (!transcript.trim()) {
    setError('Lütfen transkript girin');
    return;
  }

  setAiLoading(true);
  setError(null);

  try {
    const response = await fetch('/api/telehealth/generate-soap', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        transcript: transcript,
        mode: 'standard', // 'standard' | 'premium' | 'consultation'
        sessionId: sessionId || undefined,
        clientId: clientId || undefined,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || 'SOAP notu oluşturulamadı');
    }

    const data = await response.json();
    
    // SOAP notunu formatla ve göster
    const formattedSOAP = `S (Subjective):\n${data.soap.subjective}\n\nO (Objective):\n${data.soap.objective}\n\nA (Assessment):\n${data.soap.assessment}\n\nP (Plan):\n${data.soap.plan}`;
    
    setContent(formattedSOAP);
    setNoteType('SOAP');
    
    // Başarı mesajı
    console.log('✅ SOAP notu başarıyla oluşturuldu!');
    
  } catch (error: any) {
    console.error('SOAP oluşturma hatası:', error);
    setError(error.message || 'SOAP notu oluşturulamadı');
  } finally {
    setAiLoading(false);
  }
};
```

---

## 🧪 Adım 5: Test Et

### 5.1. Development Server'ı Başlat
```bash
cd /Users/caglarilhan/mindtrack/mindtrack
npm run dev
```

### 5.2. Tarayıcıda Aç
```
http://localhost:3000/dashboard/psychologist/clients
```

### 5.3. Notes Tab'ına Git
- Bir hasta seç
- Notes sekmesine tıkla
- Transkript alanına bir şey yaz
- "AI ile SOAP Notu Oluştur" butonuna tıkla

### 5.4. Sonuçları Kontrol Et
- SOAP notu oluşturuldu mu?
- Tüm bölümler (S, O, A, P) dolu mu?
- Hata var mı? (Console'u kontrol et)

---

## 🎯 Adım 6: İyileştirmeler (Opsiyonel)

### 6.1. Mod Seçimi Ekleyin

```typescript
const [analysisMode, setAnalysisMode] = useState<'standard' | 'premium' | 'consultation'>('standard');

// UI'da:
<div className="flex gap-2 mb-4">
  <Button
    variant={analysisMode === 'standard' ? 'default' : 'outline'}
    onClick={() => setAnalysisMode('standard')}
    size="sm"
  >
    Standart
  </Button>
  <Button
    variant={analysisMode === 'premium' ? 'default' : 'outline'}
    onClick={() => setAnalysisMode('premium')}
    size="sm"
  >
    🔬 Premium
  </Button>
  <Button
    variant={analysisMode === 'consultation' ? 'default' : 'outline'}
    onClick={() => setAnalysisMode('consultation')}
    size="sm"
  >
    👥 Konsültasyon
  </Button>
</div>
```

### 6.2. Loading State Göster

```typescript
{aiLoading && (
  <div className="flex items-center gap-2 text-sm text-muted-foreground">
    <Loader2 className="h-4 w-4 animate-spin" />
    <span>SOAP notu oluşturuluyor... (~10-15 saniye)</span>
  </div>
)}
```

### 6.3. Sonuçları Güzel Göster

```typescript
{data.soap && (
  <div className="space-y-4 mt-4">
    <div>
      <h4 className="font-semibold mb-2">Subjective (S)</h4>
      <p className="text-sm">{data.soap.subjective}</p>
    </div>
    <div>
      <h4 className="font-semibold mb-2">Objective (O)</h4>
      <p className="text-sm">{data.soap.objective}</p>
    </div>
    {/* ... */}
  </div>
)}
```

---

## 📊 Adım 7: Hata Ayıklama

### Sorun: API çağrısı çalışmıyor

**Kontrol listesi:**
1. ✅ API key doğru mu? (`.env.local` dosyasını kontrol et)
2. ✅ Server çalışıyor mu? (`npm run dev`)
3. ✅ Authentication var mı? (Login oldun mu?)
4. ✅ Network tab'da request görünüyor mu?
5. ✅ Console'da hata var mı?

### Sorun: SOAP notu boş geliyor

**Çözüm:**
- Transkript yeterince uzun mu? (en az 100 karakter)
- API response'u kontrol et (Network tab)
- Backend loglarını kontrol et

### Sorun: Parse hatası

**Çözüm:**
- `gemini-service.ts` dosyasındaki `parseSOAP` fonksiyonunu kontrol et
- Ham response'u console'a yazdır

---

## ✅ Başarı Kriterleri

Şunlar çalışıyorsa başarılı:

- ✅ Transkript girip butona tıklayınca SOAP notu oluşuyor
- ✅ S, O, A, P bölümleri dolu geliyor
- ✅ Türkçe içerik üretiliyor
- ✅ Hata yok (console temiz)
- ✅ Loading state çalışıyor

---

## 🎉 Sonuç

Artık:
1. ✅ Gemini AI entegrasyonu çalışıyor
2. ✅ SOAP notu otomatik oluşturuluyor
3. ✅ Frontend'e bağlandı
4. ✅ Test edildi

**Sonraki adımlar:**
- Premium özellik ekle
- Konsültasyon modu ekle
- UI iyileştirmeleri yap

---

**Sorun olursa:**
1. Console'u kontrol et
2. Network tab'ı kontrol et
3. Backend loglarını kontrol et
4. `test-gemini-direct.ts` scriptini çalıştır

**Hazırsın! Başlayalım! 🚀**






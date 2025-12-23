# 🔑 Gemini API Key Nasıl Alınır?

## Sorun
Verdiğiniz API key (`gen-lang-client-0595097888`) geçersiz görünüyor. Google Gemini API key'leri genellikle `AIza...` ile başlar.

## ✅ Doğru API Key Nasıl Alınır?

### Adım 1: Google AI Studio'ya Git
1. Tarayıcıda şu adrese git: https://aistudio.google.com/
2. Google hesabınla giriş yap

### Adım 2: API Key Oluştur
1. Sağ üstteki **"Get API Key"** butonuna tıkla
2. Veya direkt: https://aistudio.google.com/app/apikey
3. **"Create API Key"** butonuna tıkla
4. Yeni bir proje oluştur veya mevcut projeyi seç
5. API key oluşturulacak

### Adım 3: API Key Formatı
Doğru API key şu şekilde görünür:
```
AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```
(32+ karakter, `AIza` ile başlar)

### Adım 4: .env.local'e Ekle
```bash
GOOGLE_GEMINI_API_KEY=AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## 🆓 Free Tier Limitleri
- **1M token/ay ücretsiz**
- **15 RPM** (requests per minute)
- **1M TPM** (tokens per minute)

## ⚠️ Not
Verdiğiniz key (`gen-lang-client-0595097888`) muhtemelen:
- Farklı bir servis için olabilir
- Eski/geçersiz bir key olabilir
- Yanlış kopyalanmış olabilir

## 🔄 Sonraki Adım
Doğru API key'i aldıktan sonra:
1. `.env.local` dosyasını güncelle
2. Test scriptini tekrar çalıştır: `npx tsx test-gemini-direct.ts`






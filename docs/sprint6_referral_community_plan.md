# Sprint 6 – Referral Network & Community

## Amaç
Klinikler, bağımsız ruh sağlığı profesyonelleri ve sosyal hizmet uzmanları arasında sevk (referral) ağı ve güvenli community özelliklerini kurmak.

## Modüller
1. **Referral Directory (B2B)**
   - `/dashboard/referrals` sayfası
   - Filtreler: uzmanlık, ülke/bölge (US/EU), sigorta paneli
   - Sevk oluşturma: "Refer to provider" formu, status tracking (pending/accepted/closed)
2. **Referral API & Store**
   - Tablolar: `referral_contacts`, `referrals`
   - Endpoint taslakları: `/api/referrals` (CRUD), `/api/referrals/stats`
3. **Community Hub (Clinician Support)**
   - `/dashboard/community` sayfası (yalnızca clinician/admin rolleri)
   - Board: case discussion tags (anonimleştirilmiş), guideline/link paylaşımı (sadece placeholder)
4. **Permission & Guardrails**
   - RLS için: sadece aynı clinic veya açık paylaşım (de-id) kuralları
   - US/EU için farklı flag’ler: community özelliğinin ülkeye göre açılıp kapanması dokümanı

## Teslim Kriterleri
- Referral directory ve community için Next.js sayfaları ve client component placeholder'ları hazır
- Referral tabloları ve API taslakları dokümante edildi (`docs/referral_schema.md`)
- Permission ve de-identification için kısa guideline yazıldı (`docs/community_guardrails.md`)

## KPI / Test
- [ ] `/dashboard/referrals` açılıp dummy provider listesi ve "Create referral" butonunu gösteriyor
- [ ] `/dashboard/community` açılıp placeholder board / info kartlarını gösteriyor
- [ ] Dokümantasyon dosyaları repo'da ve okunabilir

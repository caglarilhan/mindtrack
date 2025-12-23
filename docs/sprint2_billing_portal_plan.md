# Sprint 2 – Billing & Portal Hardening

## Amaç
Clearinghouse entegrasyonu ile sigorta iş akışını üretim seviyesine taşımak, aynı zamanda hasta/caregiver portal deneyimini sunmak.

## Modüller
1. **Clearinghouse Connector**
   - Payer bağlantı kayıtları (`payer_connections`)
   - 837/270 kuyruk tablosu (`claims_queue`)
   - ERA/835 olay kaydı (`era_events`)
   - Connector servis katmanı (`clearinghouse.ts`)
2. **Claims API**
   - `/api/billing/claims` → claim oluşturma/kuyruğa alma
   - `/api/billing/claims/[id]` → durum & ERA özetleri
3. **Denial Cockpit UI**
   - Claim state board, ERA event feed, yeniden gönderme butonu
4. **Client/Caregiver Portal (MVP)**
   - `/portal/client` & `/portal/caregiver` sayfaları (token bazlı)
   - Özet kartları: seanslar, faturalar, care gap
5. **Notifications**
   - Claim durumu değiştiğinde yöneticilere e-posta/SMS

## Teknik Adımlar
1. Migration `20250207_0007_clearinghouse.sql`
2. `src/lib/server/clearinghouse.ts`
3. API rotaları (claims, portal data)
4. Dashboard UI güncellemeleri (billing cockpit)
5. Portal sayfaları + token doğrulama

## Test KPI
- [ ] Demo claim Availity sandbox’a gönderim logu
- [ ] ERA CSV’si ingest edilip denial board’da gösteriliyor
- [ ] Portal token → hasta seans/claim özetleri çıkıyor

# Sprint 4 – Integration Marketplace & Workflow Automation

## Amaç
MindTrack'i üçüncü parti servislerle (Google, Zoom, Twilio, Stripe, Resend vb.) bağlamak için tek noktadan yönetilen bir marketplace kurmak ve entegrasyonlara bağlı otomasyon akışlarını (webhook + rule builder) devreye almak.

## Modüller
1. **Integration Marketplace UI**
   - `/dashboard/settings/integrations` sayfası
   - Kartlar: logo, kısa açıklama, bağlantı durumu (Connected/Needs Auth/Issue)
   - Ayrıntı paneli: OAuth bağlantısı, API anahtarı, log özeti
2. **Integration API & Store**
   - Supabase tabloları: `integrations_catalog`, `integration_connections`, `integration_events`
   - `/api/integrations/catalog` (list), `/api/integrations/connect`, `/api/integrations/webhook`
3. **Webhook Engine**
   - `integration_events` tablosuna gelen webhook logları
   - `integration_webhook_secret` doğrulaması + imza kontrolü
4. **Workflow Automation (MVP)**
   - `automation_rules` tablosu (trigger + condition + action JSON)
   - UI modalı: “When [Telehealth Risk High] AND [Region = US] THEN [Send SMS to admin]”
   - Background worker (cron) → pending integration events’i kurallarla eşleştirip `notifications` veya `integration_connections` aracılığıyla tetikler

## Teslim Kriterleri
- Marketplace sayfasında en az 5 entegrasyon kartı (Google Calendar, Zoom, Twilio, Stripe, Resend)
- OAuth/Key mock bağlantısı → status = Connected
- `/api/integrations/webhook` gelen request’i imza + secret ile doğrulayıp `integration_events` tablosuna loglar
- Workflow rule kaydedilip triggered event sonucu Twilio veya e-posta bildirimi tetikliyor (mock)

## KPI / Test
- [ ] Marketplace’de “Connect” → credentials kaydoluyor → status güncelleniyor
- [ ] Webhook POST → event tablosuna kaydoluyor → automation rule tetikleniyor
- [ ] İşlem logu `/dashboard/settings/integrations` içinde görüntüleniyor (son 10 event)

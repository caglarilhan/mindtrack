# Sosyal Hizmet Portalı

## Özet
- **Amaç:** Klinik sosyal hizmet uzmanlarına care gap verilerini, caregiver özetlerini ve kurum koordinasyonunu tek panelden sunmak.
- **Teknolojiler:** Next.js 15 (App Router) + Supabase (Postgres + RLS) + bölge bazlı AI guardrails.
- **Kapsam:** Home visit planlama, agency status, resource request takibi, care gap alarmı, caregiver snapshot ve caregiver API köprüsü.

## Veri Kaynakları
| Tablo / Kaynak | Kullanım | Not |
| --- | --- | --- |
| `social_worker_cases` | Home visit, agency, resource verisi | Migration: `20250207_0004_social_worker_cases.sql`, RLS sadece service role |
| `patient_safety_alerts` | Risk ve guardrail bağlamı | `region` filtresi ile US/EU ayrımı |
| `treatment_plans`, `therapy_sessions`, `patient_assessments`, `medications` | `computeCareGaps` için | Supabase fonksiyonları mevcut |
| `caregiver_tokens` | Revocable token deposu | Migration: `20250207_0005_caregiver_tokens.sql`, sha256 hash saklanıyor |
| `caregiver_access_logs` | Audit trail | Aynı migration, sadece service role okuyabilir |
| `/api/caregiver/summary` | Portal dışı caregiver paylaşımı | `Authorization: Bearer CAREGIVER_SHARED_TOKEN` veya DB tokenı zorunlu |

## US / EU Farkları
- **US:** CPS + Medicaid + Housing entegrasyonu, 988 kriz hattı, HIPAA guardrail.
- **EU:** Belediye & STK koordinasyonu, GDPR onam saklama, 112 kriz hattı ve EHIC/E112 formları.
- Paneldeki "Region Insights" ve öneriler dinamik olarak bu listelerden geliyor.

## Akış
1. `fetchSocialWorkerDashboard(region)` → Supabase + fallback dataset → care gap / safety enrich.
2. `/api/social-worker/dashboard?region=us|eu` → client fetch.
3. `/dashboard/social-worker` sayfası → Tabs (home, agency, resource) + care gap + caregiver dialog.
4. Her karttan hasta dosyası, caregiver API ve kriz paneline yönlendirme.
5. Caregiver API erişimi shared token ile sınırlı (`CAREGIVER_SHARED_TOKEN` env + header) ya da Supabase `caregiver_tokens` tablosundaki hashlenmiş anahtarlarla sağlanır.
6. Her erişim `caregiver_access_logs` tablosuna audit kaydı olarak yazılır.

## Test Notları
- [ ] API: `/api/social-worker/dashboard?region=us` 200 dönüyor, `careGapAlerts` dolu.
- [ ] Region toggle: US↔EU geçişinde loading state ve hata yakalanıyor.
- [ ] Caregiver dialog: snapshot seçince iletişim bilgisi ve gap listesi doğru.
- [ ] Care gap kartları ilgili modül linklerini açıyor (`/dashboard/therapy`, `/dashboard/analytics/safety`).
- [ ] `window.open(/api/caregiver/summary)` çağrısı session içinde çalışıyor.

## Açık Tasks
- Caregiver token yönetimi için panel + rotate komutları ekle.
- Access loglarını Sentry / SIEM ile entegre et.
- Bölge bazlı Twilio / e-mail şablonları (ABD: CPS form, EU: GDPR notice).

# Deploy Preflight Checklist

## 1. Smoke & E2E Tests

| Flow | Tool | Notes |
| --- | --- | --- |
| Auth + Dashboard load | Playwright `tests/auth.spec.ts` (todo) | Validate Supabase session + `/dashboard` rendering |
| DSM-5 Tanı Kaydı | Playwright `tests/diagnosis.spec.ts` | Fill kriterler → `/api/diagnosis` 200, Supabase insert |
| Therapy Otomasyon | Cypress `therapy.cy.ts` | `/dashboard/therapy` tabları, homework API yanıtı |
| Billing Cockpit | Cypress `billing.cy.ts` | Eligibility + claim forms, guardrail output |
| AI SOAP Draft | Vitest `soapDraft.test.ts` | `/api/ai/soap-draft` happy path + guardrail fail |
| Telehealth Risk | Unit test `telehealthRiskTicker.test.ts` | Transcript'ten risk event üretimi |

> **Action**: Minimum Playwright + Vitest suite kurulmalı. `package.json` test script önerisi: `playwright test && vitest run`.

## 2. Monitoring & Alerts

- **Sentry**: BACKEND + FRONTEND DSN'leri `.env` ve Vercel projelerinde dolu olmalı.
- **Supabase Log Drains**: `analytics_events`, `ai_audit_logs` için log-based alert (insert rate > threshold → Slack webhook).
- **Stripe Webhooks**: Cloudflare Worker veya Vercel Edge logu izlemek için Sentry breadcrumb ekleyin.
- **Twilio Delivery**: `sendReminderBundle` success/fail Prometheus counter (future). Şimdilik CloudWatch log ingestion planı.
- **Uptime**: BetterStack (GET `/api/health` 30s interval), telehealth node separate.

## 3. Data Backfill & Seed

1. Çalıştır: `python backend/pipelines/supabase_loader.py --table assessments --csv backend/data/patient_assessments_us.csv --region us`
2. Tekrarla: `--table safety` ve `*_eu.csv`
3. Yeni tablolar için örnek kayıtlar:
   - `ai_audit_logs`: `backend/pipelines/ai_pipeline.py` içinde `log_ai_soap` fonksiyonu.
   - `medications`: manual `psql` insert (script pending) → release öncesi 5 örnek hasta.

## 4. Access & Security

- Supabase RLS: `therapy_sessions`, `treatment_plans`, `ai_audit_logs`, `medications`, `analytics_events` tablolarına policy ekleyin (`docs/rls_plan.md` TBD).
- Admin kullanıcıları: `/api/auth/admin-setup` bir defa çalıştırın.
- Stripe Webhook: `/api/payments/webhook` → `STRIPE_WEBHOOK_SECRET` ile test edin.

## 5. Rollback Plan

- Vercel deployment preview testleri ✅ olmadan `production` promote edilmez.
- Supabase migration geri dönüşü: `supabase db remote commit` + `git revert migration`.
- Feature flag: `NEXT_PUBLIC_APP_STAGE=staging` → AI otomasyon (therapy) butonlarını pasifleştirmek için conditional logic eklendi (TODO).

---
Checklist tamamlandığında `docs/deploy_preflight_checklist.md` üzerinde tarih ve onaylayan eklenir.

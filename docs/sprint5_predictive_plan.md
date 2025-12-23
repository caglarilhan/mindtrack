# Sprint 5 – Predictive Analytics & Explainability

## Amaç
Telehealth ve klinik metrikler üzerinden risk/predictive modellerini görselleştirmek, Explainable AI şablonları hazırlamak ve deployment için veri gereksinimlerini netleştirmek.

## Modüller
1. **Predictive Dashboard Taslağı**
   - `/dashboard/analytics/predictive` sayfası
   - Kartlar: relapse risk, appointment no-show forecast, billing denial forecast
   - Placeholder chart bileşenleri (Dummy data + API hook)
2. **Data Pipeline Planı**
   - Kaynaklar: `integration_events`, `telehealth_transcripts`, `patient_assessments`
   - ETL gereksinimleri ve cron planı (`data/predictive_pipeline.md`)
   - Model seçimi: LightGBM (tabular) + SHAP
3. **Explainability Layer**
   - `docs/explainability_plan.md`: feature set + SHAP grafikleri + UI mockup
   - API taslağı: `/api/analytics/predictive?metric=relapse`

## Teslim Kriterleri
- Predictive dashboard placeholder componenti repo’daki analytics bölümüne eklendi
- Predictive data pipeline dokümantasyonu ve cron önerisi hazır
- Explainability planı (SHAP, LIME, UI) yazıldı

## KPI / Test
- [ ] `/dashboard/analytics/predictive` sayfası açılıp dummy chart’ları gösteriyor
- [ ] `docs/predictive_pipeline.md` veri kaynakları ve ETL adımlarını listeliyor
- [ ] Explainability planı (docs/explainability_plan.md) onaylandı

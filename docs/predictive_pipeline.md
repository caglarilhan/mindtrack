# Predictive Pipeline Planı

## Veri Kaynakları
- `integration_events`: Telehealth risk eventleri ve webhook tetikleri
- `telehealth_transcripts`: Risk ticker çıktıları (sentiment, severity)
- `patient_assessments`: PHQ-9, GAD-7 skorları
- `therapy_sessions`: Seans sıklığı, no-show bilgisi

## ETL & Schedule
1. `integration_events` -> günlük, S3 arşiv + Supabase view
2. `patient_assessments` -> nightly z-score normalization
3. `telehealth_transcripts` -> Whisper worker + risk label
4. Aggregation -> `predictive_features` tablosu

Cron önerisi:
- 01:00 UTC: transcription + risk pipeline
- 02:00 UTC: feature aggregation & LightGBM retrain
- 02:30 UTC: SHAP explainability compute -> S3 JSON

## Model & Explainability
- Primary model: LightGBM (tabular features), `predictive_risk_lightgbm.pkl`
- Explainability: SHAP summary + top features, `docs/explainability_plan.md`
- API: `/api/analytics/predictive?metric=relapse` (Sprint 6'da implement edilecek)

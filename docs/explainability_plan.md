# Explainability Plan (Sprint 5)

## Hedef
Predictive modellerin neden belirli risk skorları verdiğini klinisyenlere açıklamak.

## Katmanlar
1. **Feature Importance (Global)**
   - SHAP summary plot
   - Top-10 feature listesi
2. **Instance-Level Explanation**
   - SHAP waterfall chart (single patient)
   - "Hangi özellikler riski +5% yükseltti?" kartı
3. **UI Taslağı**
   - `/dashboard/analytics/predictive` içinde "Explain" butonu → modal
   - Modal içeriği: SHAP bar chart + text summary
4. **API Taslağı**
   - Endpoint: `/api/analytics/predictive/explain?patientId=...`
   - Response: `{ score: 0.55, contributions: [{ feature: 'PHQ9', value: 0.48, impact: +0.12 }] }`
5. **Veri Gereksinimi**
   - Feature store → `predictive_features`
   - Model outputs + SHAP values saklama (`predictive_explanations` tablosu)

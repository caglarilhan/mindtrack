# Sprint 3 – Form Builder + PWA

## Amaç
No-code form builder'ı versiyonlama ve template galerisiyle güçlendirmek, aynı zamanda offline/PWA deneyimi ve kiosk check-in akışlarını devreye almak.

## Modüller
1. **Form Builder V3**
   - Drag-drop alan düzenleme (grid, reorder)
   - Form versiyon geçmişi (list, publish/unpublish)
   - Template gallery (hazır şablonlar, kopyala)
   - E-imza pipeline (signature alanı kaydı + PDF render placeholder)
2. **API & DB**
   - Migration: `form_template_versions`, `form_template_gallery`, `form_template_reviews`
   - Endpoints: `/api/forms/gallery`, `/api/forms/templates/[id]/publish`, `/api/forms/templates/[id]/versions`
3. **PWA + Offline**
   - `next-pwa` konfigürasyonu, manifest güncellemesi
   - Offline form cache (IndexedDB + service worker sync)
   - Install prompt & push notifications (web push placeholder)
4. **Kiosk / Mobile Check-in**
   - `/portal/kiosk` sayfası (hasta kodu + form doldurma)
   - Offline queue → online olunca `/api/forms/submissions`'a sync

## Teslim Kriterleri
- Form builder UI'de "Versiyonlar" tabı, publish butonu, template import modalı
- Gallery endpoint → UI listesi → "Klinik kütüphanene ekle" akışı
- Service worker offline modunda portal/kiosk açılabiliyor, form taslakları saklanıyor
- PWA install banner tetikleniyor, push permission isteği mock'u
- Kiosk sayfası kod girince form listesi + imza destekli submission

## KPI / Test
- [ ] Form builder ile yeni versiyon yarat → publish → gallery'e ekle → başka klinikte kopyala
- [ ] Offline modda form doldur → bağlantı gelince submission API'ye gider
- [ ] PWA manifest Lighthouse PWA skoru ≥ 90
- [ ] Kiosk sayfası ile check-in formu + imza kaydı → Supabase `form_submissions`

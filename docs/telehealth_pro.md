# Telehealth Pro Özeti

## Modüller
1. **Branding & Waiting Room**
   - Supabase `telehealth_branding` tablosu (logo, accent, mesaj, help links, caregiver ayarı).
   - API: `/api/telehealth/branding` → GET/POST (RBAC: settings:communications:read/write).
   - Telehealth video UI artık brand kartını gösteriyor (logo + aksan rengi + caregiver durumu).
2. **Transkript & Risk Tabloları**
   - `telehealth_transcripts`, `telehealth_risk_events` → transcript snippet + risk ticker verisi.
   - Backend worker (TODO) transcription & risk yazacak.
3. **Telehealth Pro UI**
   - `telehealth-video-platform.tsx` → bekleme alanı kartı, brand accent badge’leri.
   - Region toggle ile entegre.
4. **Caregiver Token Bağı**
   - Branding ayarında `allowCaregiverJoin` ve default region; davet modalları bu bilgiyi kullanacak (devam eden görev).

## Yapılacaklar
- Waiting room brand paneli (ayar UI) → communications settings altına eklenecek.
- Recording/transcript worker → `telehealth_transcripts` tablosuna yazacak.
- Risk ticker UI → `telehealth_risk_events` feed.

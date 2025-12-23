# Social Worker Flows

## 1. My Cases
- Giriş: `role = social_worker`
- Liste: atandığı hastalar (initials + age range + risk flag)
- Aksiyonlar:
  - "View tasks" → care task board filtresi (sadece bu hasta)
  - "Add handoff note" → clinician ile mesaj / görev bağlantısı

## 2. Tasks
- Kaynak: `care_tasks` tablosu
- Alanlar: `domain`, `risk_level`, `status`, `due_date`, `owner_id`
- Filtreler: `domain`, `risk_level`, `status`, `region`

## 3. Handoff
- Klinik ekip üyeleri arasında: örn. therapist → social_worker
- Metin alanı: kısa özet + yapılacak aksiyon + hedef tarih
- Otomatik link: istenirse referral olarak dış kuruma dönüştürülebilir (Referral modülü ile entegrasyon sonraki sprint)

## 4. US / EU Farkları
- US: Medicaid/SSI, housing programs, school IEP/504 referansları
- EU: sosyal devlet hizmetleri, belediye destekleri, NGO yönlendirmeleri
- UI seviyesinde sadece açıklama/etiket düzeyinde ayrım; gerçek entegrasyon ileriki sürümlerde eklenecek.

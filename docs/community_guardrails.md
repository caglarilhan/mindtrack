# Community Guardrails (Referral & Discussion)

## Hedef
Klinisyen community ve referral akışında hasta gizliliğini (HIPAA / GDPR) korumak.

## Temel İlkeler
- Hasta isimleri, doğrudan tanımlayıcı bilgiler community board'da gösterilmez.
- Referral notlarında minimum gerekli bilgi ("minimum necessary") prensibi.
- US/EU için farklı flag: bazı ülkelerde açık case tartışması devre dışı bırakılabilir.

## Teknik Notlar
- `community_posts` (ileriki sprint) için `clinic_id` + `created_by` RLS kuralı.
- De-id pipeline: isim/telefon/e-posta gibi alanları maskeden helper fonksiyon (gelecek sprint'te).

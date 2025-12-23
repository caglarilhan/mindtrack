# Referral Schema Taslağı

## Tablolar

### `referral_contacts`
- `id` (uuid, pk)
- `clinic_id` (uuid, fk clinics)
- `name` (text)
- `specialty` (text)
- `region` (text, 'us' | 'eu' | 'other')
- `country` (text)
- `city` (text)
- `email` (text)
- `phone` (text)
- `accepts_insurance` (boolean)
- `notes` (text)
- `created_at`, `updated_at`

### `referrals`
- `id` (uuid, pk)
- `from_clinic_id` (uuid)
- `to_contact_id` (uuid, fk referral_contacts)
- `patient_id` (uuid, optional / hashed id for de-id)
- `status` (text: 'pending' | 'accepted' | 'declined' | 'closed')
- `reason` (text)
- `priority` (text: 'low' | 'normal' | 'high')
- `region` (text, 'us' | 'eu')
- `created_by` (uuid, user)
- `created_at`, `updated_at`

## API Taslakları
- `GET /api/referrals` → listeleme (filter by status, region)
- `POST /api/referrals` → yeni referral oluşturma
- `PATCH /api/referrals/:id` → status update
- `GET /api/referrals/stats` → basit metrikler (by status, by region)

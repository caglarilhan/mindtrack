# Sprint 7 – Social Worker Collaboration & Care Team

## Amaç
Psikolog / psikiyatrist ile sosyal hizmet uzmanları arasında care team akışını kurmak; sosyal ihtiyaç görevlerini (barınma, iş, okul, aile) görünür ve izlenebilir hale getirmek.

## Modüller
1. **Social Worker Dashboard (Portal)**
   - Route: `/dashboard/social-worker`
   - Sekmeler: `My Cases`, `Tasks`, `Hand-offs`
   - Kartlar: patient initials + risk flag + açık görev sayısı
2. **Care Team & Handoff**
   - Her hasta için care team üyeleri (psychiatrist, therapist, social worker, PCP)
   - Handoff notları: `from_role`, `to_role`, `status` (open/in-progress/done)
3. **Tasks & Prioritization**
   - `care_tasks` tablosu: domain (housing, employment, education, finances, legal), `risk_level`, `due_date`
   - Telehealth risk + assessment skorlarından gelen sinyallere göre öncelik alanı
4. **RBAC & RLS**
   - Yeni rol: `social_worker`
   - İzinler: `social:cases:read`, `social:tasks:write`
   - RLS: yalnızca atandığı hastaların özetini görebilir; tam SOAP değil, risk/goal/summary alanları

## Teslim Kriterleri
- `/dashboard/social-worker` sayfası; dummy Supabase-ready verilerle case & task board gösteriyor
- Supabase şema taslağı: `supabase/social-worker-schema.sql` (care_tasks + care_handoffs)
- RBAC güncellemesi (yeni rol + izinler) ve server helper (`src/lib/server/social-worker.ts`) hazır

## KPI / Test
- [ ] Social worker rolü ile login olduğunda sadece atandığı case'ler listeleniyor (mock veya RLS taslağı)
- [ ] Task board’da domain & risk seviyesine göre filtreleme çalışıyor (UI)
- [ ] Handoff kartları care team içerisinde doğru rollerle görünüyor (placeholder)

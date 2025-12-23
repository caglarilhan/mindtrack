-- Audit logs
create table if not exists public.audit_logs (
  id uuid primary key default gen_random_uuid(),
  action text not null,
  user_id uuid,
  patient_id uuid,
  appointment_id uuid,
  ip text,
  user_agent text,
  context jsonb not null default '{}',
  created_at timestamptz not null default now()
);

-- Clinic members role (if not exists)
alter table if exists public.clinic_members add column if not exists role text;




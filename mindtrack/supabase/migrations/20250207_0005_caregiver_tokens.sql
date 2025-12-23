-- Caregiver API token management and audit tables
create table if not exists public.caregiver_tokens (
  id uuid primary key default gen_random_uuid(),
  label text not null,
  token_hash text not null unique,
  allowed_regions text[] not null default array['us','eu'],
  active boolean not null default true,
  expires_at timestamptz,
  last_used_at timestamptz,
  metadata jsonb,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.caregiver_access_logs (
  id uuid primary key default gen_random_uuid(),
  token_id uuid references public.caregiver_tokens(id),
  token_label text,
  patient_id text,
  region text not null,
  status text not null check (status in ('allowed','denied')),
  reason text,
  ip_address text,
  user_agent text,
  created_at timestamptz not null default timezone('utc', now())
);

alter table public.caregiver_tokens enable row level security;
alter table public.caregiver_access_logs enable row level security;

create policy if not exists "caregiver-tokens-service-role" on public.caregiver_tokens
  using (auth.role() = 'service_role')
  with check (auth.role() = 'service_role');

create policy if not exists "caregiver-access-logs-service-role" on public.caregiver_access_logs
  using (auth.role() = 'service_role')
  with check (auth.role() = 'service_role');

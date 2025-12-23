-- Social worker cases table to back social worker dashboard (US/EU)
create table if not exists public.social_worker_cases (
  id uuid primary key default gen_random_uuid(),
  case_id text not null,
  patient_id uuid,
  patient_name text,
  region text not null check (region in ('us','eu')),
  priority text not null check (priority in ('high','medium','low')),
  next_visit_at timestamptz,
  visit_focus text,
  address text,
  caregiver_contact text,
  caregiver_channel text check (caregiver_channel in ('phone','email','portal')),
  agency_partner text,
  agency_contact text,
  agency_status text check (agency_status in ('pending','in-progress','completed')),
  agency_category text check (agency_category in ('housing','cps','immigration','benefit')),
  resource_need text,
  resource_amount text,
  resource_due_at timestamptz,
  resource_status text check (resource_status in ('pending','approved','denied')),
  funding_source text,
  inserted_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now()),
  constraint social_worker_cases_case_id_unique unique(case_id)
);

alter table public.social_worker_cases enable row level security;

create policy if not exists "social-worker-cases-service-role" on public.social_worker_cases
  using (auth.role() = 'service_role') with check (auth.role() = 'service_role');

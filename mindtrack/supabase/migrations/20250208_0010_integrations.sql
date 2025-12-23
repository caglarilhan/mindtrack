create table if not exists public.integrations_catalog (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  name text not null,
  description text,
  category text not null default 'General',
  logo_url text,
  auth_type text not null default 'api_key' check (auth_type in ('api_key','oauth','webhook')),
  docs_url text,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.integration_connections (
  id uuid primary key default gen_random_uuid(),
  clinic_id uuid not null references public.clinics(id) on delete cascade,
  integration_id uuid not null references public.integrations_catalog(id) on delete cascade,
  status text not null default 'disconnected' check (status in ('disconnected','connected','error','needs_action')),
  settings jsonb,
  credentials jsonb,
  last_synced_at timestamptz,
  health_status text default 'unknown',
  error_message text,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now()),
  unique (clinic_id, integration_id)
);

create table if not exists public.integration_events (
  id uuid primary key default gen_random_uuid(),
  integration_id uuid references public.integrations_catalog(id) on delete set null,
  clinic_id uuid references public.clinics(id) on delete set null,
  event_type text not null,
  payload jsonb not null,
  status text not null default 'queued' check (status in ('queued','processed','failed')),
  received_at timestamptz not null default timezone('utc', now()),
  processed_at timestamptz,
  error text
);

create index if not exists idx_integration_events_integration_id on public.integration_events (integration_id);
create index if not exists idx_integration_events_status on public.integration_events (status);

create table if not exists public.automation_rules (
  id uuid primary key default gen_random_uuid(),
  clinic_id uuid not null references public.clinics(id) on delete cascade,
  name text not null,
  trigger jsonb not null,
  conditions jsonb,
  actions jsonb not null,
  enabled boolean not null default true,
  last_run_at timestamptz,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

alter table public.integrations_catalog enable row level security;
alter table public.integration_connections enable row level security;
alter table public.integration_events enable row level security;
alter table public.automation_rules enable row level security;

create policy if not exists "integrations-catalog-read" on public.integrations_catalog
  for select using (true);

create policy if not exists "integration-connections-service" on public.integration_connections
  for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');

create policy if not exists "integration-events-service" on public.integration_events
  for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');

create policy if not exists "automation-rules-service" on public.automation_rules
  for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');

comment on table public.integrations_catalog is 'Marketplace data for third-party integrations';
comment on table public.integration_connections is 'Clinic-level integration credential store';
comment on table public.integration_events is 'Webhook and sync event logs';
comment on table public.automation_rules is 'Workflow automation definitions';

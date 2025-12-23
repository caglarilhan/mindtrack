-- Clearinghouse integration tables
create table if not exists public.payer_connections (
  id uuid primary key default gen_random_uuid(),
  payer_name text not null,
  payer_id text not null,
  clearinghouse text not null,
  api_endpoint text,
  credentials jsonb,
  status text not null default 'inactive' check (status in ('inactive','active','error')),
  last_sync_at timestamptz,
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.claims_queue (
  id uuid primary key default gen_random_uuid(),
  claim_number text not null,
  patient_id uuid not null,
  provider_id uuid not null,
  payer_connection_id uuid references public.payer_connections(id) on delete set null,
  payload jsonb not null,
  status text not null default 'queued' check (status in ('queued','submitted','acknowledged','denied','paid','error')),
  acknowledgements jsonb,
  submitted_at timestamptz,
  response_at timestamptz,
  region text not null default 'us' check (region in ('us','eu')),
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.era_events (
  id uuid primary key default gen_random_uuid(),
  claim_id uuid references public.claims_queue(id) on delete cascade,
  raw_payload jsonb,
  amount numeric,
  code text,
  description text,
  posted_at timestamptz not null default timezone('utc', now())
);

alter table public.payer_connections enable row level security;
alter table public.claims_queue enable row level security;
alter table public.era_events enable row level security;

create policy if not exists "payer-connections-service" on public.payer_connections
  for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');

create policy if not exists "claims-queue-service" on public.claims_queue
  for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');

create policy if not exists "era-events-service" on public.era_events
  for all using (auth.role() = 'service_role') with check (auth.role() = 'service_role');

comment on table public.payer_connections is 'Clearinghouse payer credentials and endpoints';
comment on table public.claims_queue is '837/270 submission queue with statuses';
comment on table public.era_events is '835/ERA events mapped to claims';

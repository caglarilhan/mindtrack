-- Telehealth Pro branding + transcript tables
create table if not exists public.telehealth_branding (
  id uuid primary key default gen_random_uuid(),
  clinic_id uuid not null,
  logo_url text,
  accent_color text default '#2563eb',
  waiting_room_message text,
  help_links jsonb,
  allow_caregiver_join boolean default true,
  default_region text default 'us' check (default_region in ('us','eu')),
  updated_by uuid,
  updated_at timestamptz not null default timezone('utc', now()),
  constraint telehealth_branding_clinic_unique unique (clinic_id)
);

create table if not exists public.telehealth_transcripts (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references video_sessions(id) on delete cascade,
  speaker text not null check (speaker in ('patient','provider','caregiver','system')),
  snippet text not null,
  start_time numeric,
  end_time numeric,
  risk_tags jsonb,
  sentiment_score numeric,
  created_at timestamptz not null default timezone('utc', now())
);

create table if not exists public.telehealth_risk_events (
  id uuid primary key default gen_random_uuid(),
  session_id uuid references video_sessions(id) on delete cascade,
  severity text not null check (severity in ('low','medium','high','critical')),
  category text not null,
  message text not null,
  transcript_excerpt text,
  recommended_action text,
  region text not null default 'us' check (region in ('us','eu')),
  created_at timestamptz not null default timezone('utc', now())
);

alter table public.telehealth_branding enable row level security;
alter table public.telehealth_transcripts enable row level security;
alter table public.telehealth_risk_events enable row level security;

create policy if not exists "telehealth-branding-ro" on public.telehealth_branding
  for select using (true);
create policy if not exists "telehealth-branding-rw" on public.telehealth_branding
  for insert with check (true);
create policy if not exists "telehealth-branding-update" on public.telehealth_branding
  for update using (true);

create policy if not exists "telehealth-transcripts-ro" on public.telehealth_transcripts
  for select using (true);
create policy if not exists "telehealth-transcripts-insert" on public.telehealth_transcripts
  for insert with check (true);

create policy if not exists "telehealth-risk-events-ro" on public.telehealth_risk_events
  for select using (true);
create policy if not exists "telehealth-risk-events-insert" on public.telehealth_risk_events
  for insert with check (true);

comment on table public.telehealth_branding is 'Telehealth Pro waiting room branding and caregiver settings';
comment on table public.telehealth_transcripts is 'Stores transcript snippets + risk metadata';
comment on table public.telehealth_risk_events is 'Risk ticker events derived from transcripts';

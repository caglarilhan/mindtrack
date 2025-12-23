create table if not exists public.delivery_queue (
  id uuid primary key default gen_random_uuid(),
  channel text not null, -- email | sms
  payload jsonb not null,
  run_at timestamptz not null,
  attempts int not null default 0,
  max_attempts int not null default 5,
  locked_at timestamptz,
  locked_by text,
  created_at timestamptz not null default now()
);

create index if not exists idx_delivery_queue_run_at on public.delivery_queue (run_at);





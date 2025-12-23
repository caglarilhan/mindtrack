create table if not exists public.delivery_logs (
  id uuid primary key default gen_random_uuid(),
  channel text not null, -- email | sms
  provider text not null,
  to_address text not null,
  subject text,
  body text,
  status text not null, -- sent | failed
  error text,
  context jsonb not null default '{}',
  created_at timestamptz not null default now()
);





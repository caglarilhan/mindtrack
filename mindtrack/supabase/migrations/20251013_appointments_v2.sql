alter table if exists public.appointments add column if not exists status text default 'scheduled';
alter table if exists public.appointments add column if not exists type text default 'consult';
alter table if exists public.appointments add column if not exists location text;
alter table if exists public.appointments add column if not exists recurrence jsonb; -- e.g., {"freq":"WEEKLY","count":6}





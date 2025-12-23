-- Appointments table
create table if not exists public.appointments (
  id uuid primary key default gen_random_uuid(),
  patient_id uuid not null,
  start_at timestamptz not null,
  telehealth_link text,
  created_at timestamptz not null default now()
);

-- Appointment settings
create table if not exists public.appointment_settings (
  appointment_id uuid primary key references public.appointments(id) on delete cascade,
  settings jsonb not null default '{}',
  updated_at timestamptz not null default now()
);

-- Patient preferences
create table if not exists public.patient_preferences (
  patient_id uuid primary key,
  preferences jsonb not null default '{}',
  updated_at timestamptz not null default now()
);

-- Patient anamnesis
create table if not exists public.patient_anamnesis (
  patient_id uuid primary key,
  payload jsonb not null,
  mode text not null default 'record',
  updated_at timestamptz not null default now()
);



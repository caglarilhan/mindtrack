-- Group / Couples Therapy + Supervision tables

create table if not exists public.group_sessions (
    id uuid primary key default gen_random_uuid(),
    session_type text not null check (session_type in ('group','family','couples')),
    facilitator_id uuid not null,
    session_date timestamptz not null,
    modality text not null default 'in-person',
    topic text,
    notes text,
    created_at timestamptz not null default now()
);

create table if not exists public.group_session_participants (
    session_id uuid references public.group_sessions(id) on delete cascade,
    patient_id uuid not null,
    role text default 'participant',
    status text default 'active',
    primary key (session_id, patient_id)
);

create table if not exists public.supervision_notes (
    id uuid primary key default gen_random_uuid(),
    patient_id uuid not null,
    therapist_id uuid not null,
    note text not null,
    created_at timestamptz not null default now()
);

create index if not exists idx_group_sessions_date on public.group_sessions(session_date);
create index if not exists idx_supervision_notes_patient on public.supervision_notes(patient_id);

-- Enable required extensions
create extension if not exists "pgcrypto";

-- Therapy sessions captured directly from the in-app scheduler
create table if not exists public.therapy_sessions (
    id uuid primary key default gen_random_uuid(),
    patient_id uuid not null,
    therapist_id uuid not null,
    session_date timestamptz not null,
    session_type text not null check (session_type in ('individual','group','family','couples','initial','followup')),
    duration integer not null check (duration > 0),
    status text not null check (status in ('scheduled','completed','cancelled','no-show')),
    goals text[] default array[]::text[],
    techniques text[] default array[]::text[],
    homework text,
    notes text,
    progress_rating numeric,
    next_session_date timestamptz,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_therapy_sessions_patient on public.therapy_sessions(patient_id);
create index if not exists idx_therapy_sessions_therapist on public.therapy_sessions(therapist_id);

-- Treatment plan repository backing AI autoplan suggestions
create table if not exists public.treatment_plans (
    id uuid primary key default gen_random_uuid(),
    patient_id uuid not null,
    therapist_id uuid not null,
    diagnosis_code text not null,
    goals text[] default array[]::text[],
    interventions text[] default array[]::text[],
    estimated_sessions integer,
    start_date date not null,
    end_date date,
    status text not null default 'active' check (status in ('active','completed','paused')),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_treatment_plans_patient on public.treatment_plans(patient_id);

-- AI audit log for explainability & dispute workflow
create table if not exists public.ai_audit_logs (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null,
    patient_id uuid,
    ai_type text not null,
    input_data jsonb not null,
    output_data jsonb not null,
    explanation jsonb,
    guardrail_results jsonb,
    region text not null default 'us' check (region in ('us','eu')),
    disputed boolean not null default false,
    dispute_reason text,
    dispute_resolved boolean not null default false,
    created_at timestamptz not null default now()
);

create index if not exists idx_ai_audit_logs_user on public.ai_audit_logs(user_id);
create index if not exists idx_ai_audit_logs_patient on public.ai_audit_logs(patient_id);
create index if not exists idx_ai_audit_logs_type on public.ai_audit_logs(ai_type);

-- Analytics lake style event bus
create table if not exists public.analytics_events (
    id uuid primary key default gen_random_uuid(),
    event_type text not null,
    user_id uuid,
    patient_id uuid,
    metadata jsonb not null,
    region text check (region in ('us','eu')),
    created_at timestamptz not null default now()
);

create index if not exists idx_analytics_events_type on public.analytics_events(event_type);
create index if not exists idx_analytics_events_patient on public.analytics_events(patient_id);

-- Medication management + side-effects
create table if not exists public.medications (
    id uuid primary key default gen_random_uuid(),
    patient_id uuid not null,
    medication_name text not null,
    dosage text not null,
    frequency text not null,
    start_date date not null,
    end_date date,
    prescriber_id uuid not null,
    status text not null default 'active' check (status in ('active','discontinued','completed')),
    region text not null default 'us' check (region in ('us','eu')),
    adherence numeric,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_medications_patient on public.medications(patient_id);

create table if not exists public.medication_side_effects (
    id uuid primary key default gen_random_uuid(),
    medication_id uuid not null references public.medications(id) on delete cascade,
    reported_at timestamptz not null,
    severity text not null check (severity in ('mild','moderate','severe')),
    description text not null,
    action_taken text,
    created_at timestamptz not null default now()
);

create index if not exists idx_side_effects_medication on public.medication_side_effects(medication_id);

-- Custom guardrail policy editor
create table if not exists public.custom_guardrail_rules (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null,
    name text not null,
    pattern text not null,
    severity text not null check (severity in ('low','medium','high','critical')),
    category text not null,
    message text not null,
    recommendation text not null,
    region text not null default 'both' check (region in ('us','eu','both')),
    active boolean not null default true,
    created_at timestamptz not null default now()
);

create index if not exists idx_guardrail_rules_user on public.custom_guardrail_rules(user_id);

-- Crisis escalation feed
create table if not exists public.crisis_events (
    id uuid primary key default gen_random_uuid(),
    patient_id uuid not null,
    severity text not null check (severity in ('low','medium','high','critical')),
    category text not null,
    reported_at timestamptz not null,
    reported_by uuid not null,
    description text not null,
    region text not null default 'us' check (region in ('us','eu')),
    escalated boolean not null default false,
    escalation_method text,
    escalation_timestamp timestamptz,
    created_at timestamptz not null default now()
);

create index if not exists idx_crisis_events_patient on public.crisis_events(patient_id);

-- Utility trigger to keep updated_at fresh
create or replace function public.set_updated_at()
returns trigger as $$
begin
  new.updated_at = now();
  return new;
end;
$$ language plpgsql;

create trigger trg_therapy_sessions_updated
before update on public.therapy_sessions
for each row execute procedure public.set_updated_at();

create trigger trg_treatment_plans_updated
before update on public.treatment_plans
for each row execute procedure public.set_updated_at();

create trigger trg_medications_updated
before update on public.medications
for each row execute procedure public.set_updated_at();

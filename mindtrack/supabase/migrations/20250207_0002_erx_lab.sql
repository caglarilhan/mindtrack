-- e-Prescription & Laboratory Protocol tables

create table if not exists public.medication_orders (
    id uuid primary key default gen_random_uuid(),
    patient_id uuid not null,
    medication_name text not null,
    dosage text not null,
    route text,
    quantity integer,
    frequency text,
    pharmacy_name text,
    pharmacy_npi text,
    status text not null default 'pending' check (status in ('pending','sent','failed','fulfilled')),
    external_reference text,
    response_message text,
    region text not null default 'us' check (region in ('us','eu')),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_medication_orders_patient on public.medication_orders(patient_id);

create table if not exists public.lab_orders (
    id uuid primary key default gen_random_uuid(),
    patient_id uuid not null,
    test_name text not null,
    protocol text not null,
    due_date date not null,
    status text not null default 'pending' check (status in ('pending','overdue','completed')),
    last_result jsonb,
    region text not null default 'us' check (region in ('us','eu')),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_lab_orders_patient on public.lab_orders(patient_id);

create trigger trg_medication_orders_updated
before update on public.medication_orders
for each row execute procedure public.set_updated_at();

create trigger trg_lab_orders_updated
before update on public.lab_orders
for each row execute procedure public.set_updated_at();

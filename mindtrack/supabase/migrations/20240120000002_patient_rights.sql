-- Patient Rights Implementation
-- HIPAA Requirement: §164.524 - Access of Individuals

CREATE TABLE IF NOT EXISTS public.patient_access_requests (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id uuid NOT NULL REFERENCES public.clients(id) ON DELETE CASCADE,
    request_type text NOT NULL CHECK (request_type IN ('access', 'amend', 'delete', 'restrict')),
    record_id uuid, -- For amendment requests
    record_type text, -- For amendment requests
    requested_data text[], -- For access requests
    amendment_request text, -- For amendment requests
    deletion_reason text, -- For deletion requests
    status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'completed')),
    requested_at timestamptz NOT NULL DEFAULT now(),
    reviewed_at timestamptz,
    reviewed_by uuid REFERENCES public.profiles(id),
    completed_at timestamptz,
    completed_by uuid REFERENCES public.profiles(id),
    response text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_patient_access_requests_patient_id ON public.patient_access_requests(patient_id);
CREATE INDEX IF NOT EXISTS idx_patient_access_requests_status ON public.patient_access_requests(status);
CREATE INDEX IF NOT EXISTS idx_patient_access_requests_type ON public.patient_access_requests(request_type);
CREATE INDEX IF NOT EXISTS idx_patient_access_requests_created_at ON public.patient_access_requests(created_at DESC);

-- RLS for patient access requests
ALTER TABLE public.patient_access_requests ENABLE ROW LEVEL SECURITY;

-- Policy: Patients can view their own requests
CREATE POLICY "Patients can view own access requests"
    ON public.patient_access_requests
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.clients
            WHERE id = patient_access_requests.patient_id
            AND EXISTS (
                SELECT 1 FROM public.profiles
                WHERE id = auth.uid() AND (id = patient_access_requests.patient_id OR role IN ('therapist', 'admin'))
            )
        )
    );

-- Policy: Patients can create their own requests
CREATE POLICY "Patients can create own access requests"
    ON public.patient_access_requests
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.clients
            WHERE id = patient_access_requests.patient_id
            AND EXISTS (
                SELECT 1 FROM public.profiles
                WHERE id = auth.uid() AND (id = patient_access_requests.patient_id OR role IN ('therapist', 'admin'))
            )
        )
    );

-- Add deleted_at columns for soft deletion
DO $$
BEGIN
    -- Add deleted_at to notes if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'notes' AND column_name = 'deleted_at'
    ) THEN
        ALTER TABLE public.notes ADD COLUMN deleted_at timestamptz;
        CREATE INDEX IF NOT EXISTS idx_notes_deleted_at ON public.notes(deleted_at);
    END IF;

    -- Add deleted_at to clients if not exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'clients' AND column_name = 'deleted_at'
    ) THEN
        ALTER TABLE public.clients ADD COLUMN deleted_at timestamptz;
        CREATE INDEX IF NOT EXISTS idx_clients_deleted_at ON public.clients(deleted_at);
    END IF;
END $$;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_patient_access_requests_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_patient_access_requests_updated_at
    BEFORE UPDATE ON public.patient_access_requests
    FOR EACH ROW
    EXECUTE FUNCTION update_patient_access_requests_updated_at();






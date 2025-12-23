-- Consent Management System
-- HIPAA Requirement: §164.508 - Uses and Disclosures for Which Authorization is Required

CREATE TABLE IF NOT EXISTS public.consent_forms (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_id uuid NOT NULL REFERENCES public.clients(id) ON DELETE CASCADE,
    consent_type text NOT NULL CHECK (consent_type IN (
        'treatment', 'payment', 'healthcare_operations', 
        'marketing', 'research', 'psychotherapy_notes', 'other'
    )),
    description text NOT NULL,
    status text NOT NULL DEFAULT 'pending' CHECK (status IN (
        'pending', 'active', 'expired', 'withdrawn', 'revoked'
    )),
    signed_at timestamptz,
    expires_at timestamptz,
    withdrawn_at timestamptz,
    revoked_at timestamptz,
    revoked_by uuid REFERENCES public.profiles(id),
    signature_data text, -- Encrypted signature image (base64)
    signature_name text,
    signature_ip inet,
    signature_user_agent text,
    withdrawal_reason text,
    revocation_reason text,
    metadata jsonb,
    created_by uuid NOT NULL REFERENCES public.profiles(id),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_consent_forms_patient_id ON public.consent_forms(patient_id);
CREATE INDEX IF NOT EXISTS idx_consent_forms_status ON public.consent_forms(status);
CREATE INDEX IF NOT EXISTS idx_consent_forms_type ON public.consent_forms(consent_type);
CREATE INDEX IF NOT EXISTS idx_consent_forms_expires_at ON public.consent_forms(expires_at);
CREATE INDEX IF NOT EXISTS idx_consent_forms_created_at ON public.consent_forms(created_at DESC);

-- RLS for consent forms
ALTER TABLE public.consent_forms ENABLE ROW LEVEL SECURITY;

-- Policy: Patients can view their own consents
CREATE POLICY "Patients can view own consents"
    ON public.consent_forms
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.clients
            WHERE id = consent_forms.patient_id
            AND EXISTS (
                SELECT 1 FROM public.profiles
                WHERE id = auth.uid() AND (id = consent_forms.patient_id OR role IN ('therapist', 'admin'))
            )
        )
    );

-- Policy: Therapists can create consents for their patients
CREATE POLICY "Therapists can create consents"
    ON public.consent_forms
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role IN ('therapist', 'admin')
        )
    );

-- Policy: Patients can update their own consents (sign, withdraw)
CREATE POLICY "Patients can update own consents"
    ON public.consent_forms
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.clients
            WHERE id = consent_forms.patient_id
            AND EXISTS (
                SELECT 1 FROM public.profiles
                WHERE id = auth.uid() AND (
                    id = consent_forms.patient_id OR 
                    role IN ('therapist', 'admin')
                )
            )
        )
    );

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_consent_forms_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_consent_forms_updated_at
    BEFORE UPDATE ON public.consent_forms
    FOR EACH ROW
    EXECUTE FUNCTION update_consent_forms_updated_at();

-- Function to auto-expire consents
CREATE OR REPLACE FUNCTION auto_expire_consents()
RETURNS void AS $$
BEGIN
    UPDATE public.consent_forms
    SET status = 'expired'
    WHERE status = 'active'
    AND expires_at IS NOT NULL
    AND expires_at < now();
END;
$$ LANGUAGE plpgsql;

-- Schedule auto-expiration (run daily via cron or scheduled job)
-- This would typically be called by a cron job or scheduled task






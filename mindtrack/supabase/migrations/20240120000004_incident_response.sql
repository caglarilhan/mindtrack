-- Security Incident Response System
-- HIPAA Requirement: §164.308(a)(6) - Security Incident Procedures

CREATE TABLE IF NOT EXISTS public.security_incidents (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_type text NOT NULL CHECK (incident_type IN (
        'unauthorized_access', 'data_breach', 'malware', 'phishing',
        'ddos', 'insider_threat', 'physical_security', 'other'
    )),
    severity text NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    title text NOT NULL,
    description text NOT NULL,
    detected_at timestamptz NOT NULL DEFAULT now(),
    detected_by uuid NOT NULL REFERENCES public.profiles(id),
    assigned_to uuid REFERENCES public.profiles(id),
    assigned_at timestamptz,
    status text NOT NULL DEFAULT 'detected' CHECK (status IN (
        'detected', 'assigned', 'investigating', 'contained', 'resolved', 'closed'
    )),
    affected_systems text[],
    affected_users uuid[],
    impact text,
    root_cause text,
    remediation text,
    lessons_learned text,
    resolved_at timestamptz,
    closed_at timestamptz,
    escalation_reason text,
    escalated_at timestamptz,
    escalated_by uuid REFERENCES public.profiles(id),
    status_notes text,
    metadata jsonb,
    updated_by uuid REFERENCES public.profiles(id),
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_security_incidents_status ON public.security_incidents(status);
CREATE INDEX IF NOT EXISTS idx_security_incidents_severity ON public.security_incidents(severity);
CREATE INDEX IF NOT EXISTS idx_security_incidents_type ON public.security_incidents(incident_type);
CREATE INDEX IF NOT EXISTS idx_security_incidents_assigned_to ON public.security_incidents(assigned_to);
CREATE INDEX IF NOT EXISTS idx_security_incidents_detected_at ON public.security_incidents(detected_at DESC);

-- Incident Response Actions Table
CREATE TABLE IF NOT EXISTS public.incident_responses (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    incident_id uuid NOT NULL REFERENCES public.security_incidents(id) ON DELETE CASCADE,
    response_actions text[] NOT NULL,
    containment_actions text[] NOT NULL,
    eradication_actions text[] NOT NULL,
    recovery_actions text[] NOT NULL,
    post_incident_actions text[] NOT NULL,
    created_by uuid NOT NULL REFERENCES public.profiles(id),
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_incident_responses_incident_id ON public.incident_responses(incident_id);

-- RLS for security incidents (admin and assigned users only)
ALTER TABLE public.security_incidents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Admins can view all incidents"
    ON public.security_incidents
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Assigned users can view assigned incidents"
    ON public.security_incidents
    FOR SELECT
    USING (
        assigned_to = auth.uid() OR
        detected_by = auth.uid()
    );

CREATE POLICY "Admins can create incidents"
    ON public.security_incidents
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role IN ('admin', 'therapist')
        )
    );

CREATE POLICY "Admins and assigned users can update incidents"
    ON public.security_incidents
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND (
                role = 'admin' OR
                assigned_to = auth.uid() OR
                detected_by = auth.uid()
            )
        )
    );

-- RLS for incident responses
ALTER TABLE public.incident_responses ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view responses for accessible incidents"
    ON public.incident_responses
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.security_incidents
            WHERE id = incident_responses.incident_id
            AND (
                EXISTS (
                    SELECT 1 FROM public.profiles
                    WHERE id = auth.uid() AND role = 'admin'
                ) OR
                assigned_to = auth.uid() OR
                detected_by = auth.uid()
            )
        )
    );

CREATE POLICY "Admins and assigned users can create responses"
    ON public.incident_responses
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.security_incidents
            WHERE id = incident_responses.incident_id
            AND (
                EXISTS (
                    SELECT 1 FROM public.profiles
                    WHERE id = auth.uid() AND role = 'admin'
                ) OR
                assigned_to = auth.uid() OR
                detected_by = auth.uid()
            )
        )
    );

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_security_incidents_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_security_incidents_updated_at
    BEFORE UPDATE ON public.security_incidents
    FOR EACH ROW
    EXECUTE FUNCTION update_security_incidents_updated_at();






-- Breach Events Table
-- HIPAA Requirement: §164.404 - Notification to Individuals

CREATE TABLE IF NOT EXISTS public.breach_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    breach_type text NOT NULL CHECK (breach_type IN (
        'unauthorized_access', 'data_exfiltration', 'data_loss', 
        'system_compromise', 'other'
    )),
    severity text NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    description text NOT NULL,
    affected_users uuid[] NOT NULL,
    affected_records integer NOT NULL DEFAULT 0,
    detected_at timestamptz NOT NULL DEFAULT now(),
    reported_at timestamptz,
    resolved_at timestamptz,
    status text NOT NULL DEFAULT 'detected' CHECK (status IN (
        'detected', 'assessed', 'notified', 'resolved'
    )),
    risk_score integer NOT NULL DEFAULT 0 CHECK (risk_score >= 0 AND risk_score <= 100),
    notified_at timestamptz,
    notified_count integer DEFAULT 0,
    hhs_notified boolean DEFAULT false,
    hhs_notified_at timestamptz,
    media_notified boolean DEFAULT false,
    media_notified_at timestamptz,
    remediation_actions text,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_breach_events_status ON public.breach_events(status);
CREATE INDEX IF NOT EXISTS idx_breach_events_severity ON public.breach_events(severity);
CREATE INDEX IF NOT EXISTS idx_breach_events_detected_at ON public.breach_events(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_breach_events_risk_score ON public.breach_events(risk_score DESC);

-- RLS for breach events (admin only)
ALTER TABLE public.breach_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Only admins can view breach events"
    ON public.breach_events
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Only admins can create breach events"
    ON public.breach_events
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

CREATE POLICY "Only admins can update breach events"
    ON public.breach_events
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_breach_events_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_breach_events_updated_at
    BEFORE UPDATE ON public.breach_events
    FOR EACH ROW
    EXECUTE FUNCTION update_breach_events_updated_at();






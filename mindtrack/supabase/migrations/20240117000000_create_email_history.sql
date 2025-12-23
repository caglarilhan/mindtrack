-- Email history and status tracking
-- Tracks all sent emails for audit and monitoring

CREATE TABLE IF NOT EXISTS public.email_history (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    recipient_emails text[] NOT NULL,
    subject text NOT NULL,
    email_type text NOT NULL, -- 'soap', 'risk', 'appointment', 'share', 'other'
    related_id uuid, -- ID of related record (note_id, risk_log_id, etc.)
    related_type text, -- 'soap_note', 'risk_log', 'appointment', etc.
    provider text NOT NULL, -- 'resend', 'sendgrid', 'smtp'
    message_id text, -- Provider's message ID
    status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'sent', 'delivered', 'bounced', 'failed', 'opened', 'clicked')),
    error_message text,
    sent_at timestamptz,
    delivered_at timestamptz,
    opened_at timestamptz,
    clicked_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_email_history_user_id ON public.email_history(user_id);
CREATE INDEX IF NOT EXISTS idx_email_history_related ON public.email_history(related_type, related_id);
CREATE INDEX IF NOT EXISTS idx_email_history_status ON public.email_history(status);
CREATE INDEX IF NOT EXISTS idx_email_history_created_at ON public.email_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_email_history_message_id ON public.email_history(message_id);

-- Email attachments tracking
CREATE TABLE IF NOT EXISTS public.email_attachments (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    email_id uuid NOT NULL REFERENCES public.email_history(id) ON DELETE CASCADE,
    filename text NOT NULL,
    content_type text NOT NULL,
    size_bytes integer NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_email_attachments_email_id ON public.email_attachments(email_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_email_history_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_email_history_updated_at
    BEFORE UPDATE ON public.email_history
    FOR EACH ROW
    EXECUTE FUNCTION update_email_history_updated_at();






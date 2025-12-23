-- Audio Recordings Table
-- HIPAA-compliant encrypted audio storage
-- HIPAA Requirement: §164.312(a)(2)(iv) - Encryption

CREATE TABLE IF NOT EXISTS public.audio_recordings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    session_id uuid NOT NULL,
    client_id uuid NOT NULL REFERENCES public.clients(id) ON DELETE CASCADE,
    encrypted_data text NOT NULL, -- Encrypted audio data (base64)
    encrypted boolean NOT NULL DEFAULT true,
    size_bytes integer NOT NULL,
    content_type text NOT NULL DEFAULT 'audio/webm',
    duration_seconds integer,
    created_at timestamptz NOT NULL DEFAULT now(),
    expires_at timestamptz NOT NULL, -- Retention policy (7 years for HIPAA)
    deleted_at timestamptz
);

CREATE INDEX IF NOT EXISTS idx_audio_recordings_user_id ON public.audio_recordings(user_id);
CREATE INDEX IF NOT EXISTS idx_audio_recordings_session_id ON public.audio_recordings(session_id);
CREATE INDEX IF NOT EXISTS idx_audio_recordings_client_id ON public.audio_recordings(client_id);
CREATE INDEX IF NOT EXISTS idx_audio_recordings_expires_at ON public.audio_recordings(expires_at);
CREATE INDEX IF NOT EXISTS idx_audio_recordings_created_at ON public.audio_recordings(created_at DESC);

-- RLS for audio recordings
ALTER TABLE public.audio_recordings ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only access their own audio recordings
CREATE POLICY "Users can view own audio recordings"
    ON public.audio_recordings
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users can only create their own audio recordings
CREATE POLICY "Users can create own audio recordings"
    ON public.audio_recordings
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can only delete their own audio recordings
CREATE POLICY "Users can delete own audio recordings"
    ON public.audio_recordings
    FOR DELETE
    USING (auth.uid() = user_id);

-- Function to automatically set expiration (7 years)
CREATE OR REPLACE FUNCTION set_audio_expiration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.expires_at IS NULL THEN
        NEW.expires_at = NEW.created_at + INTERVAL '7 years';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_audio_expiration_trigger
    BEFORE INSERT ON public.audio_recordings
    FOR EACH ROW
    EXECUTE FUNCTION set_audio_expiration();






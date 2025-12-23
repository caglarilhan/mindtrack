-- HIPAA Foundation Migration
-- Creates tables for HIPAA-compliant features

-- Audit Logs Table
-- HIPAA Requirement: §164.312(b) - Audit Controls
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    action text NOT NULL CHECK (action IN (
        'login', 'logout', 'read', 'create', 'update', 'delete', 
        'export', 'download', 'access_denied', 'failed_login', 
        'password_change', 'role_change'
    )),
    resource_type text NOT NULL,
    resource_id uuid,
    ip_address inet,
    user_agent text,
    success boolean NOT NULL DEFAULT true,
    error_message text,
    metadata jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Indexes for audit logs
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON public.audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON public.audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON public.audit_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_success ON public.audit_logs(success);

-- User Sessions Table
-- For session management and timeout tracking
CREATE TABLE IF NOT EXISTS public.user_sessions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    session_token text NOT NULL UNIQUE,
    ip_address inet,
    user_agent text,
    last_activity timestamptz NOT NULL DEFAULT now(),
    created_at timestamptz NOT NULL DEFAULT now(),
    expires_at timestamptz NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON public.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_token ON public.user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON public.user_sessions(expires_at);

-- Function to clean up expired sessions
CREATE OR REPLACE FUNCTION cleanup_expired_sessions()
RETURNS void AS $$
BEGIN
    DELETE FROM public.user_sessions
    WHERE expires_at < now();
END;
$$ LANGUAGE plpgsql;

-- Encryption Keys Table (for key rotation)
-- In production, use a secure key management service (AWS KMS, Azure Key Vault)
CREATE TABLE IF NOT EXISTS public.encryption_keys (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    key_id text NOT NULL UNIQUE,
    key_version integer NOT NULL DEFAULT 1,
    encrypted_key text NOT NULL, -- Key encrypted with master key
    created_at timestamptz NOT NULL DEFAULT now(),
    rotated_at timestamptz,
    is_active boolean NOT NULL DEFAULT true
);

CREATE INDEX IF NOT EXISTS idx_encryption_keys_key_id ON public.encryption_keys(key_id);
CREATE INDEX IF NOT EXISTS idx_encryption_keys_active ON public.encryption_keys(is_active);

-- Row Level Security (RLS) for audit logs
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only view their own audit logs (unless admin)
CREATE POLICY "Users can view own audit logs"
    ON public.audit_logs
    FOR SELECT
    USING (
        auth.uid() = user_id OR
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Policy: Only system can insert audit logs (via service role)
-- This is typically done via Supabase service role, not user role

-- RLS for user sessions
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only view their own sessions
CREATE POLICY "Users can view own sessions"
    ON public.user_sessions
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users can delete their own sessions
CREATE POLICY "Users can delete own sessions"
    ON public.user_sessions
    FOR DELETE
    USING (auth.uid() = user_id);

-- RLS for encryption keys (admin only)
ALTER TABLE public.encryption_keys ENABLE ROW LEVEL SECURITY;

-- Policy: Only admins can view encryption keys
CREATE POLICY "Only admins can view encryption keys"
    ON public.encryption_keys
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Add role column to profiles if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'profiles' AND column_name = 'role'
    ) THEN
        ALTER TABLE public.profiles ADD COLUMN role text NOT NULL DEFAULT 'therapist' CHECK (role IN ('therapist', 'supervisor', 'admin', 'patient'));
        CREATE INDEX IF NOT EXISTS idx_profiles_role ON public.profiles(role);
    END IF;
END $$;

-- Function to update last_activity timestamp
CREATE OR REPLACE FUNCTION update_session_activity()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_activity = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to update last_activity on session update
CREATE TRIGGER update_session_activity_trigger
    BEFORE UPDATE ON public.user_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_session_activity();






-- Multi-Factor Authentication (MFA) System
-- HIPAA Requirement: §164.312(a)(1) - Access Control

CREATE TABLE IF NOT EXISTS public.mfa_methods (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    method_type text NOT NULL CHECK (method_type IN ('totp', 'sms', 'email', 'biometric')),
    enabled boolean NOT NULL DEFAULT false,
    verified boolean NOT NULL DEFAULT false,
    secret text, -- TOTP secret (encrypted)
    phone_number text, -- For SMS
    email text, -- For Email
    backup_codes text, -- JSON array of backup codes
    created_at timestamptz NOT NULL DEFAULT now(),
    last_used timestamptz,
    verified_at timestamptz
);

CREATE INDEX IF NOT EXISTS idx_mfa_methods_user_id ON public.mfa_methods(user_id);
CREATE INDEX IF NOT EXISTS idx_mfa_methods_enabled ON public.mfa_methods(enabled);
CREATE INDEX IF NOT EXISTS idx_mfa_methods_type ON public.mfa_methods(method_type);

-- MFA OTP Codes (for SMS/Email)
CREATE TABLE IF NOT EXISTS public.mfa_otp_codes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    method text NOT NULL CHECK (method IN ('sms', 'email')),
    code text NOT NULL,
    contact_info text NOT NULL, -- Phone number or email
    used boolean NOT NULL DEFAULT false,
    used_at timestamptz,
    created_at timestamptz NOT NULL DEFAULT now(),
    expires_at timestamptz NOT NULL -- OTP expires in 10 minutes
);

CREATE INDEX IF NOT EXISTS idx_mfa_otp_codes_user_id ON public.mfa_otp_codes(user_id);
CREATE INDEX IF NOT EXISTS idx_mfa_otp_codes_code ON public.mfa_otp_codes(code);
CREATE INDEX IF NOT EXISTS idx_mfa_otp_codes_expires_at ON public.mfa_otp_codes(expires_at);

-- MFA Sessions (track MFA-verified sessions)
CREATE TABLE IF NOT EXISTS public.mfa_sessions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES public.profiles(id) ON DELETE CASCADE,
    session_token text NOT NULL UNIQUE,
    mfa_method_id uuid REFERENCES public.mfa_methods(id) ON DELETE SET NULL,
    verified_at timestamptz NOT NULL DEFAULT now(),
    expires_at timestamptz NOT NULL,
    ip_address inet,
    user_agent text
);

CREATE INDEX IF NOT EXISTS idx_mfa_sessions_user_id ON public.mfa_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_mfa_sessions_token ON public.mfa_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_mfa_sessions_expires_at ON public.mfa_sessions(expires_at);

-- RLS for MFA methods
ALTER TABLE public.mfa_methods ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own MFA methods"
    ON public.mfa_methods
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can create own MFA methods"
    ON public.mfa_methods
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own MFA methods"
    ON public.mfa_methods
    FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own MFA methods"
    ON public.mfa_methods
    FOR DELETE
    USING (auth.uid() = user_id);

-- RLS for MFA OTP codes
ALTER TABLE public.mfa_otp_codes ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own OTP codes"
    ON public.mfa_otp_codes
    FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "System can create OTP codes"
    ON public.mfa_otp_codes
    FOR INSERT
    WITH CHECK (true); -- Created by system

-- RLS for MFA sessions
ALTER TABLE public.mfa_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own MFA sessions"
    ON public.mfa_sessions
    FOR SELECT
    USING (auth.uid() = user_id);

-- Function to clean up expired OTP codes
CREATE OR REPLACE FUNCTION cleanup_expired_otp_codes()
RETURNS void AS $$
BEGIN
    DELETE FROM public.mfa_otp_codes
    WHERE expires_at < now() OR used = true;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up expired MFA sessions
CREATE OR REPLACE FUNCTION cleanup_expired_mfa_sessions()
RETURNS void AS $$
BEGIN
    DELETE FROM public.mfa_sessions
    WHERE expires_at < now();
END;
$$ LANGUAGE plpgsql;






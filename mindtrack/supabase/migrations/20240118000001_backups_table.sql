-- Backups Table for HIPAA-Compliant Data Backup
-- HIPAA Requirement: §164.308(a)(7) - Contingency Plan

CREATE TABLE IF NOT EXISTS public.backups (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    table_name text NOT NULL,
    backup_data text NOT NULL, -- Encrypted or plain JSON data
    encrypted boolean NOT NULL DEFAULT true,
    record_count integer NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    expires_at timestamptz NOT NULL,
    restored_at timestamptz,
    restored_by uuid REFERENCES public.profiles(id)
);

CREATE INDEX IF NOT EXISTS idx_backups_table_name ON public.backups(table_name);
CREATE INDEX IF NOT EXISTS idx_backups_created_at ON public.backups(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_backups_expires_at ON public.backups(expires_at);

-- RLS for backups (admin only)
ALTER TABLE public.backups ENABLE ROW LEVEL SECURITY;

-- Policy: Only admins can view backups
CREATE POLICY "Only admins can view backups"
    ON public.backups
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Policy: Only admins can create backups
CREATE POLICY "Only admins can create backups"
    ON public.backups
    FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Policy: Only admins can restore backups
CREATE POLICY "Only admins can restore backups"
    ON public.backups
    FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE id = auth.uid() AND role = 'admin'
        )
    );






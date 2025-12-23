-- Patient Mode Support Migration
-- Full Client Mode & Lite/Anonymous Client Mode için gerekli alanlar

-- patients tablosuna mode ve lite mode alanları ekle
ALTER TABLE patients 
ADD COLUMN IF NOT EXISTS mode VARCHAR(10) DEFAULT 'full' CHECK (mode IN ('full', 'lite')),
ADD COLUMN IF NOT EXISTS pseudo_name VARCHAR(255),
ADD COLUMN IF NOT EXISTS age_range VARCHAR(20),
ADD COLUMN IF NOT EXISTS encrypted_local_notes BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS mode_upgraded_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS mode_upgraded_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS clinic_id UUID REFERENCES clinics(id) ON DELETE SET NULL,
ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL;

-- Index'ler
CREATE INDEX IF NOT EXISTS idx_patients_mode ON patients(mode);
CREATE INDEX IF NOT EXISTS idx_patients_clinic_id ON patients(clinic_id);
CREATE INDEX IF NOT EXISTS idx_patients_created_by ON patients(created_by);
CREATE INDEX IF NOT EXISTS idx_patients_pseudo_name ON patients(pseudo_name) WHERE pseudo_name IS NOT NULL;

-- Mevcut kayıtlar için varsayılan değer
UPDATE patients SET mode = 'full' WHERE mode IS NULL;

-- Comments
COMMENT ON COLUMN patients.mode IS 'Patient registration mode: full (HIPAA compliant) or lite (GDPR-friendly anonymous)';
COMMENT ON COLUMN patients.pseudo_name IS 'Pseudonym for lite mode patients (e.g., "Client #14")';
COMMENT ON COLUMN patients.age_range IS 'Age range for lite mode (e.g., "25-30")';
COMMENT ON COLUMN patients.encrypted_local_notes IS 'Whether notes are encrypted locally (default true for lite mode)';
COMMENT ON COLUMN patients.mode_upgraded_at IS 'Timestamp when patient was upgraded from lite to full mode';
COMMENT ON COLUMN patients.mode_upgraded_by IS 'User who upgraded the patient mode';











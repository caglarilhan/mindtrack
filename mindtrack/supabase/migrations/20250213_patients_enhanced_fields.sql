-- Enhanced Patient Fields for Professional Patient List
-- Add fields for status, risk level, diagnosis, etc.

-- Add status field if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'patients' AND column_name = 'status'
    ) THEN
        ALTER TABLE patients ADD COLUMN status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'pending', 'evaluation'));
    END IF;
END $$;

-- Add risk_level field if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'patients' AND column_name = 'risk_level'
    ) THEN
        ALTER TABLE patients ADD COLUMN risk_level VARCHAR(10) DEFAULT 'low' CHECK (risk_level IN ('low', 'medium', 'high'));
    END IF;
END $$;

-- Add primary_diagnosis field if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'patients' AND column_name = 'primary_diagnosis'
    ) THEN
        ALTER TABLE patients ADD COLUMN primary_diagnosis VARCHAR(255);
    END IF;
END $$;

-- Add secondary_diagnoses field if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'patients' AND column_name = 'secondary_diagnoses'
    ) THEN
        ALTER TABLE patients ADD COLUMN secondary_diagnoses TEXT[] DEFAULT '{}';
    END IF;
END $$;

-- Add gender field if not exists
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'patients' AND column_name = 'gender'
    ) THEN
        ALTER TABLE patients ADD COLUMN gender VARCHAR(20);
    END IF;
END $$;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_patients_status ON patients(status);
CREATE INDEX IF NOT EXISTS idx_patients_risk_level ON patients(risk_level);
CREATE INDEX IF NOT EXISTS idx_patients_primary_diagnosis ON patients(primary_diagnosis);
CREATE INDEX IF NOT EXISTS idx_patients_portal_access ON patients(portal_access_enabled);
CREATE INDEX IF NOT EXISTS idx_patients_last_portal_login ON patients(last_portal_login);

-- Update existing records to have default values
UPDATE patients SET status = 'active' WHERE status IS NULL;
UPDATE patients SET risk_level = 'low' WHERE risk_level IS NULL;
UPDATE patients SET secondary_diagnoses = '{}' WHERE secondary_diagnoses IS NULL;

COMMENT ON COLUMN patients.status IS 'Patient status: active, inactive, pending, evaluation';
COMMENT ON COLUMN patients.risk_level IS 'Risk level: low, medium, high';
COMMENT ON COLUMN patients.primary_diagnosis IS 'Primary DSM-5 diagnosis code and description';
COMMENT ON COLUMN patients.secondary_diagnoses IS 'Array of secondary diagnosis codes';











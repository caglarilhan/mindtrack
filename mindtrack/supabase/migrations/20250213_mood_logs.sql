-- Mood Logs Table
-- Patient mood check-in tracking

CREATE TABLE IF NOT EXISTS mood_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 1 AND score <= 5),
    note TEXT,
    date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_mood_logs_patient_id ON mood_logs(patient_id);
CREATE INDEX IF NOT EXISTS idx_mood_logs_user_id ON mood_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_mood_logs_date ON mood_logs(date);
CREATE INDEX IF NOT EXISTS idx_mood_logs_patient_date ON mood_logs(patient_id, date DESC);

-- Unique constraint: one mood log per patient per day
CREATE UNIQUE INDEX IF NOT EXISTS idx_mood_logs_patient_date_unique ON mood_logs(patient_id, date);

-- RLS Policies
ALTER TABLE mood_logs ENABLE ROW LEVEL SECURITY;

-- Patients can only see their own mood logs
CREATE POLICY "Patients can view own mood logs"
    ON mood_logs FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM patients
            WHERE patients.id = mood_logs.patient_id
            AND patients.user_id = auth.uid()
        )
    );

-- Patients can insert their own mood logs
CREATE POLICY "Patients can insert own mood logs"
    ON mood_logs FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM patients
            WHERE patients.id = mood_logs.patient_id
            AND patients.user_id = auth.uid()
        )
    );

-- Therapists can view mood logs of their patients
CREATE POLICY "Therapists can view patient mood logs"
    ON mood_logs FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM appointments
            WHERE appointments.patient_id = mood_logs.patient_id
            AND appointments.provider_id = auth.uid()
        )
    );

COMMENT ON TABLE mood_logs IS 'Daily mood check-in logs from patients (1-5 scale)';
COMMENT ON COLUMN mood_logs.score IS 'Mood score: 1=very bad, 2=bad, 3=neutral, 4=good, 5=very good';
COMMENT ON COLUMN mood_logs.date IS 'Date of the mood check (one entry per day per patient)';











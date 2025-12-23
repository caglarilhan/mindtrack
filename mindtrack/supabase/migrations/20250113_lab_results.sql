-- Lab Results Schema
-- Laboratuvar sonuçları tablosu

CREATE TABLE IF NOT EXISTS public.lab_results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id UUID NOT NULL REFERENCES auth.users(id),
    test_name TEXT NOT NULL,
    test_code TEXT NOT NULL,
    value TEXT NOT NULL, -- Can be numeric or text
    unit TEXT,
    reference_range TEXT,
    status TEXT NOT NULL CHECK (status IN ('normal', 'abnormal', 'critical')),
    lab_date TIMESTAMP WITH TIME ZONE NOT NULL,
    ordered_by TEXT NOT NULL,
    lab_provider TEXT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policies
ALTER TABLE public.lab_results ENABLE ROW LEVEL SECURITY;

-- Klinik üyeleri hasta laboratuvar sonuçlarını okuyabilir
CREATE POLICY "Clinic members can read lab results" ON public.lab_results
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.clinic_members cm 
            WHERE cm.user_id = auth.uid() 
            AND cm.role IN ('admin', 'clinician', 'staff')
        )
    );

-- Klinik üyeleri laboratuvar sonucu oluşturabilir
CREATE POLICY "Clinic members can create lab results" ON public.lab_results
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.clinic_members cm 
            WHERE cm.user_id = auth.uid() 
            AND cm.role IN ('admin', 'clinician', 'staff')
        )
    );

-- Klinik üyeleri laboratuvar sonucu güncelleyebilir
CREATE POLICY "Clinic members can update lab results" ON public.lab_results
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.clinic_members cm 
            WHERE cm.user_id = auth.uid() 
            AND cm.role IN ('admin', 'clinician', 'staff')
        )
    );

-- Indexes
CREATE INDEX IF NOT EXISTS idx_lab_results_patient_id ON public.lab_results(patient_id);
CREATE INDEX IF NOT EXISTS idx_lab_results_test_code ON public.lab_results(test_code);
CREATE INDEX IF NOT EXISTS idx_lab_results_lab_date ON public.lab_results(lab_date);
CREATE INDEX IF NOT EXISTS idx_lab_results_status ON public.lab_results(status);
CREATE INDEX IF NOT EXISTS idx_lab_results_lab_provider ON public.lab_results(lab_provider);

-- Sample lab results
INSERT INTO public.lab_results (patient_id, test_name, test_code, value, unit, reference_range, status, lab_date, ordered_by, lab_provider, notes) VALUES
('00000000-0000-0000-0000-000000000001', 'Complete Blood Count', 'CBC', 'Normal', '', 'Normal', 'normal', NOW() - INTERVAL '1 day', 'Dr. Ahmet Yılmaz', 'Acibadem Lab', 'Rutin kontrol'),
('00000000-0000-0000-0000-000000000001', 'Lithium Level', 'LITH', '0.8', 'mEq/L', '0.6-1.2', 'normal', NOW() - INTERVAL '2 days', 'Dr. Ahmet Yılmaz', 'Acibadem Lab', 'Lithium tedavisi takibi'),
('00000000-0000-0000-0000-000000000001', 'Liver Function Tests', 'LFT', 'Elevated ALT', '', 'Normal', 'abnormal', NOW() - INTERVAL '3 days', 'Dr. Ahmet Yılmaz', 'Acibadem Lab', 'İlaç yan etkisi kontrolü'),
('00000000-0000-0000-0000-000000000001', 'Thyroid Function Tests', 'TFT', 'TSH: 2.5', 'mIU/L', '0.4-4.0', 'normal', NOW() - INTERVAL '1 week', 'Dr. Ahmet Yılmaz', 'Acibadem Lab', 'Rutin kontrol'),
('00000000-0000-0000-0000-000000000001', 'Kidney Function Tests', 'KFT', 'Creatinine: 1.2', 'mg/dL', '0.6-1.2', 'normal', NOW() - INTERVAL '1 week', 'Dr. Ahmet Yılmaz', 'Acibadem Lab', 'Lithium takibi')
ON CONFLICT DO NOTHING;



-- Patient Messages Schema
-- Hasta mesajlaşma tablosu

CREATE TABLE IF NOT EXISTS public.patient_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id UUID NOT NULL REFERENCES auth.users(id),
    sender_id UUID REFERENCES public.clinic_members(user_id),
    content TEXT NOT NULL,
    message_type TEXT DEFAULT 'text' CHECK (message_type IN ('text', 'image', 'file', 'system')),
    attachments JSONB, -- {"files": [{"name": "file.pdf", "url": "...", "size": 1024}]}
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- RLS Policies
ALTER TABLE public.patient_messages ENABLE ROW LEVEL SECURITY;

-- Hastalar kendi mesajlarını okuyabilir
CREATE POLICY "Patients can read their own messages" ON public.patient_messages
    FOR SELECT USING (patient_id = auth.uid());

-- Klinik üyeleri hasta mesajlarını okuyabilir
CREATE POLICY "Clinic members can read patient messages" ON public.patient_messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.clinic_members cm 
            WHERE cm.user_id = auth.uid() 
            AND cm.role IN ('admin', 'clinician', 'staff')
        )
    );

-- Klinik üyeleri hasta mesajları gönderebilir
CREATE POLICY "Clinic members can send messages" ON public.patient_messages
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.clinic_members cm 
            WHERE cm.user_id = auth.uid() 
            AND cm.role IN ('admin', 'clinician', 'staff')
        )
    );

-- Hastalar kendi mesajlarını güncelleyebilir (okundu olarak işaretleme)
CREATE POLICY "Patients can update their own messages" ON public.patient_messages
    FOR UPDATE USING (patient_id = auth.uid());

-- Indexes
CREATE INDEX IF NOT EXISTS idx_patient_messages_patient_id ON public.patient_messages(patient_id);
CREATE INDEX IF NOT EXISTS idx_patient_messages_sender_id ON public.patient_messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_patient_messages_created_at ON public.patient_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_patient_messages_is_read ON public.patient_messages(is_read);

-- Sample messages
INSERT INTO public.patient_messages (patient_id, content, message_type, sender_id) VALUES
('00000000-0000-0000-0000-000000000001', 'Randevunuzu onaylayabilir misiniz?', 'text', NULL),
('00000000-0000-0000-0000-000000000001', 'Yeni eğitim materyali eklendi', 'system', NULL),
('00000000-0000-0000-0000-000000000001', 'İlaçlarınızı düzenli olarak almayı unutmayın', 'text', NULL)
ON CONFLICT DO NOTHING;



-- Education Materials Schema
-- Eğitim materyalleri tablosu

CREATE TABLE IF NOT EXISTS public.education_materials (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('article', 'video', 'pdf', 'infographic')),
    description TEXT NOT NULL,
    content TEXT, -- HTML content for articles
    file_url TEXT, -- URL for videos/PDFs
    read_time_minutes INTEGER,
    category TEXT DEFAULT 'general',
    tags TEXT[],
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES auth.users(id)
);

-- RLS Policies
ALTER TABLE public.education_materials ENABLE ROW LEVEL SECURITY;

-- Herkes aktif materyalleri okuyabilir
CREATE POLICY "Anyone can read active education materials" ON public.education_materials
    FOR SELECT USING (is_active = true);

-- Sadece klinik üyeleri materyal oluşturabilir/güncelleyebilir
CREATE POLICY "Clinic members can manage education materials" ON public.education_materials
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.clinic_members cm 
            WHERE cm.user_id = auth.uid() 
            AND cm.role IN ('admin', 'clinician')
        )
    );

-- Indexes
CREATE INDEX IF NOT EXISTS idx_education_materials_active ON public.education_materials(is_active);
CREATE INDEX IF NOT EXISTS idx_education_materials_type ON public.education_materials(type);
CREATE INDEX IF NOT EXISTS idx_education_materials_category ON public.education_materials(category);

-- Sample data
INSERT INTO public.education_materials (title, type, description, content, read_time_minutes, category, tags) VALUES
('Anksiyete Bozuklukları Hakkında', 'article', 'Anksiyete belirtileri ve başa çıkma yöntemleri', '<h2>Anksiyete Nedir?</h2><p>Anksiyete, gelecekteki olaylara karşı duyulan endişe ve korku hissidir...</p>', 5, 'mental-health', ARRAY['anksiyete', 'stres', 'psikoloji']),
('Nefes Egzersizleri Videosu', 'video', 'Günlük stres yönetimi için nefes teknikleri', NULL, 10, 'wellness', ARRAY['nefes', 'meditasyon', 'stres-yönetimi']),
('İlaç Kullanım Rehberi', 'pdf', 'Psikiyatrik ilaçların doğru kullanımı', NULL, 15, 'medication', ARRAY['ilaç', 'psikiyatri', 'güvenlik']),
('Depresyon Belirtileri', 'infographic', 'Depresyonun erken belirtilerini tanıma', NULL, 3, 'mental-health', ARRAY['depresyon', 'belirtiler', 'erken-tanı'])
ON CONFLICT DO NOTHING;



-- SOAP notu versiyonlama tablosu
CREATE TABLE IF NOT EXISTS soap_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
  version INTEGER NOT NULL,
  soap_data JSONB NOT NULL, -- {subjective, objective, assessment, plan}
  notes TEXT,
  created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Unique constraint: her client için versiyon numarası unique
  UNIQUE(client_id, version),
  
  -- Indexes
  INDEX idx_soap_versions_client_id ON soap_versions(client_id),
  INDEX idx_soap_versions_version ON soap_versions(client_id, version DESC),
  INDEX idx_soap_versions_created_at ON soap_versions(created_at DESC)
);

-- RLS (Row Level Security) politikaları
ALTER TABLE soap_versions ENABLE ROW LEVEL SECURITY;

-- Provider'lar kendi client'larının SOAP versiyonlarını görebilir
CREATE POLICY "Providers can view their clients' SOAP versions"
  ON soap_versions FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM clients
      WHERE clients.id = soap_versions.client_id
      AND clients.owner_id = auth.uid()
    )
  );

-- Provider'lar SOAP versiyonu oluşturabilir
CREATE POLICY "Providers can create SOAP versions"
  ON soap_versions FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM clients
      WHERE clients.id = soap_versions.client_id
      AND clients.owner_id = auth.uid()
    )
  );

-- Comments
COMMENT ON TABLE soap_versions IS 'SOAP notu versiyonları - değişiklik geçmişi ve geri alma için';
COMMENT ON COLUMN soap_versions.version IS 'Versiyon numarası (1, 2, 3, ...)';
COMMENT ON COLUMN soap_versions.soap_data IS 'SOAP notu verisi (JSON formatında)';
COMMENT ON COLUMN soap_versions.notes IS 'Versiyon notları (opsiyonel)';






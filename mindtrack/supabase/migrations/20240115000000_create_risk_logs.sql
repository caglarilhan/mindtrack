-- Risk loglama tablosu
CREATE TABLE IF NOT EXISTS risk_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
  session_id UUID REFERENCES sessions(id) ON DELETE SET NULL,
  risk_level VARCHAR(10) NOT NULL CHECK (risk_level IN ('high', 'medium', 'low')),
  keywords TEXT[] NOT NULL DEFAULT '{}',
  transcript_snippet TEXT NOT NULL,
  risk_score INTEGER DEFAULT 0,
  created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  
  -- Indexes
  INDEX idx_risk_logs_client_id ON risk_logs(client_id),
  INDEX idx_risk_logs_risk_level ON risk_logs(risk_level),
  INDEX idx_risk_logs_created_at ON risk_logs(created_at DESC)
);

-- RLS (Row Level Security) politikaları
ALTER TABLE risk_logs ENABLE ROW LEVEL SECURITY;

-- Provider'lar kendi client'larının risk loglarını görebilir
CREATE POLICY "Providers can view their clients' risk logs"
  ON risk_logs FOR SELECT
  USING (
    EXISTS (
      SELECT 1 FROM clients
      WHERE clients.id = risk_logs.client_id
      AND clients.owner_id = auth.uid()
    )
  );

-- Provider'lar risk log oluşturabilir
CREATE POLICY "Providers can create risk logs"
  ON risk_logs FOR INSERT
  WITH CHECK (
    EXISTS (
      SELECT 1 FROM clients
      WHERE clients.id = risk_logs.client_id
      AND clients.owner_id = auth.uid()
    )
  );

-- Comments
COMMENT ON TABLE risk_logs IS 'Risk analizi kayıtları - hasta transkriptlerinden tespit edilen riskler';
COMMENT ON COLUMN risk_logs.risk_level IS 'Risk seviyesi: high, medium, low';
COMMENT ON COLUMN risk_logs.keywords IS 'Tespit edilen riskli kelimeler dizisi';
COMMENT ON COLUMN risk_logs.transcript_snippet IS 'Risk tespit edilen transkript parçası (max 1000 karakter)';
COMMENT ON COLUMN risk_logs.risk_score IS 'Risk skoru (0-100)';






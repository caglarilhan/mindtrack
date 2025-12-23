-- Social worker specific tables: care_tasks & care_handoffs

CREATE TABLE IF NOT EXISTS care_tasks (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  clinic_id UUID NOT NULL,
  patient_id UUID,
  owner_id UUID NOT NULL,
  domain TEXT NOT NULL, -- housing, employment, education, finances, legal, family
  title TEXT NOT NULL,
  description TEXT,
  risk_level TEXT NOT NULL DEFAULT 'medium', -- low, medium, high
  status TEXT NOT NULL DEFAULT 'todo', -- todo, in_progress, done
  region TEXT NOT NULL DEFAULT 'us',
  due_date DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_care_tasks_clinic ON care_tasks(clinic_id);
CREATE INDEX IF NOT EXISTS idx_care_tasks_owner ON care_tasks(owner_id);
CREATE INDEX IF NOT EXISTS idx_care_tasks_patient ON care_tasks(patient_id);
CREATE INDEX IF NOT EXISTS idx_care_tasks_status ON care_tasks(status);

CREATE TABLE IF NOT EXISTS care_handoffs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  clinic_id UUID NOT NULL,
  patient_id UUID,
  from_role TEXT NOT NULL,
  to_role TEXT NOT NULL,
  summary TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'open', -- open, in_progress, done
  created_by UUID NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_care_handoffs_clinic ON care_handoffs(clinic_id);
CREATE INDEX IF NOT EXISTS idx_care_handoffs_patient ON care_handoffs(patient_id);
CREATE INDEX IF NOT EXISTS idx_care_handoffs_status ON care_handoffs(status);

-- Updated_at triggers reuse global function
CREATE TRIGGER trg_care_tasks_updated_at
  BEFORE UPDATE ON care_tasks
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_care_handoffs_updated_at
  BEFORE UPDATE ON care_handoffs
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

ALTER TABLE care_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE care_handoffs ENABLE ROW LEVEL SECURITY;

CREATE POLICY care_tasks_sw_select ON care_tasks
  FOR SELECT USING (
    owner_id = auth.uid() OR clinic_id IN (
      SELECT clinic_id FROM clinic_members WHERE user_id = auth.uid() AND status = 'active'
    )
  );

CREATE POLICY care_tasks_sw_insert ON care_tasks
  FOR INSERT WITH CHECK (
    owner_id = auth.uid()
  );

CREATE POLICY care_tasks_sw_update ON care_tasks
  FOR UPDATE USING (
    owner_id = auth.uid()
  ) WITH CHECK (
    owner_id = auth.uid()
  );

CREATE POLICY care_handoffs_select ON care_handoffs
  FOR SELECT USING (
    clinic_id IN (
      SELECT clinic_id FROM clinic_members WHERE user_id = auth.uid() AND status = 'active'
    )
  );

CREATE POLICY care_handoffs_insert ON care_handoffs
  FOR INSERT WITH CHECK (
    clinic_id IN (
      SELECT clinic_id FROM clinic_members WHERE user_id = auth.uid() AND status = 'active'
    )
  );

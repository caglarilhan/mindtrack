-- Performance optimization indexes for SOAP notes and related tables
-- These indexes improve query performance significantly

-- Notes table indexes
CREATE INDEX IF NOT EXISTS idx_notes_client_type_created 
ON notes(client_id, type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_notes_type_created 
ON notes(type, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_notes_owner_created 
ON notes(owner_id, created_at DESC);

-- SOAP versions indexes
CREATE INDEX IF NOT EXISTS idx_soap_versions_note_version 
ON soap_versions(note_id, version_number DESC);

-- Therapy sessions indexes
CREATE INDEX IF NOT EXISTS idx_therapy_sessions_client_created 
ON therapy_sessions(client_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_therapy_sessions_status_created 
ON therapy_sessions(status, created_at DESC);

-- Risk logs indexes
CREATE INDEX IF NOT EXISTS idx_risk_logs_client_created 
ON risk_logs(client_id, logged_at DESC);

CREATE INDEX IF NOT EXISTS idx_risk_logs_level_created 
ON risk_logs(risk_level, logged_at DESC);

CREATE INDEX IF NOT EXISTS idx_risk_logs_resolved 
ON risk_logs(is_resolved, logged_at DESC) 
WHERE is_resolved = false;

-- Clients indexes
CREATE INDEX IF NOT EXISTS idx_clients_status_name 
ON clients(status, name);

-- Analytics optimization: Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_notes_analytics 
ON notes(client_id, type, created_at DESC) 
WHERE type = 'SOAP';

-- Session notes indexes
CREATE INDEX IF NOT EXISTS idx_session_notes_session_client 
ON session_notes(session_id, client_id);

CREATE INDEX IF NOT EXISTS idx_session_notes_client_created 
ON session_notes(client_id, created_at DESC);

-- AI feedback indexes
CREATE INDEX IF NOT EXISTS idx_ai_feedback_user_created 
ON ai_feedback(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ai_feedback_soap_created 
ON ai_feedback(soap_id, created_at DESC) 
WHERE soap_id IS NOT NULL;

-- Partial indexes for better performance on filtered queries
CREATE INDEX IF NOT EXISTS idx_notes_active_clients 
ON notes(client_id, created_at DESC) 
WHERE client_id IN (SELECT id FROM clients WHERE status = 'active');

-- Covering index for common SOAP note queries
CREATE INDEX IF NOT EXISTS idx_notes_soap_covering 
ON notes(client_id, type, created_at DESC, id) 
WHERE type = 'SOAP';






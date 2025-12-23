-- Patient Messages Table
-- Secure messaging between patients and therapists

CREATE TABLE IF NOT EXISTS patient_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    sender_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    recipient_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_crisis BOOLEAN DEFAULT false,
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for patient_messages
CREATE INDEX IF NOT EXISTS idx_patient_messages_patient_id ON patient_messages(patient_id);
CREATE INDEX IF NOT EXISTS idx_patient_messages_sender_id ON patient_messages(sender_id);
CREATE INDEX IF NOT EXISTS idx_patient_messages_recipient_id ON patient_messages(recipient_id);
CREATE INDEX IF NOT EXISTS idx_patient_messages_is_read ON patient_messages(is_read);
CREATE INDEX IF NOT EXISTS idx_patient_messages_is_crisis ON patient_messages(is_crisis);
CREATE INDEX IF NOT EXISTS idx_patient_messages_created_at ON patient_messages(created_at DESC);

-- Patient Notifications Table
-- Notifications for appointments, assignments, forms, etc.

CREATE TABLE IF NOT EXISTS patient_notifications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    patient_id UUID NOT NULL REFERENCES patients(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL CHECK (type IN (
        'appointment_reminder',
        'appointment_cancelled',
        'appointment_confirmed',
        'assignment_assigned',
        'assignment_due',
        'form_assigned',
        'form_overdue',
        'message_received',
        'crisis_alert',
        'general'
    )),
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for patient_notifications
CREATE INDEX IF NOT EXISTS idx_patient_notifications_patient_id ON patient_notifications(patient_id);
CREATE INDEX IF NOT EXISTS idx_patient_notifications_type ON patient_notifications(type);
CREATE INDEX IF NOT EXISTS idx_patient_notifications_is_read ON patient_notifications(is_read);
CREATE INDEX IF NOT EXISTS idx_patient_notifications_created_at ON patient_notifications(created_at DESC);

-- RLS Policies for patient_messages
ALTER TABLE patient_messages ENABLE ROW LEVEL SECURITY;

-- Patients can view messages where they are sender or recipient
CREATE POLICY "Patients can view own messages"
    ON patient_messages FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM patients
            WHERE patients.id = patient_messages.patient_id
            AND patients.user_id = auth.uid()
        )
        AND (
            patient_messages.sender_id = auth.uid()
            OR patient_messages.recipient_id = auth.uid()
        )
    );

-- Patients can send messages
CREATE POLICY "Patients can send messages"
    ON patient_messages FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM patients
            WHERE patients.id = patient_messages.patient_id
            AND patients.user_id = auth.uid()
        )
        AND patient_messages.sender_id = auth.uid()
    );

-- Patients can update their own messages (mark as read)
CREATE POLICY "Patients can update own messages"
    ON patient_messages FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM patients
            WHERE patients.id = patient_messages.patient_id
            AND patients.user_id = auth.uid()
        )
    );

-- Therapists can view messages of their patients
CREATE POLICY "Therapists can view patient messages"
    ON patient_messages FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM appointments
            WHERE appointments.patient_id = patient_messages.patient_id
            AND appointments.provider_id = auth.uid()
        )
    );

-- RLS Policies for patient_notifications
ALTER TABLE patient_notifications ENABLE ROW LEVEL SECURITY;

-- Patients can view their own notifications
CREATE POLICY "Patients can view own notifications"
    ON patient_notifications FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM patients
            WHERE patients.id = patient_notifications.patient_id
            AND patients.user_id = auth.uid()
        )
    );

-- Patients can update their own notifications (mark as read)
CREATE POLICY "Patients can update own notifications"
    ON patient_notifications FOR UPDATE
    USING (
        EXISTS (
            SELECT 1 FROM patients
            WHERE patients.id = patient_notifications.patient_id
            AND patients.user_id = auth.uid()
        )
    );

-- Therapists can create notifications for their patients
CREATE POLICY "Therapists can create patient notifications"
    ON patient_notifications FOR INSERT
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM appointments
            WHERE appointments.patient_id = patient_notifications.patient_id
            AND appointments.provider_id = auth.uid()
        )
    );

COMMENT ON TABLE patient_messages IS 'Secure messaging between patients and therapists';
COMMENT ON COLUMN patient_messages.is_crisis IS 'Flag for crisis/urgent messages that require immediate attention';
COMMENT ON TABLE patient_notifications IS 'Notifications for appointments, assignments, forms, etc.';
COMMENT ON COLUMN patient_notifications.type IS 'Type of notification: appointment_reminder, assignment_assigned, form_assigned, etc.';











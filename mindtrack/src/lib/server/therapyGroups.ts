import { createSupabaseServerClient } from "@/lib/supabaseClient";

export interface GroupSession {
  id: string;
  sessionType: "group" | "family" | "couples";
  sessionDate: string;
  modality: string;
  topic?: string;
  participants: { patientId: string; role: string }[];
}

export interface SupervisionNote {
  id: string;
  patientId: string;
  therapistId: string;
  note: string;
  createdAt: string;
}

export async function fetchGroupSessionsForPatient(patientId: string): Promise<GroupSession[]> {
  const supabase = await createSupabaseServerClient();
  const { data, error } = await supabase
    .from("group_session_participants")
    .select(
      `session_id, role, group_sessions:session_id (id, session_type, session_date, modality, topic, group_session_participants (patient_id, role))`
    )
    .eq("patient_id", patientId)
    .order("session_date", { referencedTable: "group_sessions", ascending: false });

  if (error) {
    console.error("[therapyGroups] fetch error", error);
    return [];
  }

  return (data || []).map((row) => ({
    id: row.group_sessions.id,
    sessionType: row.group_sessions.session_type,
    sessionDate: row.group_sessions.session_date,
    modality: row.group_sessions.modality,
    topic: row.group_sessions.topic,
    participants: row.group_sessions.group_session_participants.map((p: any) => ({ patientId: p.patient_id, role: p.role })),
  }));
}

export async function fetchSupervisionNotes(patientId: string, limit = 10): Promise<SupervisionNote[]> {
  const supabase = await createSupabaseServerClient();
  const { data, error } = await supabase
    .from("supervision_notes")
    .select("id, patient_id, therapist_id, note, created_at")
    .eq("patient_id", patientId)
    .order("created_at", { ascending: false })
    .limit(limit);

  if (error) {
    console.error("[supervision] fetch error", error);
    return [];
  }

  return (data || []).map((row) => ({
    id: row.id,
    patientId: row.patient_id,
    therapistId: row.therapist_id,
    note: row.note,
    createdAt: row.created_at,
  }));
}

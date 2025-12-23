import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL;
const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

function getAdminClient() {
  if (!SUPABASE_URL || !SERVICE_ROLE_KEY) {
    return null;
  }
  return createClient(SUPABASE_URL, SERVICE_ROLE_KEY, {
    auth: { autoRefreshToken: false, persistSession: false },
  });
}

export interface RecordingMetadata {
  sessionId: string;
  recordingUrl: string;
  duration: number;
  fileSize: number;
  quality: "SD" | "HD" | "FHD";
  storageLocation: string;
  encrypted: boolean;
}

export async function saveRecordingMetadata(metadata: RecordingMetadata) {
  const adminClient = getAdminClient();
  if (!adminClient) {
    throw new Error("Service role client unavailable");
  }

  const { error } = await adminClient.from("video_session_recordings").insert({
    session_id: metadata.sessionId,
    recording_url: metadata.recordingUrl,
    recording_duration: metadata.duration,
    file_size: metadata.fileSize,
    recording_quality: metadata.quality,
    storage_location: metadata.storageLocation,
  });

  if (error) {
    console.error("[telehealth-recording] save error", error);
    throw error;
  }

  return { success: true };
}

export async function getRecordingMetadata(sessionId: string) {
  const adminClient = getAdminClient();
  if (!adminClient) {
    return null;
  }

  const { data, error } = await adminClient
    .from("video_session_recordings")
    .select("*")
    .eq("session_id", sessionId)
    .order("created_at", { ascending: false })
    .limit(1)
    .maybeSingle();

  if (error) {
    console.error("[telehealth-recording] fetch error", error);
    return null;
  }

  return data;
}

export async function generateSignedDownloadUrl(recordingUrl: string, expiresIn: number = 3600): Promise<string | null> {
  // TODO: S3 signed URL generation (AWS SDK v3)
  // Şu an için recordingUrl'i döndürüyoruz
  return recordingUrl;
}

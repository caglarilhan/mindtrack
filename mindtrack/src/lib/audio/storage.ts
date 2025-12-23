/**
 * Encrypted Audio Storage
 * HIPAA-compliant audio storage with encryption and retention policies
 */

import { encryptAudioData, decryptAudioData } from "./audio-encryption";
import { createClient } from "@/utils/supabase/server";

export interface AudioStorageMetadata {
  id: string;
  userId: string;
  sessionId: string;
  clientId: string;
  encrypted: boolean;
  size: number;
  type: string;
  duration?: number; // seconds
  createdAt: string;
  expiresAt: string; // Retention policy
}

/**
 * Store encrypted audio
 */
export async function storeEncryptedAudio(
  audioBlob: Blob,
  metadata: {
    userId: string;
    sessionId: string;
    clientId: string;
    duration?: number;
  }
): Promise<{ success: boolean; audioId?: string; error?: string }> {
  try {
    const supabase = await createClient();

    // Encrypt audio
    const { encrypted, metadata: audioMetadata } = await encryptAudioData(audioBlob);

    // Calculate expiration (7 years for HIPAA)
    const expiresAt = new Date();
    expiresAt.setFullYear(expiresAt.getFullYear() + 7);

    // Store in database
    const { data, error } = await supabase
      .from("audio_recordings")
      .insert({
        user_id: metadata.userId,
        session_id: metadata.sessionId,
        client_id: metadata.clientId,
        encrypted_data: encrypted,
        encrypted: true,
        size_bytes: audioMetadata.size,
        content_type: audioMetadata.type,
        duration_seconds: metadata.duration || null,
        expires_at: expiresAt.toISOString(),
      })
      .select("id")
      .single();

    if (error) {
      throw new Error(`Failed to store audio: ${error.message}`);
    }

    return {
      success: true,
      audioId: data.id,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Audio storage error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Retrieve encrypted audio
 */
export async function retrieveEncryptedAudio(
  audioId: string,
  userId: string
): Promise<{ success: boolean; audioBlob?: Blob; error?: string }> {
  try {
    const supabase = await createClient();

    // Get audio record
    const { data, error } = await supabase
      .from("audio_recordings")
      .select("*")
      .eq("id", audioId)
      .eq("user_id", userId)
      .single();

    if (error || !data) {
      throw new Error("Audio recording not found");
    }

    // Check expiration
    if (new Date(data.expires_at) < new Date()) {
      throw new Error("Audio recording has expired");
    }

    // Decrypt audio
    const audioBlob = await decryptAudioData(data.encrypted_data, {
      size: data.size_bytes,
      type: data.content_type,
    });

    return {
      success: true,
      audioBlob,
    };
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : "Unknown error";
    console.error("Audio retrieval error:", error);
    return {
      success: false,
      error: errorMessage,
    };
  }
}

/**
 * Delete expired audio recordings
 */
export async function cleanupExpiredAudio(): Promise<number> {
  try {
    const supabase = await createClient();

    const { data, error } = await supabase
      .from("audio_recordings")
      .delete()
      .lt("expires_at", new Date().toISOString())
      .select("id");

    if (error) {
      console.error("Failed to cleanup expired audio:", error);
      return 0;
    }

    return data?.length || 0;
  } catch (error) {
    console.error("Audio cleanup error:", error);
    return 0;
  }
}

/**
 * Get audio recordings for a session
 */
export async function getSessionAudioRecordings(
  sessionId: string,
  userId: string
): Promise<AudioStorageMetadata[]> {
  try {
    const supabase = await createClient();

    const { data, error } = await supabase
      .from("audio_recordings")
      .select("id, user_id, session_id, client_id, encrypted, size_bytes, content_type, duration_seconds, created_at, expires_at")
      .eq("session_id", sessionId)
      .eq("user_id", userId)
      .order("created_at", { ascending: false });

    if (error) {
      console.error("Failed to get audio recordings:", error);
      return [];
    }

    return (data || []).map((recording) => ({
      id: recording.id,
      userId: recording.user_id,
      sessionId: recording.session_id,
      clientId: recording.client_id,
      encrypted: recording.encrypted,
      size: recording.size_bytes,
      type: recording.content_type,
      duration: recording.duration_seconds || undefined,
      createdAt: recording.created_at,
      expiresAt: recording.expires_at,
    }));
  } catch (error) {
    console.error("Get audio recordings error:", error);
    return [];
  }
}






import { v4 as uuidv4 } from 'uuid';

export type TelehealthProvider = 'zoom' | 'google_meet' | 'custom';

export interface GenerateTelehealthLinkInput {
  provider?: TelehealthProvider;
  customUrl?: string;
}

export interface GenerateTelehealthLinkResult {
  provider: TelehealthProvider;
  url: string;
  sessionId: string;
}

export interface RecordingPayload {
  sessionId: string;
  recordingUrl: string;
  duration?: number;
  fileSize?: number;
  quality?: "SD" | "HD" | "FHD";
  storageLocation?: string;
}

export interface TranscriptIngestSegment {
  speaker: "patient" | "provider" | "caregiver" | "system";
  text: string;
  startTime?: number;
  endTime?: number;
  sentimentScore?: number;
}

function getBaseUrl(): string {
  // Prefer explicit base URL; fallback to example domain
  return (
    process.env.TELEHEALTH_BASE_URL ||
    process.env.NEXT_PUBLIC_SITE_URL ||
    'https://app.mindtrack.example'
  ).replace(/\/$/, '');
}

export function generateTelehealthLink(
  input: GenerateTelehealthLinkInput
): GenerateTelehealthLinkResult {
  const provider: TelehealthProvider = input.provider || 'custom';
  const sessionId = uuidv4();

  if (provider === 'custom') {
    const base = getBaseUrl();
    const url = input.customUrl?.trim() || `${base}/telehealth/session/${sessionId}`;
    return { provider, url, sessionId };
  }

  // Placeholders for Zoom/Google Meet; real integrations can replace these
  if (provider === 'zoom') {
    const url = `https://zoom.us/j/${sessionId.replace(/-/g, '').slice(0, 11)}`;
    return { provider, url, sessionId };
  }

  const meetId = sessionId.split('-')[0];
  const url = `https://meet.google.com/${meetId}`;
  return { provider: 'google_meet', url, sessionId };
}

// ---- Client-side helperlar ----

export async function saveRecording(metadata: RecordingPayload) {
  const res = await fetch("/api/telehealth/recordings", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sessionId: metadata.sessionId,
      recordingUrl: metadata.recordingUrl,
      duration: metadata.duration,
      fileSize: metadata.fileSize,
      quality: metadata.quality,
      storageLocation: metadata.storageLocation,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.error || "Recording kaydedilemedi");
  }
  return res.json();
}

export async function fetchTranscripts(sessionId: string, includeRisks = true) {
  const qs = new URLSearchParams({ sessionId, includeRisks: includeRisks ? "true" : "false" });
  const res = await fetch(`/api/telehealth/transcripts?${qs.toString()}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.error || "Transcript alınamadı");
  }
  return res.json();
}

export async function fetchRiskFeed(sessionId: string) {
  const qs = new URLSearchParams({ sessionId });
  const res = await fetch(`/api/telehealth/risk-feed?${qs.toString()}`);
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.error || "Risk feed alınamadı");
  }
  return res.json();
}

export async function ingestTranscripts(params: {
  sessionId: string;
  region?: "us" | "eu";
  segments: TranscriptIngestSegment[];
}) {
  const res = await fetch("/api/telehealth/transcripts/ingest", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      sessionId: params.sessionId,
      region: params.region || "us",
      segments: params.segments,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err?.error || "Transcript ingest başarısız");
  }
  return res.json();
}






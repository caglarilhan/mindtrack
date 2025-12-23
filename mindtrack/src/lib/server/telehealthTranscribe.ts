import axios from "axios";

/**
 * AssemblyAI tabanlı basit transcription helper.
 * Beklenen env: ASSEMBLYAI_API_KEY
 */
export async function transcribeAudioFromUrl(params: {
  audioUrl: string;
  speaker?: "patient" | "provider" | "caregiver" | "system";
}) {
  const apiKey = process.env.ASSEMBLYAI_API_KEY;
  if (!apiKey) {
    throw new Error("ASSEMBLYAI_API_KEY eksik");
  }

  const client = axios.create({
    baseURL: "https://api.assemblyai.com/v2",
    headers: {
      authorization: apiKey,
      "content-type": "application/json",
    },
  });

  // Upload adımı atlanıyor; doğrudan public audio URL bekliyoruz.
  const { data: job } = await client.post("/transcript", {
    audio_url: params.audioUrl,
    speaker_labels: false,
    language_detection: true,
    disfluencies: true,
    filter_profanity: false,
    sentiment_analysis: false,
    entity_detection: false,
  });

  // Poll basit: 5 sn interval, 60 sn timeout
  const deadline = Date.now() + 60_000;
  while (Date.now() < deadline) {
    const { data: status } = await client.get(`/transcript/${job.id}`);
    if (status.status === "completed") {
      const text: string = status.text || "";
      return {
        text,
        confidence: status.confidence,
        words: status.words,
      };
    }
    if (status.status === "error") {
      throw new Error(status.error || "Transcription failed");
    }
    await new Promise((res) => setTimeout(res, 5000));
  }

  throw new Error("Transcription timeout (AssemblyAI)");
}











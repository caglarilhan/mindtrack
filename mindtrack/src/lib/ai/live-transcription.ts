import { CRISIS_KEYWORDS, normalizeText } from "@/lib/psychologist/crisis-keywords";

export interface TranscriptChunk {
  text: string;
  speaker: "patient" | "therapist";
  isFinal: boolean;
  timestamp: number;
  riskDetected: boolean;
}

export function isSpeechRecognitionSupported(): boolean {
  return (
    "webkitSpeechRecognition" in window || "SpeechRecognition" in window
  );
}

export function createSpeechRecognition(
  onResult: (chunk: TranscriptChunk) => void,
  onEnd: () => void,
  onError: (error: string) => void,
  speaker: "patient" | "therapist" = "patient"
): SpeechRecognition | null {
  if (!isSpeechRecognitionSupported()) {
    onError("Tarayıcınız Speech Recognition API'sini desteklemiyor.");
    return null;
  }

  const SpeechRecognition =
    (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
  const recognition = new SpeechRecognition();

  recognition.continuous = true;
  recognition.interimResults = true;
  recognition.lang = "tr-TR"; // Türkçe dil desteği

  recognition.onresult = (event: SpeechRecognitionEvent) => {
    let interimTranscript = "";
    let finalTranscript = "";

    for (let i = event.resultIndex; i < event.results.length; ++i) {
      const transcriptPart = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalTranscript += transcriptPart;
      } else {
        interimTranscript += transcriptPart;
      }
    }

    const checkRisk = (text: string) => {
      const normalizedText = normalizeText(text);
      return Object.values(CRISIS_KEYWORDS).some((category) =>
        [...category.tr, ...category.en].some((keyword) =>
          normalizedText.includes(normalizeText(keyword))
        )
      );
    };

    if (interimTranscript) {
      onResult({
        text: interimTranscript,
        speaker,
        isFinal: false,
        timestamp: Date.now(),
        riskDetected: checkRisk(interimTranscript),
      });
    }
    if (finalTranscript) {
      onResult({
        text: finalTranscript,
        speaker,
        isFinal: true,
        timestamp: Date.now(),
        riskDetected: checkRisk(finalTranscript),
      });
    }
  };

  recognition.onend = () => {
    onEnd();
  };

  recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
    console.error("Speech Recognition Error:", event.error);
    onError(event.error);
  };

  return recognition;
}

/**
 * Ses seviyesi analizi (basit)
 */
export function analyzeAudioLevel(audioContext: AudioContext, stream: MediaStream): {
  level: number; // 0-100
  isSpeaking: boolean;
} {
  const analyser = audioContext.createAnalyser();
  const microphone = audioContext.createMediaStreamSource(stream);
  microphone.connect(analyser);

  analyser.fftSize = 256;
  const dataArray = new Uint8Array(analyser.frequencyBinCount);
  analyser.getByteFrequencyData(dataArray);

  const average = dataArray.reduce((a, b) => a + b) / dataArray.length;
  const level = Math.min(100, (average / 255) * 100);
  const isSpeaking = level > 10; // Threshold

  return { level, isSpeaking };
}


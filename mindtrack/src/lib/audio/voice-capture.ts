/**
 * Voice Capture Module
 * HIPAA-compliant real-time voice capture using Web Speech API
 */

export interface VoiceCaptureConfig {
  language?: string; // Default: "tr-TR"
  continuous?: boolean; // Default: true
  interimResults?: boolean; // Default: true
  maxAlternatives?: number; // Default: 1
}

export interface TranscriptionResult {
  transcript: string;
  isFinal: boolean;
  confidence?: number;
  timestamp: number;
}

export interface VoiceCaptureCallbacks {
  onTranscript?: (result: TranscriptionResult) => void;
  onError?: (error: Error) => void;
  onStart?: () => void;
  onStop?: () => void;
  onPause?: () => void;
  onResume?: () => void;
}

export class VoiceCapture {
  private recognition: SpeechRecognition | null = null;
  private isRecording = false;
  private config: Required<VoiceCaptureConfig>;
  private callbacks: VoiceCaptureCallbacks;
  private transcriptBuffer: TranscriptionResult[] = [];

  constructor(
    config: VoiceCaptureConfig = {},
    callbacks: VoiceCaptureCallbacks = {}
  ) {
    this.config = {
      language: config.language || "tr-TR",
      continuous: config.continuous ?? true,
      interimResults: config.interimResults ?? true,
      maxAlternatives: config.maxAlternatives || 1,
    };
    this.callbacks = callbacks;

    this.initializeRecognition();
  }

  /**
   * Initialize Speech Recognition
   */
  private initializeRecognition(): void {
    if (typeof window === "undefined") {
      throw new Error("VoiceCapture can only be used in browser environment");
    }

    // Check browser support
    const SpeechRecognition =
      (window as unknown as { SpeechRecognition?: typeof SpeechRecognition }).SpeechRecognition ||
      (window as unknown as { webkitSpeechRecognition?: typeof SpeechRecognition }).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      throw new Error(
        "Speech Recognition API not supported in this browser. Please use Chrome, Edge, or Safari."
      );
    }

    this.recognition = new SpeechRecognition();
    this.recognition.lang = this.config.language;
    this.recognition.continuous = this.config.continuous;
    this.recognition.interimResults = this.config.interimResults;
    this.recognition.maxAlternatives = this.config.maxAlternatives;

    // Event handlers
    this.recognition.onstart = () => {
      this.isRecording = true;
      this.callbacks.onStart?.();
    };

    this.recognition.onresult = (event: SpeechRecognitionEvent) => {
      let finalTranscript = "";
      let interimTranscript = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const result = event.results[i];
        const transcript = result[0].transcript;
        const confidence = result[0].confidence;

        if (result.isFinal) {
          finalTranscript += transcript + " ";
          
          const transcriptionResult: TranscriptionResult = {
            transcript: transcript.trim(),
            isFinal: true,
            confidence,
            timestamp: Date.now(),
          };

          this.transcriptBuffer.push(transcriptionResult);
          this.callbacks.onTranscript?.(transcriptionResult);
        } else {
          interimTranscript += transcript + " ";
          
          const transcriptionResult: TranscriptionResult = {
            transcript: transcript.trim(),
            isFinal: false,
            confidence,
            timestamp: Date.now(),
          };

          this.callbacks.onTranscript?.(transcriptionResult);
        }
      }
    };

    this.recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
      const error = new Error(`Speech recognition error: ${event.error}`);
      this.callbacks.onError?.(error);
      
      // Handle specific errors
      if (event.error === "no-speech") {
        // No speech detected, but not necessarily an error
        return;
      }
      
      if (event.error === "not-allowed") {
        throw new Error("Microphone access denied. Please allow microphone access.");
      }
    };

    this.recognition.onend = () => {
      this.isRecording = false;
      this.callbacks.onStop?.();
      
      // Auto-restart if continuous mode
      if (this.config.continuous && this.isRecording) {
        try {
          this.recognition?.start();
        } catch (error) {
          // Already started or error
        }
      }
    };
  }

  /**
   * Start recording
   */
  async start(): Promise<void> {
    if (!this.recognition) {
      throw new Error("Speech recognition not initialized");
    }

    if (this.isRecording) {
      console.warn("Already recording");
      return;
    }

    try {
      // Request microphone permission
      await navigator.mediaDevices.getUserMedia({ audio: true });
      
      this.recognition.start();
    } catch (error) {
      const err = error instanceof Error ? error : new Error("Failed to start recording");
      this.callbacks.onError?.(err);
      throw err;
    }
  }

  /**
   * Stop recording
   */
  stop(): void {
    if (!this.recognition) {
      return;
    }

    if (!this.isRecording) {
      return;
    }

    this.recognition.stop();
    this.isRecording = false;
  }

  /**
   * Pause recording
   */
  pause(): void {
    if (!this.recognition || !this.isRecording) {
      return;
    }

    this.recognition.stop();
    this.callbacks.onPause?.();
  }

  /**
   * Resume recording
   */
  resume(): void {
    if (!this.recognition) {
      return;
    }

    if (this.isRecording) {
      return;
    }

    try {
      this.recognition.start();
      this.callbacks.onResume?.();
    } catch (error) {
      const err = error instanceof Error ? error : new Error("Failed to resume recording");
      this.callbacks.onError?.(err);
    }
  }

  /**
   * Get current transcript buffer
   */
  getTranscriptBuffer(): TranscriptionResult[] {
    return [...this.transcriptBuffer];
  }

  /**
   * Clear transcript buffer
   */
  clearBuffer(): void {
    this.transcriptBuffer = [];
  }

  /**
   * Get full transcript (all final results)
   */
  getFullTranscript(): string {
    return this.transcriptBuffer
      .filter((result) => result.isFinal)
      .map((result) => result.transcript)
      .join(" ");
  }

  /**
   * Check if recording
   */
  isActive(): boolean {
    return this.isRecording;
  }

  /**
   * Check browser support
   */
  static isSupported(): boolean {
    if (typeof window === "undefined") {
      return false;
    }

    const SpeechRecognition =
      (window as unknown as { SpeechRecognition?: typeof SpeechRecognition }).SpeechRecognition ||
      (window as unknown as { webkitSpeechRecognition?: typeof SpeechRecognition }).webkitSpeechRecognition;

    return !!SpeechRecognition;
  }

  /**
   * Request microphone permission
   */
  static async requestPermission(): Promise<boolean> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach((track) => track.stop()); // Stop immediately after permission
      return true;
    } catch (error) {
      console.error("Microphone permission denied:", error);
      return false;
    }
  }
}

// Type definitions for Web Speech API
interface SpeechRecognition extends EventTarget {
  lang: string;
  continuous: boolean;
  interimResults: boolean;
  maxAlternatives: number;
  start(): void;
  stop(): void;
  abort(): void;
  onstart: ((this: SpeechRecognition, ev: Event) => unknown) | null;
  onend: ((this: SpeechRecognition, ev: Event) => unknown) | null;
  onerror: ((this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => unknown) | null;
  onresult: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => unknown) | null;
}

interface SpeechRecognitionEvent extends Event {
  resultIndex: number;
  results: SpeechRecognitionResultList;
}

interface SpeechRecognitionResultList {
  length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
  isFinal: boolean;
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

interface SpeechRecognitionErrorEvent extends Event {
  error: string;
  message?: string;
}

declare var SpeechRecognition: {
  prototype: SpeechRecognition;
  new (): SpeechRecognition;
};

declare var webkitSpeechRecognition: {
  prototype: SpeechRecognition;
  new (): SpeechRecognition;
};






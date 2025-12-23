/**
 * Audio Feature Extraction
 * Extracts audio features for emotion analysis (client-side, no data leaves device)
 */

export interface AudioFeatures {
  pitch: number; // Hz
  tempo: number; // words per minute
  pauseFrequency: number; // pauses per minute
  pauseDuration: number; // average pause duration in ms
  volume: number; // 0-1 normalized
  speechRate: number; // syllables per second
  pitchVariation: number; // standard deviation of pitch
  energy: number; // 0-1 normalized
}

export interface AudioAnalysisResult {
  features: AudioFeatures;
  timestamp: number;
  duration: number; // ms
  wordCount: number;
}

/**
 * Extract audio features from audio stream
 * Note: This is a simplified version. Full implementation would use Web Audio API
 */
export class AudioFeatureExtractor {
  private audioContext: AudioContext | null = null;
  private analyser: AnalyserNode | null = null;
  private microphone: MediaStreamAudioSourceNode | null = null;
  private stream: MediaStream | null = null;
  private isAnalyzing = false;
  private pitchHistory: number[] = [];
  private pauseHistory: number[] = [];
  private wordTimings: number[] = [];

  /**
   * Initialize audio context and analyser
   */
  async initialize(): Promise<void> {
    try {
      this.audioContext = new (window.AudioContext || (window as unknown as { webkitAudioContext?: typeof AudioContext }).webkitAudioContext)();
      this.analyser = this.audioContext.createAnalyser();
      this.analyser.fftSize = 2048;
      this.analyser.smoothingTimeConstant = 0.8;
    } catch (error) {
      throw new Error(`Failed to initialize audio context: ${error instanceof Error ? error.message : "Unknown error"}`);
    }
  }

  /**
   * Start analyzing audio stream
   */
  async startAnalysis(stream: MediaStream): Promise<void> {
    if (!this.audioContext || !this.analyser) {
      await this.initialize();
    }

    if (!this.audioContext || !this.analyser) {
      throw new Error("Audio context not initialized");
    }

    this.stream = stream;
    this.microphone = this.audioContext.createMediaStreamSource(stream);
    this.microphone.connect(this.analyser);
    this.isAnalyzing = true;

    // Start continuous analysis
    this.analyzeLoop();
  }

  /**
   * Stop analysis
   */
  stopAnalysis(): void {
    this.isAnalyzing = false;
    
    if (this.microphone) {
      this.microphone.disconnect();
      this.microphone = null;
    }

    if (this.stream) {
      this.stream.getTracks().forEach((track) => track.stop());
      this.stream = null;
    }
  }

  /**
   * Continuous analysis loop
   */
  private analyzeLoop(): void {
    if (!this.isAnalyzing || !this.analyser) {
      return;
    }

    const bufferLength = this.analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);
    this.analyser.getByteFrequencyData(dataArray);

    // Calculate pitch (simplified - using dominant frequency)
    const pitch = this.calculatePitch(dataArray);
    this.pitchHistory.push(pitch);

    // Keep only last 100 samples
    if (this.pitchHistory.length > 100) {
      this.pitchHistory.shift();
    }

    // Continue loop
    requestAnimationFrame(() => this.analyzeLoop());
  }

  /**
   * Calculate pitch from frequency data
   * Simplified implementation - full version would use autocorrelation or FFT
   */
  private calculatePitch(dataArray: Uint8Array): number {
    const sampleRate = this.audioContext?.sampleRate || 44100;
    const nyquist = sampleRate / 2;
    const maxIndex = dataArray.indexOf(Math.max(...Array.from(dataArray)));
    const frequency = (maxIndex / dataArray.length) * nyquist;
    
    // Filter out noise (human voice range: 85-255 Hz for fundamental)
    if (frequency < 85 || frequency > 255) {
      return this.pitchHistory.length > 0 ? this.pitchHistory[this.pitchHistory.length - 1] : 150;
    }
    
    return frequency;
  }

  /**
   * Analyze transcript for speech features
   */
  analyzeTranscript(transcript: string, duration: number): AudioFeatures {
    const words = transcript.split(/\s+/).filter((w) => w.length > 0);
    const wordCount = words.length;
    
    // Calculate tempo (words per minute)
    const tempo = duration > 0 ? (wordCount / duration) * 60000 : 0;
    
    // Calculate speech rate (syllables per second)
    const syllables = this.countSyllables(transcript);
    const speechRate = duration > 0 ? (syllables / duration) * 1000 : 0;
    
    // Detect pauses (simplified - based on punctuation and gaps)
    const pauses = this.detectPauses(transcript, duration);
    const pauseFrequency = duration > 0 ? (pauses.length / duration) * 60000 : 0;
    const pauseDuration = pauses.length > 0
      ? pauses.reduce((sum, p) => sum + p, 0) / pauses.length
      : 0;
    
    // Calculate pitch variation
    const pitchVariation = this.calculatePitchVariation();
    
    // Calculate average pitch
    const pitch = this.pitchHistory.length > 0
      ? this.pitchHistory.reduce((sum, p) => sum + p, 0) / this.pitchHistory.length
      : 150;
    
    // Volume and energy (simplified - would need actual audio analysis)
    const volume = 0.7; // Placeholder
    const energy = 0.6; // Placeholder

    return {
      pitch,
      tempo,
      pauseFrequency,
      pauseDuration,
      volume,
      speechRate,
      pitchVariation,
      energy,
    };
  }

  /**
   * Count syllables in text (simplified)
   */
  private countSyllables(text: string): number {
    // Simplified syllable counting for Turkish
    const vowels = /[aeıioöuüAEIİOÖUÜ]/g;
    const matches = text.match(vowels);
    return matches ? matches.length : 1;
  }

  /**
   * Detect pauses in transcript
   */
  private detectPauses(transcript: string, duration: number): number[] {
    const pauses: number[] = [];
    
    // Detect pauses from punctuation
    const punctuationPauses = (transcript.match(/[.!?]/g) || []).length;
    const avgPauseDuration = punctuationPauses > 0 ? duration / punctuationPauses : 0;
    
    // Estimate pause durations (simplified)
    for (let i = 0; i < punctuationPauses; i++) {
      pauses.push(avgPauseDuration);
    }
    
    return pauses;
  }

  /**
   * Calculate pitch variation (standard deviation)
   */
  private calculatePitchVariation(): number {
    if (this.pitchHistory.length < 2) {
      return 0;
    }

    const mean = this.pitchHistory.reduce((sum, p) => sum + p, 0) / this.pitchHistory.length;
    const variance = this.pitchHistory.reduce((sum, p) => sum + Math.pow(p - mean, 2), 0) / this.pitchHistory.length;
    return Math.sqrt(variance);
  }

  /**
   * Get current features
   */
  getCurrentFeatures(transcript: string, duration: number): AudioFeatures {
    return this.analyzeTranscript(transcript, duration);
  }

  /**
   * Reset analysis data
   */
  reset(): void {
    this.pitchHistory = [];
    this.pauseHistory = [];
    this.wordTimings = [];
  }
}

/**
 * Extract emotion indicators from audio features
 */
export function extractEmotionIndicators(features: AudioFeatures): {
  sadness: number;
  anxiety: number;
  anger: number;
  happiness: number;
  fear: number;
} {
  // Simplified emotion mapping based on audio features
  // In production, this would use machine learning models
  
  const emotions = {
    sadness: 0,
    anxiety: 0,
    anger: 0,
    happiness: 0,
    fear: 0,
  };

  // Low pitch + slow tempo + frequent pauses = sadness
  if (features.pitch < 120 && features.tempo < 100 && features.pauseFrequency > 10) {
    emotions.sadness = 0.7;
  }

  // High pitch variation + fast tempo = anxiety
  if (features.pitchVariation > 30 && features.tempo > 150) {
    emotions.anxiety = 0.7;
  }

  // High pitch + fast tempo + high volume = anger
  if (features.pitch > 180 && features.tempo > 150 && features.volume > 0.8) {
    emotions.anger = 0.7;
  }

  // Moderate pitch + steady tempo = happiness
  if (features.pitch > 140 && features.pitch < 180 && features.tempo > 120 && features.tempo < 160) {
    emotions.happiness = 0.6;
  }

  // High pitch variation + frequent pauses = fear
  if (features.pitchVariation > 25 && features.pauseFrequency > 8) {
    emotions.fear = 0.6;
  }

  return emotions;
}






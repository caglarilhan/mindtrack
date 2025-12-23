"use client";

/**
 * Voice Recorder Component
 * HIPAA-compliant voice recording with real-time transcription
 */

import { useState, useEffect, useRef, useCallback } from "react";
import { VoiceCapture, type TranscriptionResult } from "@/lib/audio/voice-capture";
import { AudioFeatureExtractor, extractEmotionIndicators } from "@/lib/audio/audio-features";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Mic, MicOff, Square, Pause, Play } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

export interface VoiceRecorderProps {
  onTranscript?: (transcript: string, isFinal: boolean) => void;
  onEmotionUpdate?: (emotions: {
    sadness: number;
    anxiety: number;
    anger: number;
    happiness: number;
    fear: number;
  }) => void;
  onError?: (error: Error) => void;
  autoStart?: boolean;
  language?: string;
}

export function VoiceRecorder({
  onTranscript,
  onEmotionUpdate,
  onError,
  autoStart = false,
  language = "tr-TR",
}: VoiceRecorderProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [isSupported, setIsSupported] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const voiceCaptureRef = useRef<VoiceCapture | null>(null);
  const featureExtractorRef = useRef<AudioFeatureExtractor | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const startTimeRef = useRef<number>(0);
  
  const { toast } = useToast();

  useEffect(() => {
    // Check browser support
    setIsSupported(VoiceCapture.isSupported());

    if (!VoiceCapture.isSupported()) {
      setError("Tarayıcınız ses tanıma özelliğini desteklemiyor. Lütfen Chrome, Edge veya Safari kullanın.");
      return;
    }

    // Initialize feature extractor
    const extractor = new AudioFeatureExtractor();
    extractor.initialize().catch((err) => {
      console.error("Failed to initialize audio feature extractor:", err);
    });
    featureExtractorRef.current = extractor;

    // Initialize voice capture
    const capture = new VoiceCapture(
      { language, continuous: true, interimResults: true },
      {
        onTranscript: (result: TranscriptionResult) => {
          if (result.isFinal) {
            setTranscript((prev) => prev + " " + result.transcript);
            onTranscript?.(result.transcript, true);
            
            // Analyze emotions from transcript and audio features
            analyzeEmotions(result.transcript);
          } else {
            // Update interim results
            onTranscript?.(result.transcript, false);
          }
        },
        onError: (err: Error) => {
          setError(err.message);
          onError?.(err);
          toast({
            title: "Ses kaydı hatası",
            description: err.message,
            variant: "destructive",
          });
        },
        onStart: () => {
          setIsRecording(true);
          setIsPaused(false);
          startTimeRef.current = Date.now();
        },
        onStop: () => {
          setIsRecording(false);
        },
        onPause: () => {
          setIsPaused(true);
        },
        onResume: () => {
          setIsPaused(false);
        },
      }
    );

    voiceCaptureRef.current = capture;

    // Auto-start if requested
    if (autoStart) {
      handleStart();
    }

    // Cleanup
    return () => {
      capture.stop();
      extractor.stopAnalysis();
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, [language, autoStart, onTranscript, onError, onEmotionUpdate, toast]);

  const handleStart = useCallback(async () => {
    if (!voiceCaptureRef.current) {
      return;
    }

    try {
      // Request microphone permission
      const hasPermission = await VoiceCapture.requestPermission();
      if (!hasPermission) {
        throw new Error("Mikrofon erişimi reddedildi. Lütfen tarayıcı ayarlarından izin verin.");
      }

      // Get audio stream for feature extraction
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      // Start feature extraction
      if (featureExtractorRef.current) {
        await featureExtractorRef.current.startAnalysis(stream);
      }

      // Start voice capture
      await voiceCaptureRef.current.start();
      setError(null);
    } catch (err) {
      const error = err instanceof Error ? err : new Error("Failed to start recording");
      setError(error.message);
      onError?.(error);
      toast({
        title: "Kayıt başlatılamadı",
        description: error.message,
        variant: "destructive",
      });
    }
  }, [onError, toast]);

  const handleStop = useCallback(() => {
    voiceCaptureRef.current?.stop();
    featureExtractorRef.current?.stopAnalysis();
    
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop());
      streamRef.current = null;
    }
  }, []);

  const handlePause = useCallback(() => {
    voiceCaptureRef.current?.pause();
  }, []);

  const handleResume = useCallback(() => {
    voiceCaptureRef.current?.resume();
  }, []);

  const analyzeEmotions = useCallback((transcriptText: string) => {
    if (!featureExtractorRef.current) {
      return;
    }

    const duration = Date.now() - startTimeRef.current;
    const features = featureExtractorRef.current.getCurrentFeatures(transcriptText, duration);
    const emotions = extractEmotionIndicators(features);
    
    onEmotionUpdate?.(emotions);
  }, [onEmotionUpdate]);

  if (!isSupported) {
    return (
      <Card className="p-6">
        <div className="text-center text-muted-foreground">
          <p>Tarayıcınız ses tanıma özelliğini desteklemiyor.</p>
          <p className="text-sm mt-2">Lütfen Chrome, Edge veya Safari kullanın.</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Ses Kaydı</h3>
          <div className="flex gap-2">
            {!isRecording ? (
              <Button onClick={handleStart} size="sm">
                <Mic className="mr-2 h-4 w-4" />
                Başlat
              </Button>
            ) : (
              <>
                {isPaused ? (
                  <Button onClick={handleResume} size="sm" variant="outline">
                    <Play className="mr-2 h-4 w-4" />
                    Devam Et
                  </Button>
                ) : (
                  <Button onClick={handlePause} size="sm" variant="outline">
                    <Pause className="mr-2 h-4 w-4" />
                    Duraklat
                  </Button>
                )}
                <Button onClick={handleStop} size="sm" variant="destructive">
                  <Square className="mr-2 h-4 w-4" />
                  Durdur
                </Button>
              </>
            )}
          </div>
        </div>

        {isRecording && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <div className="h-2 w-2 bg-red-500 rounded-full animate-pulse" />
            <span>Kayıt yapılıyor...</span>
          </div>
        )}

        {error && (
          <div className="p-3 bg-destructive/10 text-destructive text-sm rounded">
            {error}
          </div>
        )}

        {transcript && (
          <div className="mt-4">
            <h4 className="text-sm font-medium mb-2">Transkript:</h4>
            <div className="p-3 bg-muted rounded text-sm max-h-40 overflow-y-auto">
              {transcript}
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}






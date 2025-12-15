"use client";

import React, { useEffect, useRef, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Mic,
  Square,
  Loader2,
  Waveform,
  User,
  ShieldAlert,
  CheckCircle2,
} from "lucide-react";

interface TelehealthVoiceToTextProps {
  sessionId?: string;
}

type RecordingStatus = "idle" | "recording" | "processing" | "error";

export default function TelehealthVoiceToText({ sessionId }: TelehealthVoiceToTextProps) {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const [status, setStatus] = useState<RecordingStatus>("idle");
  const [transcript, setTranscript] = useState<string>("");
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [progress, setProgress] = useState(0);
  const [speaker, setSpeaker] = useState<"patient" | "provider">("patient");
  const [localSessionId, setLocalSessionId] = useState(sessionId || "");
  const [riskDetected, setRiskDetected] = useState(false);
  const [durationSec, setDurationSec] = useState(0);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      const chunks: Blob[] = [];

      mediaRecorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };

      mediaRecorder.onstop = async () => {
        const blob = new Blob(chunks, { type: "audio/webm" });
        const url = URL.createObjectURL(blob);
        setAudioUrl(url);
        setStatus("processing");
        await mockTranscribe(blob);
        stream.getTracks().forEach((t) => t.stop());
      };

      mediaRecorder.start();
      setStatus("recording");
      setDurationSec(0);
      timerRef.current = setInterval(() => setDurationSec((s) => s + 1), 1000);
    } catch (error) {
      console.error("Recording error", error);
      setStatus("error");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && status === "recording") {
      mediaRecorderRef.current.stop();
      setStatus("processing");
      if (timerRef.current) clearInterval(timerRef.current);
    }
  };

  const mockTranscribe = async (audioBlob: Blob) => {
    // Mock progress
    setProgress(10);
    await new Promise((res) => setTimeout(res, 500));
    setProgress(45);
    await new Promise((res) => setTimeout(res, 500));
    setProgress(80);
    await new Promise((res) => setTimeout(res, 400));

    // Mock transcript text
    const mockText =
      "Hasta son haftalarda uyku problemlerinin arttığını, kaygı düzeyinin yükseldiğini ve zaman zaman çarpıntı hissettiğini belirtiyor.";
    setTranscript(mockText);
    setProgress(100);

    // Simple risk flag if certain keywords exist
    const riskKeywords = ["intihar", "self-harm", "kendime zarar", "ölmek"];
    const detected = riskKeywords.some((kw) => mockText.toLowerCase().includes(kw));
    setRiskDetected(detected);
    setStatus("idle");
  };

  const reset = () => {
    setTranscript("");
    setAudioUrl(null);
    setProgress(0);
    setRiskDetected(false);
    setStatus("idle");
    if (timerRef.current) clearInterval(timerRef.current);
    setDurationSec(0);
  };

  return (
    <Card className="border-blue-200 bg-blue-50/40">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Waveform className="h-5 w-5 text-blue-600" />
            Voice-to-Text (Tele-Seans)
          </CardTitle>
          {riskDetected && (
            <Badge variant="destructive" className="flex items-center gap-1">
              <ShieldAlert className="h-3 w-3" />
              Risk tespit edildi
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="text-sm font-semibold">Session ID</label>
            <Input
              value={localSessionId}
              onChange={(e) => setLocalSessionId(e.target.value)}
              placeholder="Seans ID girin"
              className="mt-1"
            />
          </div>
          <div>
            <label className="text-sm font-semibold">Konuşmacı</label>
            <div className="flex gap-2 mt-2">
              <Button
                variant={speaker === "patient" ? "default" : "outline"}
                size="sm"
                onClick={() => setSpeaker("patient")}
              >
                <User className="h-4 w-4 mr-1" />
                Danışan
              </Button>
              <Button
                variant={speaker === "provider" ? "default" : "outline"}
                size="sm"
                onClick={() => setSpeaker("provider")}
              >
                <User className="h-4 w-4 mr-1" />
                Terapist
              </Button>
            </div>
          </div>
          <div className="flex flex-col justify-end">
            <div className="text-xs text-gray-600 mb-1">
              Süre: {durationSec}s · Durum: {status === "recording" ? "Kaydediliyor" : status === "processing" ? "İşleniyor" : "Hazır"}
            </div>
            <div className="flex gap-2">
              <Button
                onClick={startRecording}
                disabled={status === "recording" || status === "processing"}
              >
                {status === "recording" ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Kaydediliyor
                  </>
                ) : (
                  <>
                    <Mic className="h-4 w-4 mr-2" />
                    Kayda Başla
                  </>
                )}
              </Button>
              <Button
                variant="destructive"
                onClick={stopRecording}
                disabled={status !== "recording"}
              >
                <Square className="h-4 w-4 mr-1" />
                Durdur
              </Button>
              <Button variant="outline" onClick={reset} disabled={status === "processing"}>
                Sıfırla
              </Button>
            </div>
          </div>
        </div>

        {status === "processing" && (
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span>Transkripsiyon işleniyor...</span>
              <span>%{progress}</span>
            </div>
            <Progress value={progress} />
          </div>
        )}

        {(transcript || audioUrl) && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Transkript</CardTitle>
              </CardHeader>
              <CardContent>
                {transcript ? (
                  <Textarea value={transcript} onChange={(e) => setTranscript(e.target.value)} rows={8} />
                ) : (
                  <p className="text-sm text-gray-500">Henüz transkript yok</p>
                )}
                {riskDetected && (
                  <div className="mt-2 text-xs text-red-600 flex items-center gap-1">
                    <ShieldAlert className="h-3 w-3" />
                    Kritik anahtar kelime tespit edildi. Seansı yakın takip edin.
                  </div>
                )}
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Kayıt</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {audioUrl ? (
                  <audio controls src={audioUrl} className="w-full" />
                ) : (
                  <p className="text-sm text-gray-500">Henüz kayıt yok</p>
                )}
                <div className="text-xs text-gray-500">
                  Not: Gerçek entegrasyonda kayıt buluta yüklenecek ve AssemblyAI/Whisper ile çözümlenecek.
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {status === "idle" && transcript && (
          <div className="flex items-center gap-2 text-sm text-green-700">
            <CheckCircle2 className="h-4 w-4" />
            Transkripsiyon tamamlandı. Kopyalayabilir veya notlara ekleyebilirsiniz.
          </div>
        )}
      </CardContent>
    </Card>
  );
}


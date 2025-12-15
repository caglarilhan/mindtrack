"use client";

import React, { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Mic, Square, Copy, Sparkles, Timer } from "lucide-react";

const loremStream = [
  "Hasta son haftalarda uykuya dalmakta zorlandığını belirtiyor.",
  "Yoğun iş temposu nedeniyle kaygı düzeyinin arttığını ifade ediyor.",
  "Sabahları yorgun uyanma şikayeti var.",
  "Aile içi destek aldığını, ancak stres yönetiminde zorlandığını söylüyor.",
  "Daha önce uygulanan nefes egzersizlerinin kısmen rahatlatıcı olduğunu belirtiyor.",
];

export default function SessionPage() {
  const [elapsed, setElapsed] = useState(0);
  const [recording, setRecording] = useState(false);
  const [transcripts, setTranscripts] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<"s" | "o" | "a" | "p">("s");

  // Timer
  useEffect(() => {
    const timer = setInterval(() => setElapsed((prev) => prev + 1), 1000);
    return () => clearInterval(timer);
  }, []);

  // Mock live transcript stream
  useEffect(() => {
    const interval = setInterval(() => {
      setTranscripts((prev) => {
        const nextLine = loremStream[prev.length % loremStream.length];
        return [...prev, nextLine];
      });
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  const formatTime = (seconds: number) => {
    const mm = String(Math.floor(seconds / 60)).padStart(2, "0");
    const ss = String(seconds % 60).padStart(2, "0");
    return `${mm}:${ss}`;
  };

  const handleCopy = (tab: string) => {
    const text = aiDrafts[tab] || "";
    navigator.clipboard.writeText(text).catch(() => {});
  };

  const handleAIDraft = (tab: string) => {
    // Mock AI edit
    aiDrafts[tab] = `AI güncelledi: ${aiDrafts[tab]}`;
    setDraftVersion((v) => v + 1);
  };

  const [draftVersion, setDraftVersion] = useState(0);
  const aiDrafts: Record<string, string> = {
    s: "Hasta yoğun kaygı ve uyku güçlüğü bildiriyor.",
    o: "Görünüm düzenli, göz teması yeterli, konuşma hızı normal.",
    a: "Yaygın Anksiyete Bozukluğu olasılığı; uyku hijyeni bozulmuş.",
    p: "CBT odaklı seanslar, günlük nefes egzersizi, uyku hijyeni eğitimi.",
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-3xl font-bold">Seans Asistanı</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left - Active Session */}
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Timer className="h-5 w-5 text-blue-600" />
              Aktif Seans
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-5xl font-bold tracking-tight text-center">{formatTime(elapsed)}</div>
            <div className="flex justify-center">
              <Button
                size="lg"
                variant={recording ? "destructive" : "default"}
                className={`gap-2 ${recording ? "animate-pulse" : ""}`}
                onClick={() => setRecording((r) => !r)}
              >
                {recording ? <Square className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                {recording ? "Kaydı Durdur" : "Ses Kaydını Başlat"}
              </Button>
            </div>
            <div className="space-y-2">
              <p className="text-sm font-semibold">Canlı Transkript</p>
              <div className="border rounded-lg h-72 bg-slate-50">
                <ScrollArea className="h-full p-3">
                  <div className="space-y-2 text-sm text-slate-700">
                    {transcripts.map((line, idx) => (
                      <div key={idx} className="leading-relaxed">
                        {line}
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Right - AI SOAP Notes */}
        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle>AI Notları (SOAP)</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as any)}>
              <TabsList className="grid grid-cols-4">
                <TabsTrigger value="s">S (Subjective)</TabsTrigger>
                <TabsTrigger value="o">O (Objective)</TabsTrigger>
                <TabsTrigger value="a">A (Assessment)</TabsTrigger>
                <TabsTrigger value="p">P (Plan)</TabsTrigger>
              </TabsList>
              {(["s", "o", "a", "p"] as const).map((tabKey) => (
                <TabsContent key={tabKey} value={tabKey} className="space-y-3">
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={() => handleAIDraft(tabKey)}>
                      <Sparkles className="h-4 w-4 mr-1" />
                      AI ile Düzenle
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleCopy(tabKey)}>
                      <Copy className="h-4 w-4 mr-1" />
                      Kopyala
                    </Button>
                  </div>
                  <div className="border rounded-lg bg-slate-50 p-3 text-sm text-slate-800 min-h-[140px]">
                    {aiDrafts[tabKey]}
                  </div>
                </TabsContent>
              ))}
            </Tabs>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}


"use client";

import React, { useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Input } from "@/components/ui/input";
import { Mic, Square, Copy, Sparkles, Timer, ShieldAlert, Trash2, Loader2, CheckCircle2 } from "lucide-react";

const loremStream = [
  "Hasta son haftalarda uykuya dalmakta zorlandığını belirtiyor.",
  "Yoğun iş temposu nedeniyle kaygı düzeyinin arttığını ifade ediyor.",
  "Sabahları yorgun uyanma şikayeti var.",
  "Aile içi destek aldığını, ancak stres yönetiminde zorlandığını söylüyor.",
  "Daha önce uygulanan nefes egzersizlerinin kısmen rahatlatıcı olduğunu belirtiyor.",
];

const riskKeywords = [
  "intihar",
  "kendime zarar",
  "self-harm",
  "öldürmek",
  "ölmek",
  "panik",
  "kriz",
  "şiddet",
  "kabus",
  "umutsuz",
  "kaygı",
  "çarpıntı",
];

export default function SessionPage() {
  const [elapsed, setElapsed] = useState(0);
  const [recording, setRecording] = useState(false);
  const [transcripts, setTranscripts] = useState<{ text: string; risk: boolean }[]>([]);
  const [risks, setRisks] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<"s" | "o" | "a" | "p">("s");
  const [soapLoading, setSoapLoading] = useState(false);
  const [soapGenerated, setSoapGenerated] = useState(false);

  // Timer
  useEffect(() => {
    let timer: NodeJS.Timeout | null = null;
    if (recording) {
      timer = setInterval(() => setElapsed((prev) => prev + 1), 1000);
    }
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [recording]);

  // Mock live transcript stream
  useEffect(() => {
    if (!recording) return;
    const interval = setInterval(() => {
      setTranscripts((prev) => {
        const nextLine = loremStream[prev.length % loremStream.length];
        const isRisk = riskKeywords.some((kw) => nextLine.toLowerCase().includes(kw));
        if (isRisk) {
          setRisks((r) => [...r, nextLine]);
        }
        return [...prev, { text: nextLine, risk: isRisk }];
      });
    }, 2200);
    return () => clearInterval(interval);
  }, [recording]);

  const formatTime = (seconds: number) => {
    const mm = String(Math.floor(seconds / 60)).padStart(2, "0");
    const ss = String(seconds % 60).padStart(2, "0");
    return `${mm}:${ss}`;
  };

  const [drafts, setDrafts] = useState<Record<"s" | "o" | "a" | "p", string>>({
    s: "Hasta yoğun kaygı ve uyku güçlüğü bildiriyor.",
    o: "Görünüm düzenli, göz teması yeterli, konuşma hızı normal.",
    a: "Yaygın Anksiyete Bozukluğu olasılığı; uyku hijyeni bozulmuş.",
    p: "CBT odaklı seanslar, günlük nefes egzersizi, uyku hijyeni eğitimi.",
  });

  const handleCopy = (tab: "s" | "o" | "a" | "p") => {
    const text = drafts[tab] || "";
    navigator.clipboard.writeText(text).catch(() => {});
  };

  const handleAIDraft = (tab: "s" | "o" | "a" | "p") => {
    setDrafts((prev) => ({
      ...prev,
      [tab]: `AI güncelledi: ${prev[tab]}`,
    }));
  };

  const riskBadge = useMemo(() => {
    if (risks.length === 0) return null;
    return (
      <div className="flex items-center gap-2 text-sm text-red-600">
        <ShieldAlert className="h-4 w-4" />
        {risks.length} riskli ifade tespit edildi
      </div>
    );
  }, [risks]);

  const generateSoap = async () => {
    setSoapLoading(true);
    setSoapGenerated(false);
    // Mock AI SOAP generation using transcripts
    await new Promise((res) => setTimeout(res, 2000));
    setDrafts({
      s: "Hasta yoğun kaygı, uyku güçlüğü ve çarpıntı bildirdi.",
      o: "Göz teması yeterli, konuşma hızı normal, afekt kaygılı.",
      a: "Olası GAD; uyku hijyeni bozulmuş; riskli ifadeler gözlendi.",
      p: "CBT seansları, günlük nefes egzersizi, uyku hijyeni; risk takibi ve gerekirse psikiyatri konsültasyonu.",
    });
    setSoapLoading(false);
    setSoapGenerated(true);
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
            <div className="flex justify-between items-center text-xs text-slate-500">
              <span>Canlı Transkript</span>
              <Button
                variant="ghost"
                size="sm"
                className="text-red-500"
                onClick={() => {
                  setTranscripts([]);
                  setRisks([]);
                  setSoapGenerated(false);
                }}
              >
                <Trash2 className="h-3 w-3 mr-1" />
                Temizle
              </Button>
            </div>
            {riskBadge}
            <div className="space-y-2">
              <div className="border rounded-lg h-72 bg-slate-50">
                <ScrollArea className="h-full p-3">
                  <div className="space-y-2 text-sm text-slate-700">
                    {transcripts.map((line, idx) => (
                      <div
                        key={idx}
                        className={`leading-relaxed ${line.risk ? "text-red-600 font-semibold" : ""}`}
                      >
                        {line.text}
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
            <div className="flex items-center justify-between">
              <CardTitle>AI Notları (SOAP)</CardTitle>
              <Button size="sm" onClick={generateSoap} disabled={soapLoading}>
                {soapLoading ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                    AI Oluşturuyor...
                  </>
                ) : (
                  "Seansı Bitir ve AI SOAP Oluştur"
                )}
              </Button>
            </div>
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
                      {drafts[tabKey]}
                  </div>
                </TabsContent>
              ))}
            </Tabs>
            {soapGenerated && (
              <div className="flex items-center gap-2 text-sm text-green-600">
                <CheckCircle2 className="h-4 w-4" />
                AI taslakları hazır. İnceleyip kopyalayabilirsiniz.
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}


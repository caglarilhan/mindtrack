"use client";

import React, { useCallback, useMemo, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Loader2, Wand2, Sparkles, Shuffle } from "lucide-react";
import ReactFlow, { Background, Controls, MiniMap, Node, Edge, BackgroundVariant } from "reactflow";
import "reactflow/dist/style.css";

type Gender = "male" | "female";

interface PersonNode {
  id: string;
  label: string;
  gender: Gender;
  position: { x: number; y: number };
}

interface RelationshipEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  type?: "default" | "conflict";
}

const initialNodes: Node[] = [];
const initialEdges: Edge[] = [];

export default function GenogramPage() {
  const [story, setStory] = useState("");
  const [loading, setLoading] = useState(false);
  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);
   // relation editor state
  const [relSource, setRelSource] = useState<string>("");
  const [relTarget, setRelTarget] = useState<string>("");
  const [relLabel, setRelLabel] = useState<string>("İlişki");
  const [relConflict, setRelConflict] = useState<boolean>(false);

  // Simple auto layout (grid)
  const applyLayout = useCallback((people: PersonNode[]): PersonNode[] => {
    if (people.length === 0) return people;
    const perRow = Math.max(3, Math.ceil(Math.sqrt(people.length)));
    const gapX = 200;
    const gapY = 150;
    return people.map((p, idx) => {
      const row = Math.floor(idx / perRow);
      const col = idx % perRow;
      return { ...p, position: { x: col * gapX + 50, y: row * gapY + 50 } };
    });
  }, []);

  // Mock parser: simulate AI extraction
  const runMockAnalysis = useCallback(async () => {
    setLoading(true);
    await new Promise((res) => setTimeout(res, 2000));

    // Basit kural: hikaye içinde "baba", "anne", "oğul", "kız" geçiyorsa kişi oluştur.
    const basePeople: PersonNode[] = [
      { id: "p1", label: "Ahmet (Baba)", gender: "male", position: { x: 0, y: 0 } },
      { id: "p2", label: "Ayşe (Anne)", gender: "female", position: { x: 0, y: 0 } },
      { id: "p3", label: "Mehmet (Oğul)", gender: "male", position: { x: 0, y: 0 } },
      { id: "p4", label: "Elif (Kız)", gender: "female", position: { x: 0, y: 0 } },
    ];

    const people = applyLayout(basePeople);

    const relations: RelationshipEdge[] = [
      { id: "e1", source: "p1", target: "p2", label: "Evli", type: "default" },
      { id: "e2", source: "p1", target: "p3", label: "Baba-Oğul", type: "default" },
      { id: "e3", source: "p2", target: "p3", label: "Anne-Oğul", type: "default" },
      { id: "e4", source: "p2", target: "p4", label: "Anne-Kız", type: "default" },
      { id: "e5", source: "p1", target: "p4", label: "Baba-Kız", type: "default" },
      { id: "e6", source: "p3", target: "p4", label: "Çatışmalı", type: "conflict" },
    ];

    const flowNodes: Node[] = people.map((p) => ({
      id: p.id,
      data: { label: p.label },
      position: p.position,
      style: {
        padding: 12,
        border: "2px solid",
        borderColor: p.gender === "male" ? "#2563eb" : "#ec4899",
        borderRadius: p.gender === "female" ? 20 : 4,
        background: "#fff",
        boxShadow: "0 10px 25px -15px rgba(0,0,0,0.35)",
        minWidth: 120,
        textAlign: "center",
        fontWeight: 600,
      },
    }));

    const flowEdges: Edge[] = relations.map((r) => ({
      id: r.id,
      source: r.source,
      target: r.target,
      label: r.label,
      animated: r.type === "conflict",
      style: {
        stroke: r.type === "conflict" ? "#ef4444" : "#94a3b8",
        strokeWidth: r.type === "conflict" ? 2.5 : 1.5,
      },
      labelStyle: {
        fill: r.type === "conflict" ? "#ef4444" : "#334155",
        fontWeight: 600,
        fontSize: 12,
      },
      markerEnd: {
        type: "arrowclosed",
      },
    }));

    setNodes(flowNodes);
    setEdges(flowEdges);
    setLoading(false);
    setRelSource("");
    setRelTarget("");
    setRelLabel("İlişki");
    setRelConflict(false);
  }, [applyLayout]);

  const handleAddRelation = useCallback(() => {
    if (!relSource || !relTarget || relSource === relTarget) return;
    const id = `e-${Date.now()}`;
    const newEdge: Edge = {
      id,
      source: relSource,
      target: relTarget,
      label: relLabel || "İlişki",
      animated: relConflict,
      style: {
        stroke: relConflict ? "#ef4444" : "#94a3b8",
        strokeWidth: relConflict ? 2.5 : 1.5,
      },
      labelStyle: {
        fill: relConflict ? "#ef4444" : "#334155",
        fontWeight: 600,
        fontSize: 12,
      },
      markerEnd: { type: "arrowclosed" },
    };
    setEdges((prev) => [...prev, newEdge]);
  }, [relSource, relTarget, relLabel, relConflict]);

  const handleAutoLayout = useCallback(() => {
    const people = nodes.map((n) => {
      const gender: Gender = n.style?.borderColor === "#2563eb" ? "male" : "female";
      return {
        id: n.id,
        label: String(n.data?.label || n.id),
        gender,
        position: { x: 0, y: 0 },
      };
    });
    const relaid = applyLayout(people);
    const nextNodes = relaid.map((p) => ({
      id: p.id,
      data: { label: p.label },
      position: p.position,
      style: {
        padding: 12,
        border: "2px solid",
        borderColor: p.gender === "male" ? "#2563eb" : "#ec4899",
        borderRadius: p.gender === "female" ? 20 : 4,
        background: "#fff",
        boxShadow: "0 10px 25px -15px rgba(0,0,0,0.35)",
        minWidth: 120,
        textAlign: "center",
        fontWeight: 600,
      },
    }));
    setNodes(nextNodes);
  }, [nodes, applyLayout]);

  const isStoryEmpty = useMemo(() => story.trim().length < 5, [story]);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">AI Genogram Builder</h1>
          <p className="text-gray-600 text-sm mt-1">
            Hikayeyi yaz, AI aile ağacını otomatik çizsin (mock).
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left Panel */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle>Hikaye Girişi</CardTitle>
            <CardDescription>
              Aile ilişkilerini, çatışmaları ve rol bilgilerini serbestçe yazın.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Textarea
              value={story}
              onChange={(e) => setStory(e.target.value)}
              placeholder="Örn: Ahmet ve Ayşe 15 yıldır evli. Mehmet 12 yaşında oğulları, Elif 9 yaşında kızları. Mehmet ile Elif arasında sık sık kavga oluyor..."
              rows={10}
              className="resize-none"
            />
            <Button
              onClick={runMockAnalysis}
              disabled={loading || isStoryEmpty}
              className="w-full"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  AI analiz ediyor...
                </>
              ) : (
                <>
                  <Wand2 className="h-4 w-4 mr-2" />
                  AI ile Analiz Et ve Çiz
                </>
              )}
            </Button>
            {isStoryEmpty && (
              <p className="text-xs text-amber-600">
                En az birkaç cümle yazın, AI anlamlandırabilsin (mock).
              </p>
            )}

            {/* Relation Editor */}
            {nodes.length > 0 && (
              <div className="border rounded-lg p-3 space-y-3 bg-slate-50">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold flex items-center gap-2">
                    <Sparkles className="h-4 w-4 text-blue-600" />
                    İlişki Ekle / Düzenle
                  </p>
                  <Button variant="outline" size="sm" onClick={handleAutoLayout}>
                    <Shuffle className="h-4 w-4 mr-1" />
                    Auto Layout
                  </Button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div>
                    <Label className="text-xs">Kaynak</Label>
                    <Select value={relSource} onValueChange={setRelSource}>
                      <SelectTrigger>
                        <SelectValue placeholder="Seçin" />
                      </SelectTrigger>
                      <SelectContent>
                        {nodes.map((n) => (
                          <SelectItem key={n.id} value={n.id}>
                            {String(n.data?.label || n.id)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label className="text-xs">Hedef</Label>
                    <Select value={relTarget} onValueChange={setRelTarget}>
                      <SelectTrigger>
                        <SelectValue placeholder="Seçin" />
                      </SelectTrigger>
                      <SelectContent>
                        {nodes.map((n) => (
                          <SelectItem key={n.id} value={n.id}>
                            {String(n.data?.label || n.id)}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label className="text-xs">İlişki Etiketi</Label>
                    <Input value={relLabel} onChange={(e) => setRelLabel(e.target.value)} />
                    <div className="mt-2 flex items-center gap-2">
                      <input
                        id="conflict"
                        type="checkbox"
                        checked={relConflict}
                        onChange={(e) => setRelConflict(e.target.checked)}
                      />
                      <Label htmlFor="conflict" className="text-xs">
                        Çatışmalı (kırmızı, animasyonlu)
                      </Label>
                    </div>
                  </div>
                </div>
                <Button size="sm" onClick={handleAddRelation} disabled={!relSource || !relTarget}>
                  İlişki Ekle
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Right Panel */}
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle>Genogram Canvas</CardTitle>
            <CardDescription>
              Erkek: kare (mavi), Kadın: yuvarlak (pembe). Çatışma kırmızı çizgi.
            </CardDescription>
          </CardHeader>
          <CardContent className="h-[640px]">
            <div className="w-full h-full border rounded-xl overflow-hidden">
              <ReactFlow
                nodes={nodes}
                edges={edges}
                fitView
                fitViewOptions={{ padding: 0.3 }}
                panOnScroll
                zoomOnScroll
                zoomOnPinch
              >
                <Background variant={BackgroundVariant.Dots} gap={16} size={1} />
                <MiniMap />
                <Controls />
              </ReactFlow>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}


"use client";

import React, { useCallback, useMemo, useRef, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Loader2, Wand2, Sparkles, Shuffle, ImageDown, Upload as UploadIcon, Info } from "lucide-react";
import ReactFlow, { Background, Controls, MiniMap, Node, Edge, BackgroundVariant } from "reactflow";
import "reactflow/dist/style.css";
import { toPng } from "html-to-image";

type Gender = "male" | "female";
type RelationType =
  | "married"
  | "divorced"
  | "partners"
  | "parent-child"
  | "conflict"
  | "cutoff"
  | "other";

interface PersonNode {
  id: string;
  label: string;
  gender: Gender;
  generation: number; // 0=üst kuşak, 1=ebeveyn, 2=çocuk vb.
  position: { x: number; y: number };
}

interface RelationshipEdge {
  id: string;
  source: string;
  target: string;
  label: string;
  relationType: RelationType;
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
  const [relType, setRelType] = useState<RelationType>("parent-child");

  // person editor state
  const [newPersonName, setNewPersonName] = useState<string>("");
  const [newPersonGender, setNewPersonGender] = useState<Gender>("male");
  const [newPersonGeneration, setNewPersonGeneration] = useState<number>(1);
  // LLM parse state (mock)
  const [extractedPeople, setExtractedPeople] = useState<PersonNode[]>([]);
  const [extractedRelations, setExtractedRelations] = useState<RelationshipEdge[]>([]);
  // export/import refs
  const flowWrapperRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const buildNode = useCallback((p: PersonNode): Node => {
    return {
      id: p.id,
      data: { label: p.label, gender: p.gender, generation: p.generation },
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
    };
  }, []);

  const buildEdge = useCallback((r: RelationshipEdge): Edge => {
    return {
      id: r.id,
      source: r.source,
      target: r.target,
      label: r.label,
      animated: r.relationType === "conflict",
      style: {
        stroke:
          r.relationType === "conflict"
            ? "#ef4444"
            : r.relationType === "cutoff"
            ? "#f97316"
            : r.relationType === "married"
            ? "#22c55e"
            : "#94a3b8",
        strokeWidth: r.relationType === "conflict" ? 2.5 : 1.5,
        strokeDasharray: r.relationType === "cutoff" ? "6 4" : undefined,
      },
      labelStyle: {
        fill: r.relationType === "conflict" ? "#ef4444" : "#334155",
        fontWeight: 600,
        fontSize: 12,
      },
      markerEnd: { type: "arrowclosed" },
    };
  }, []);

  // Simple auto layout (grid)
  const applyLayout = useCallback((people: PersonNode[]): PersonNode[] => {
    if (people.length === 0) return people;
    const grouped = people.reduce<Record<number, PersonNode[]>>((acc, p) => {
      acc[p.generation] = acc[p.generation] || [];
      acc[p.generation].push(p);
      return acc;
    }, {});

    const gapX = 200;
    const gapY = 160;
    const generations = Object.keys(grouped)
      .map((g) => Number(g))
      .sort((a, b) => a - b);

    const placed: PersonNode[] = [];
    generations.forEach((gen) => {
      const rowItems = grouped[gen];
      const perRow = Math.max(3, rowItems.length);
      rowItems.forEach((p, idx) => {
        const col = idx % perRow;
        placed.push({
          ...p,
          position: {
            x: col * gapX + 80,
            y: gen * gapY + 60,
          },
        });
      });
    });

    return placed;
  }, []);

  // Mock parser: simulate AI extraction
  const runMockAnalysis = useCallback(async () => {
    setLoading(true);
    await new Promise((res) => setTimeout(res, 2000));

    // Basit kural: hikaye içinde "baba", "anne", "oğul", "kız" geçiyorsa kişi oluştur.
    const basePeople: PersonNode[] = [
      { id: "p1", label: "Ahmet (Baba)", gender: "male", generation: 1, position: { x: 0, y: 0 } },
      { id: "p2", label: "Ayşe (Anne)", gender: "female", generation: 1, position: { x: 0, y: 0 } },
      { id: "p3", label: "Mehmet (Oğul)", gender: "male", generation: 2, position: { x: 0, y: 0 } },
      { id: "p4", label: "Elif (Kız)", gender: "female", generation: 2, position: { x: 0, y: 0 } },
    ];

    const people = applyLayout(basePeople);

    const relations: RelationshipEdge[] = [
      { id: "e1", source: "p1", target: "p2", label: "Evli", relationType: "married" },
      { id: "e2", source: "p1", target: "p3", label: "Baba-Oğul", relationType: "parent-child" },
      { id: "e3", source: "p2", target: "p3", label: "Anne-Oğul", relationType: "parent-child" },
      { id: "e4", source: "p2", target: "p4", label: "Anne-Kız", relationType: "parent-child" },
      { id: "e5", source: "p1", target: "p4", label: "Baba-Kız", relationType: "parent-child" },
      { id: "e6", source: "p3", target: "p4", label: "Çatışmalı", relationType: "conflict" },
    ];
    setExtractedPeople(people);
    setExtractedRelations(relations);
    setLoading(false);
    setRelSource("");
    setRelTarget("");
    setRelLabel("İlişki");
    setRelType("parent-child");
  }, [applyLayout]);

  const handleAddRelation = useCallback(() => {
    if (!relSource || !relTarget || relSource === relTarget) return;
    const id = `e-${Date.now()}`;
    const newEdge: Edge = {
      id,
      source: relSource,
      target: relTarget,
      label: relLabel || "İlişki",
      animated: relType === "conflict",
      style: {
        stroke:
          relType === "conflict"
            ? "#ef4444"
            : relType === "cutoff"
            ? "#f97316"
            : relType === "married"
            ? "#22c55e"
            : "#94a3b8",
        strokeWidth: relType === "conflict" ? 2.5 : 1.5,
        strokeDasharray: relType === "cutoff" ? "6 4" : undefined,
      },
      labelStyle: {
        fill: relType === "conflict" ? "#ef4444" : "#334155",
        fontWeight: 600,
        fontSize: 12,
      },
      markerEnd: { type: "arrowclosed" },
    };
    setEdges((prev) => [...prev, newEdge]);
  }, [relSource, relTarget, relLabel, relType]);

  const handleAutoLayout = useCallback(() => {
    const people = nodes.map((n) => {
      const gender: Gender = n.style?.borderColor === "#2563eb" ? "male" : "female";
      return {
        id: n.id,
        label: String(n.data?.label || n.id),
        gender,
        generation: Math.round((n.position.y - 60) / 160) || 1,
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

  const applyGraphFromExtracted = useCallback(() => {
    if (extractedPeople.length === 0) return;
    const laid = applyLayout(
      extractedPeople.map((p) => ({ ...p, position: { x: 0, y: 0 } }))
    );
    const flowNodes: Node[] = laid.map(buildNode);
    const flowEdges: Edge[] = extractedRelations.map(buildEdge);

    setNodes(flowNodes);
    setEdges(flowEdges);
  }, [extractedPeople, extractedRelations, applyLayout, buildNode, buildEdge]);

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
        {nodes.length > 0 && (
          <Button
            variant="outline"
            onClick={() => {
              const payload = { nodes, edges };
              const blob = new Blob([JSON.stringify(payload, null, 2)], {
                type: "application/json",
              });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "genogram.json";
              a.click();
              URL.revokeObjectURL(url);
            }}
          >
            JSON Dışa Aktar
          </Button>
        )}
      </div>

      <div className="flex flex-wrap gap-2">
        <Button
          variant="outline"
          onClick={async () => {
            if (!flowWrapperRef.current) return;
            try {
              const dataUrl = await toPng(flowWrapperRef.current, {
                cacheBust: true,
                pixelRatio: 2,
                backgroundColor: "#f8fafc",
              });
              const a = document.createElement("a");
              a.href = dataUrl;
              a.download = "genogram.png";
              a.click();
            } catch (err) {
              console.error("PNG export failed", err);
            }
          }}
        >
          <ImageDown className="h-4 w-4 mr-2" />
          PNG Dışa Aktar
        </Button>
        <Button
          variant="outline"
          onClick={() => {
            fileInputRef.current?.click();
          }}
        >
          <UploadIcon className="h-4 w-4 mr-2" />
          JSON Yükle
        </Button>
        <input
          ref={fileInputRef}
          type="file"
          accept="application/json"
          className="hidden"
          onChange={(e) => {
            const file = e.target.files?.[0];
            if (!file) return;
            const reader = new FileReader();
            reader.onload = () => {
              try {
                const parsed = JSON.parse(String(reader.result));
                // Yeni format: { people, relations }
                if (parsed.people && parsed.relations) {
                  const laid = applyLayout(
                    (parsed.people as PersonNode[]).map((p) => ({
                      ...p,
                      position: p.position || { x: 0, y: 0 },
                    }))
                  );
                  setNodes(laid.map(buildNode));
                  setEdges((parsed.relations as RelationshipEdge[]).map(buildEdge));
                } else if (parsed.nodes && parsed.edges) {
                  // Eski format: raw reactflow nodes/edges (infer gender/generation best-effort)
                  const inferredPeople: PersonNode[] = (parsed.nodes as Node[]).map((n) => ({
                    id: n.id,
                    label: String(n.data?.label || n.id),
                    gender:
                      (n.data as any)?.gender ||
                      (n.style?.borderColor === "#2563eb" ? "male" : "female"),
                    generation:
                      (n.data as any)?.generation !== undefined
                        ? (n.data as any).generation
                        : Math.round((n.position.y - 60) / 160) || 1,
                    position: n.position || { x: 0, y: 0 },
                  }));
                  const laid = applyLayout(inferredPeople);
                  setNodes(laid.map(buildNode));
                  setEdges((parsed.edges as any[]).map((e) => {
                    const relationType: RelationType =
                      e.relationType ||
                      (e.style?.stroke === "#22c55e"
                        ? "married"
                        : e.style?.stroke === "#ef4444"
                        ? "conflict"
                        : e.style?.stroke === "#f97316"
                        ? "cutoff"
                        : "other");
                    return buildEdge({
                      id: e.id,
                      source: e.source,
                      target: e.target,
                      label: e.label,
                      relationType,
                    });
                  }));
                } else {
                  alert("Geçersiz JSON");
                }
              } catch (err) {
                console.error(err);
                alert("JSON okunamadı");
              }
            };
            reader.readAsText(file);
          }}
        />
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
                  </div>
                  <div>
                    <Label className="text-xs">İlişki Tipi</Label>
                    <Select value={relType} onValueChange={(v) => setRelType(v as RelationType)}>
                      <SelectTrigger>
                        <SelectValue placeholder="Seçin" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="married">Evli</SelectItem>
                        <SelectItem value="divorced">Boşanmış</SelectItem>
                        <SelectItem value="partners">Birlikte</SelectItem>
                        <SelectItem value="parent-child">Ebeveyn-Çocuk</SelectItem>
                        <SelectItem value="conflict">Çatışmalı</SelectItem>
                        <SelectItem value="cutoff">Kopuk</SelectItem>
                        <SelectItem value="other">Diğer</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <Button size="sm" onClick={handleAddRelation} disabled={!relSource || !relTarget}>
                  İlişki Ekle
                </Button>
              </div>
            )}

            {/* Person Editor */}
            <div className="border rounded-lg p-3 space-y-3 bg-slate-50">
              <p className="text-sm font-semibold flex items-center gap-2">
                <Sparkles className="h-4 w-4 text-blue-600" />
                Kişi Ekle
              </p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <div>
                  <Label className="text-xs">Ad/Soyad</Label>
                  <Input
                    value={newPersonName}
                    onChange={(e) => setNewPersonName(e.target.value)}
                    placeholder="Örn: Ali"
                  />
                </div>
                <div>
                  <Label className="text-xs">Cinsiyet</Label>
                  <Select
                    value={newPersonGender}
                    onValueChange={(v) => setNewPersonGender(v as Gender)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Seçin" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="male">Erkek</SelectItem>
                      <SelectItem value="female">Kadın</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label className="text-xs">Kuşak</Label>
                  <Select
                    value={String(newPersonGeneration)}
                    onValueChange={(v) => setNewPersonGeneration(Number(v))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Seçin" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="0">Büyükbaba/Büyükanne</SelectItem>
                      <SelectItem value="1">Anne/Baba</SelectItem>
                      <SelectItem value="2">Çocuk</SelectItem>
                      <SelectItem value="3">Torun</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <Button
                size="sm"
                onClick={() => {
                  if (!newPersonName.trim()) return;
                  const id = `p-${Date.now()}`;
                  const next = [
                    ...nodes.map((n) => ({
                      id: n.id,
          label: String(n.data?.label || n.id),
          gender: (n.data as any)?.gender || (n.style?.borderColor === "#2563eb" ? "male" : "female"),
          generation:
            (n.data as any)?.generation !== undefined
              ? (n.data as any).generation
              : Math.round((n.position.y - 60) / 160) || 1,
                      position: { x: n.position.x, y: n.position.y },
                    })) as PersonNode[],
                    {
                      id,
                      label: newPersonName.trim(),
                      gender: newPersonGender,
                      generation: newPersonGeneration,
                      position: { x: 0, y: 0 },
                    },
                  ];
                  const laid = applyLayout(next);
                  setNodes(
                    laid.map((p) => ({
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
                    }))
                  );
                  setNewPersonName("");
                }}
              >
                Kişi Ekle
              </Button>
            </div>
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
            <div
              className="w-full h-full border rounded-xl overflow-hidden"
              ref={flowWrapperRef}
            >
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

      {/* LLM Extraction Review */}
      {extractedPeople.length > 0 && (
        <Card className="shadow-lg">
          <CardHeader>
            <CardTitle>LLM Çıkarımı (Onayla / Düzenle)</CardTitle>
            <CardDescription>
              Metinden çıkarılan kişiler ve ilişkiler. Düzenleyip “Onayla ve Çiz” ile canvas’a yansıtın.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="border rounded-lg p-3">
                <p className="text-sm font-semibold mb-2">Kişiler</p>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {extractedPeople.map((p, idx) => (
                    <div key={p.id} className="border rounded p-2 space-y-2 bg-white">
                      <Input
                        value={p.label}
                        onChange={(e) => {
                          const next = [...extractedPeople];
                          next[idx] = { ...p, label: e.target.value };
                          setExtractedPeople(next);
                        }}
                      />
                      <div className="flex gap-2">
                        <Select
                          value={p.gender}
                          onValueChange={(v) => {
                            const next = [...extractedPeople];
                            next[idx] = { ...p, gender: v as Gender };
                            setExtractedPeople(next);
                          }}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="male">Erkek</SelectItem>
                            <SelectItem value="female">Kadın</SelectItem>
                          </SelectContent>
                        </Select>
                        <Select
                          value={String(p.generation)}
                          onValueChange={(v) => {
                            const next = [...extractedPeople];
                            next[idx] = { ...p, generation: Number(v) };
                            setExtractedPeople(next);
                          }}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="0">Büyükanne/Büyükbaba</SelectItem>
                            <SelectItem value="1">Anne/Baba</SelectItem>
                            <SelectItem value="2">Çocuk</SelectItem>
                            <SelectItem value="3">Torun</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="border rounded-lg p-3">
                <p className="text-sm font-semibold mb-2">İlişkiler</p>
                <div className="space-y-2 max-h-64 overflow-y-auto">
                  {extractedRelations.map((r, idx) => (
                    <div key={r.id} className="border rounded p-2 space-y-2 bg-white">
                      <Input
                        value={r.label}
                        onChange={(e) => {
                          const next = [...extractedRelations];
                          next[idx] = { ...r, label: e.target.value };
                          setExtractedRelations(next);
                        }}
                      />
                      <div className="grid grid-cols-3 gap-2">
                        <Select
                          value={r.source}
                          onValueChange={(v) => {
                            const next = [...extractedRelations];
                            next[idx] = { ...r, source: v };
                            setExtractedRelations(next);
                          }}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Kaynak" />
                          </SelectTrigger>
                          <SelectContent>
                            {extractedPeople.map((p) => (
                              <SelectItem key={p.id} value={p.id}>
                                {p.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <Select
                          value={r.target}
                          onValueChange={(v) => {
                            const next = [...extractedRelations];
                            next[idx] = { ...r, target: v };
                            setExtractedRelations(next);
                          }}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Hedef" />
                          </SelectTrigger>
                          <SelectContent>
                            {extractedPeople.map((p) => (
                              <SelectItem key={p.id} value={p.id}>
                                {p.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <Select
                          value={r.relationType}
                          onValueChange={(v) => {
                            const next = [...extractedRelations];
                            next[idx] = { ...r, relationType: v as RelationType };
                            setExtractedRelations(next);
                          }}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="married">Evli</SelectItem>
                            <SelectItem value="divorced">Boşanmış</SelectItem>
                            <SelectItem value="partners">Birlikte</SelectItem>
                            <SelectItem value="parent-child">Ebeveyn-Çocuk</SelectItem>
                            <SelectItem value="conflict">Çatışmalı</SelectItem>
                            <SelectItem value="cutoff">Kopuk</SelectItem>
                            <SelectItem value="other">Diğer</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex justify-end">
              <Button onClick={applyGraphFromExtracted} disabled={extractedPeople.length === 0}>
                Onayla ve Çiz
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}


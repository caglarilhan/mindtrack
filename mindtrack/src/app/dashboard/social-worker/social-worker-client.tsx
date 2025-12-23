"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/components/ui/use-toast";
import { Textarea } from "@/components/ui/textarea";

interface CareTask {
  id: string;
  domain: string;
  title: string;
  description?: string | null;
  risk_level: string;
  status: string;
  region: string;
  due_date?: string | null;
  created_at: string;
}

interface CareHandoff {
  id: string;
  from_role: string;
  to_role: string;
  summary: string;
  status: string;
  created_at: string;
}

interface Props {
  clinicId: string;
  initialTasks: CareTask[];
  initialHandoffs: CareHandoff[];
}

const DOMAIN_LABELS: Record<string, string> = {
  housing: "Housing",
  employment: "Employment",
  education: "Education",
  finances: "Finances",
  legal: "Legal",
  family: "Family",
};

const RISK_BADGE: Record<string, string> = {
  low: "bg-emerald-100 text-emerald-800",
  medium: "bg-amber-100 text-amber-800",
  high: "bg-red-100 text-red-800",
};

const STATUS_COLUMN: Record<string, string> = {
  todo: "To-do",
  in_progress: "In Progress",
  done: "Done",
};

export default function SocialWorkerClient({ clinicId, initialTasks, initialHandoffs }: Props) {
  const { toast } = useToast();
  const [region, setRegion] = useState("us");
  const [domain, setDomain] = useState<string | "all">("all");
  const [tasks, setTasks] = useState<CareTask[]>(initialTasks);
  const [handoffs, setHandoffs] = useState<CareHandoff[]>(initialHandoffs);
  const [loading, setLoading] = useState(false);
  const [note, setNote] = useState("");

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ region, clinicId });
      const res = await fetch(`/api/social-worker/tasks?${params.toString()}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || "Görevler alınamadı");
      setTasks(data.tasks || []);
      setHandoffs(data.handoffs || []);
    } catch (error) {
      toast({ title: "Social worker verisi alınamadı", description: String(error), variant: "destructive" });
    } finally {
      setLoading(false);
    }
  }, [clinicId, region, toast]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const columns = useMemo(
    () => ({
      todo: tasks.filter((t) => t.status === "todo" && (domain === "all" || t.domain === domain)),
      in_progress: tasks.filter((t) => t.status === "in_progress" && (domain === "all" || t.domain === domain)),
      done: tasks.filter((t) => t.status === "done" && (domain === "all" || t.domain === domain)),
    }),
    [tasks, domain],
  );

  const handleMockNote = () => {
    if (!note.trim()) {
      toast({ title: "Not boş olamaz", variant: "destructive" });
      return;
    }
    toast({ title: "Handoff notu kaydedildi (mock)", description: note });
    setNote("");
  };

  return (
    <Tabs defaultValue="tasks" className="mt-4 space-y-4">
      <TabsList>
        <TabsTrigger value="tasks">Tasks</TabsTrigger>
        <TabsTrigger value="handoffs">Hand-offs</TabsTrigger>
      </TabsList>
      <TabsContent value="tasks" className="space-y-4">
        <div className="flex flex-wrap items-center gap-3">
          <Select value={region} onValueChange={setRegion}>
            <SelectTrigger className="w-36">
              <SelectValue placeholder="Region" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="us">US</SelectItem>
              <SelectItem value="eu">EU</SelectItem>
            </SelectContent>
          </Select>
          <Select value={domain} onValueChange={(v) => setDomain(v as any)}>
            <SelectTrigger className="w-44">
              <SelectValue placeholder="Domain" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All domains</SelectItem>
              {Object.entries(DOMAIN_LABELS).map(([key, label]) => (
                <SelectItem key={key} value={key}>
                  {label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button variant="outline" size="sm" onClick={refresh} disabled={loading}>
            {loading ? "Yükleniyor..." : "Refresh"}
          </Button>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {Object.entries(columns).map(([key, list]) => (
            <Card key={key} className="min-h-[200px]">
              <CardHeader>
                <CardTitle className="text-sm font-semibold">{STATUS_COLUMN[key] || key}</CardTitle>
                <CardDescription>{list.length} item</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {list.map((t) => (
                  <div key={t.id} className="rounded border p-2 text-xs space-y-1">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{t.title}</span>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-semibold ${RISK_BADGE[t.risk_level] || "bg-slate-100"}`}
                      >
                        {t.risk_level.toUpperCase()}
                      </span>
                    </div>
                    <p className="text-[11px] text-muted-foreground">{DOMAIN_LABELS[t.domain] || t.domain}</p>
                    {t.description && <p className="text-[11px] line-clamp-3">{t.description}</p>}
                  </div>
                ))}
                {list.length === 0 && <p className="text-xs text-muted-foreground">Kayıt yok.</p>}
              </CardContent>
            </Card>
          ))}
        </div>
      </TabsContent>
      <TabsContent value="handoffs" className="grid gap-4 md:grid-cols-[2fr,1fr]">
        <div className="space-y-3">
          {handoffs.length === 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-semibold">Handoff yok</CardTitle>
                <CardDescription>Clinician → Social worker handoff notları burada görünecek.</CardDescription>
              </CardHeader>
            </Card>
          )}
          {handoffs.map((h) => (
            <Card key={h.id}>
              <CardHeader>
                <CardTitle className="flex items-center justify-between text-sm">
                  <span>{h.summary.slice(0, 60)}...</span>
                  <Badge variant="outline">{h.status.toUpperCase()}</Badge>
                </CardTitle>
                <CardDescription>
                  {h.from_role} → {h.to_role} · {new Date(h.created_at).toLocaleString()}
                </CardDescription>
              </CardHeader>
            </Card>
          ))}
        </div>
        <div className="space-y-3">
          <Card>
            <CardHeader>
              <CardTitle>Yeni handoff notu (mock)</CardTitle>
              <CardDescription>Clinician ile koordinasyon için kısa özet.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2 text-sm">
              <Textarea
                rows={5}
                placeholder="Örnek: 'Evden atılma riski, housing ve legal aid için değerlendirme lütfen.'"
                value={note}
                onChange={(e) => setNote(e.target.value)}
              />
              <Button className="w-full" size="sm" onClick={handleMockNote}>
                Save (mock)
              </Button>
            </CardContent>
          </Card>
        </div>
      </TabsContent>
    </Tabs>
  );
}

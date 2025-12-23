"use client";

import { useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Plus, Trash2, RefreshCw, Play } from "lucide-react";

interface Rule {
  id?: string;
  name: string;
  trigger: Record<string, unknown>;
  conditions?: Record<string, unknown>[];
  actions: Record<string, unknown>[];
  enabled?: boolean;
}

interface AutomationBuilderProps {
  clinicId: string;
}

function emptyRule(): Rule {
  return {
    name: "Yeni kural",
    trigger: { event: "appointment.created" },
    conditions: [],
    actions: [{ type: "notify", channel: "email", template: "default" }],
    enabled: true,
  };
}

export function AutomationBuilder({ clinicId }: AutomationBuilderProps) {
  const [rules, setRules] = useState<Rule[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [testingRuleId, setTestingRuleId] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/automation?clinicId=${clinicId}`);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.error || "Kurallar alınamadı");
      }
      const data = await res.json();
      setRules(data?.rules || []);
    } catch (e: any) {
      setError(e?.message || "Hata oluştu");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [clinicId]);

  const addRule = () => setRules((r) => [...r, emptyRule()]);

  const updateRule = (idx: number, patch: Partial<Rule>) => {
    setRules((r) => r.map((rule, i) => (i === idx ? { ...rule, ...patch } : rule)));
  };

  const saveRule = async (rule: Rule) => {
    setLoading(true);
    setError(null);
    try {
      const payload = { ...rule, clinicId };
      const res = await fetch("/api/automation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.error || "Kural kaydedilemedi");
      }
      await load();
    } catch (e: any) {
      setError(e?.message || "Hata oluştu");
    } finally {
      setLoading(false);
    }
  };

  const testRule = async (rule: Rule) => {
    const ruleId = rule.id || `temp-${Date.now()}`;
    setTestingRuleId(ruleId);
    setError(null);
    try {
      const res = await fetch("/api/automation/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ruleId,
          trigger: rule.trigger,
          testData: {
            conditions: rule.conditions || []
          }
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.error || "Test başarısız");
      }
      const result = await res.json();
      alert(`Test başarılı!\n\nTrigger eşleşti: ${result.result.triggerMatched}\nAksiyonlar: ${result.result.actionsExecuted.length}\nSüre: ${result.result.executionTime}ms`);
    } catch (e: any) {
      setError(e?.message || "Test başarısız");
    } finally {
      setTestingRuleId(null);
    }
  };

  return (
    <Card>
      <CardHeader className="flex items-center justify-between">
        <div>
          <CardTitle>Automation Builder</CardTitle>
          <p className="text-sm text-muted-foreground">Trigger / condition / action tanımla</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={load} disabled={loading}>
            <RefreshCw className="h-4 w-4 mr-1" /> Yenile
          </Button>
          <Button size="sm" onClick={addRule}>
            <Plus className="h-4 w-4 mr-1" /> Yeni kural
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {error && <div className="text-sm text-red-600">{error}</div>}
        {rules.map((rule, idx) => (
          <div key={rule.id || idx} className="border rounded-md p-3 space-y-2 bg-white">
            <div className="flex items-center gap-2">
              <Input
                value={rule.name}
                onChange={(e) => updateRule(idx, { name: e.target.value })}
                placeholder="Kural adı"
              />
              <div className="flex items-center gap-2">
                <Switch
                  checked={rule.enabled ?? true}
                  onCheckedChange={(v) => updateRule(idx, { enabled: v })}
                  id={`enabled-${idx}`}
                />
                <Label htmlFor={`enabled-${idx}`} className="text-sm">Aktif</Label>
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="text-red-600 hover:text-red-700"
                onClick={() => setRules((r) => r.filter((_, i) => i !== idx))}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>

            <div className="grid md:grid-cols-3 gap-2">
              <div className="space-y-1">
                <Label className="text-xs">Trigger (JSON)</Label>
                <Textarea
                  value={JSON.stringify(rule.trigger || {}, null, 2)}
                  onChange={(e) => {
                    try {
                      updateRule(idx, { trigger: JSON.parse(e.target.value) });
                    } catch {}
                  }}
                  rows={4}
                />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Conditions (JSON[])</Label>
                <Textarea
                  value={JSON.stringify(rule.conditions || [], null, 2)}
                  onChange={(e) => {
                    try {
                      updateRule(idx, { conditions: JSON.parse(e.target.value) });
                    } catch {}
                  }}
                  rows={4}
                />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Actions (JSON[])</Label>
                <Textarea
                  value={JSON.stringify(rule.actions || [], null, 2)}
                  onChange={(e) => {
                    try {
                      updateRule(idx, { actions: JSON.parse(e.target.value) });
                    } catch {}
                  }}
                  rows={4}
                />
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Button size="sm" onClick={() => saveRule(rule)} disabled={loading}>
                Kaydet
              </Button>
              <Button 
                size="sm" 
                variant="outline" 
                onClick={() => testRule(rule)} 
                disabled={testingRuleId === (rule.id || `temp-${rules.indexOf(rule)}`)}
              >
                <Play className="h-3 w-3 mr-1" />
                Test
              </Button>
              {rule.enabled ? (
                <Badge variant="outline" className="text-xs text-emerald-700 border-emerald-300">Enabled</Badge>
              ) : (
                <Badge variant="outline" className="text-xs text-gray-700">Disabled</Badge>
              )}
            </div>
          </div>
        ))}

        {rules.length === 0 && <div className="text-sm text-muted-foreground">Henüz kural yok</div>}
      </CardContent>
    </Card>
  );
}


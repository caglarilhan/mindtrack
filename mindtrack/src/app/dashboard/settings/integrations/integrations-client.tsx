"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  PlugZap,
  ShieldAlert,
  RefreshCcw,
  CheckCircle2,
  AlertTriangle,
  Activity,
  Workflow,
} from "lucide-react";
import type {
  IntegrationCatalogItem,
  IntegrationConnection,
  IntegrationEventLog,
  AutomationRule,
} from "@/lib/server/integrations";

interface Props {
  clinicId: string;
  initialCatalog: IntegrationCatalogItem[];
  initialConnections: IntegrationConnection[];
  initialEvents: IntegrationEventLog[];
  initialRules: AutomationRule[];
}

const STATUS_BADGE: Record<string, string> = {
  connected: "bg-emerald-100 text-emerald-800",
  disconnected: "bg-slate-100 text-slate-700",
  needs_action: "bg-amber-100 text-amber-800",
  error: "bg-red-100 text-red-700",
};

export default function IntegrationsClient({ clinicId, initialCatalog, initialConnections, initialEvents, initialRules }: Props) {
  const [catalog] = useState(initialCatalog);
  const [connections, setConnections] = useState(initialConnections);
  const [events, setEvents] = useState(initialEvents);
  const [automationRules, setAutomationRules] = useState(initialRules);
  const [loadingSlug, setLoadingSlug] = useState<string | null>(null);
  const [rulePayload, setRulePayload] = useState({
    name: "High telehealth risk",
    triggerType: "telehealth_risk",
    conditionRegion: "us",
    actionChannel: "sms",
    actionTarget: "+15550109988",
    message: "High risk telehealth event tespit edildi",
    enabled: true,
  });
  const [ruleStatus, setRuleStatus] = useState<string | null>(null);

  const connectionFor = (slug: string) => connections.find((c) => c.integrationId === slug || c.id === slug || c.settings?.slug === slug);

  const handleConnect = async (slug: string) => {
    setLoadingSlug(slug);
    setRuleStatus(null);
    try {
      const current = connectionFor(slug);
      const nextStatus = current?.status === "connected" ? "disconnected" : "connected";
      const res = await fetch("/api/integrations/connect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ clinicId, integrationSlug: slug, status: nextStatus }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || "İşlem başarısız");
      setConnections((prev) => {
        const existing = prev.find((c) => c.integrationId === slug || c.id === slug);
        if (existing) {
          return prev.map((c) =>
            c.integrationId === existing.integrationId || c.id === existing.id
              ? { ...c, status: nextStatus }
              : c,
          );
        }
        return [
          ...prev,
          {
            id: crypto.randomUUID(),
            clinicId,
            integrationId: slug,
            status: nextStatus as IntegrationConnection["status"],
            settings: null,
          },
        ];
      });
    } catch (error) {
      setRuleStatus(error instanceof Error ? error.message : "Bağlantı hatası");
    } finally {
      setLoadingSlug(null);
    }
  };

  const handleSaveRule = async () => {
    setRuleStatus(null);
    try {
      const payload = {
        clinicId,
        name: rulePayload.name,
        trigger: { type: rulePayload.triggerType, severity: "high" },
        conditions: [
          { field: "region", operator: "equals", value: rulePayload.conditionRegion },
        ],
        actions: [
          { channel: rulePayload.actionChannel, target: rulePayload.actionTarget, message: rulePayload.message },
        ],
        enabled: rulePayload.enabled,
      };
      const res = await fetch("/api/automation/rules", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || "Kural kaydedilemedi");
      setAutomationRules((prev) => [
        {
          id: crypto.randomUUID(),
          clinicId,
          name: payload.name,
          trigger: payload.trigger,
          conditions: payload.conditions,
          actions: payload.actions,
          enabled: payload.enabled ?? true,
        },
        ...prev,
      ]);
      setRuleStatus("Kural kaydedildi ✅");
    } catch (error) {
      setRuleStatus(error instanceof Error ? error.message : "Kural kaydedilemedi");
    }
  };

  return (
    <Tabs defaultValue="marketplace" className="space-y-6">
      <TabsList>
        <TabsTrigger value="marketplace">Marketplace</TabsTrigger>
        <TabsTrigger value="events">Webhook Logs</TabsTrigger>
        <TabsTrigger value="automation">Automation</TabsTrigger>
      </TabsList>

      <TabsContent value="marketplace" className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2">
          {catalog.map((integration) => {
            const connection = connectionFor(integration.id) || connectionFor(integration.slug);
            const status = connection?.status || "disconnected";
            return (
              <Card key={integration.id}>
                <CardHeader className="flex flex-col gap-2">
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <PlugZap className="h-5 w-5 text-blue-600" />
                    {integration.name}
                  </CardTitle>
                  <CardDescription>{integration.description}</CardDescription>
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">{integration.category}</Badge>
                    <Badge className={STATUS_BADGE[status] || STATUS_BADGE.disconnected}>
                      {status.toUpperCase()}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="flex items-center gap-3">
                  <Button size="sm" onClick={() => handleConnect(integration.slug)} disabled={loadingSlug === integration.slug}>
                    {status === "connected" ? "Disconnect" : "Connect"}
                  </Button>
                  {integration.docsUrl && (
                    <Button size="sm" variant="outline" asChild>
                      <a href={integration.docsUrl} target="_blank" rel="noreferrer">
                        Docs
                      </a>
                    </Button>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
        {ruleStatus && (
          <Alert variant="default">
            <AlertTitle>Durum</AlertTitle>
            <AlertDescription>{ruleStatus}</AlertDescription>
          </Alert>
        )}
      </TabsContent>

      <TabsContent value="events" className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Webhook Events</CardTitle>
            <CardDescription>Son {events.length} event</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {events.length === 0 ? (
              <p className="text-sm text-muted-foreground">Event yok.</p>
            ) : (
              events.map((event) => (
                <div key={event.id} className="rounded border p-3 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{event.eventType}</span>
                    <Badge variant={event.status === "failed" ? "destructive" : "secondary"}>{event.status}</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {new Date(event.receivedAt).toLocaleString()} · #{event.id.slice(0, 8)}
                  </p>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </TabsContent>

      <TabsContent value="automation" className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle>Yeni Kural</CardTitle>
            <CardDescription>Risk eventlerine göre otomasyon tetikleyin</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Input
              value={rulePayload.name}
              onChange={(e) => setRulePayload((prev) => ({ ...prev, name: e.target.value }))}
              placeholder="Kural adı"
            />
            <div className="grid gap-3 md:grid-cols-2">
              <Select value={rulePayload.triggerType} onValueChange={(v) => setRulePayload((p) => ({ ...p, triggerType: v }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Trigger" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="telehealth_risk">Telehealth Risk</SelectItem>
                  <SelectItem value="integration_event">Integration Event</SelectItem>
                </SelectContent>
              </Select>
              <Select
                value={rulePayload.conditionRegion}
                onValueChange={(v) => setRulePayload((p) => ({ ...p, conditionRegion: v }))}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Bölge" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="us">US</SelectItem>
                  <SelectItem value="eu">EU</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <Select value={rulePayload.actionChannel} onValueChange={(v) => setRulePayload((p) => ({ ...p, actionChannel: v }))}>
                <SelectTrigger>
                  <SelectValue placeholder="Aksiyon" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="sms">SMS</SelectItem>
                  <SelectItem value="email">Email</SelectItem>
                  <SelectItem value="webhook">Webhook</SelectItem>
                </SelectContent>
              </Select>
              <Input
                value={rulePayload.actionTarget}
                onChange={(e) => setRulePayload((p) => ({ ...p, actionTarget: e.target.value }))}
                placeholder="Hedef (telefon/email/url)"
              />
            </div>
            <Textarea
              value={rulePayload.message}
              onChange={(e) => setRulePayload((p) => ({ ...p, message: e.target.value }))}
              placeholder="Mesaj"
            />
            <div className="flex items-center gap-2">
              <Switch
                checked={rulePayload.enabled}
                onCheckedChange={(checked) => setRulePayload((p) => ({ ...p, enabled: checked }))}
              />
              <span className="text-sm">Kural aktif</span>
            </div>
            <Button onClick={handleSaveRule}>
              <Workflow className="h-4 w-4 mr-2" />
              Kaydet
            </Button>
            {ruleStatus && (
              <p className="text-sm text-muted-foreground">{ruleStatus}</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Mevcut Kurallar</CardTitle>
            <CardDescription>{automationRules.length} kayıt</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {automationRules.length === 0 ? (
              <p className="text-sm text-muted-foreground">Henüz kural yok.</p>
            ) : (
              automationRules.map((rule) => (
                <div key={rule.id} className="rounded border p-3 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="font-medium">{rule.name}</span>
                    {rule.enabled ? (
                      <Badge className="bg-emerald-100 text-emerald-800">Active</Badge>
                    ) : (
                      <Badge variant="secondary">Disabled</Badge>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">
                    Trigger: {String(rule.trigger?.type || "custom")}
                  </p>
                </div>
              ))
            )}
          </CardContent>
        </Card>
      </TabsContent>
    </Tabs>
  );
}

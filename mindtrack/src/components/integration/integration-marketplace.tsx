"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { AlertCircle, CheckCircle2, RefreshCw, Zap, Search, Filter } from "lucide-react";

interface CatalogItem {
  id: string;
  slug: string;
  name: string;
  description: string;
  category: string;
  logoUrl?: string | null;
  authType: "oauth" | "api_key" | "webhook";
  docsUrl?: string | null;
}

interface Connection {
  integrationId: string;
  status: "connected" | "disconnected" | "needs_action" | "error";
  healthStatus?: string | null;
  errorMessage?: string | null;
  settings?: Record<string, unknown> | null;
}

interface MarketplaceProps {
  clinicId: string;
}

export function IntegrationMarketplace({ clinicId }: MarketplaceProps) {
  const [catalog, setCatalog] = useState<CatalogItem[]>([]);
  const [connections, setConnections] = useState<Record<string, Connection>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [apiKeys, setApiKeys] = useState<Record<string, string>>({});
  const [searchTerm, setSearchTerm] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/integrations/catalog?clinicId=${clinicId}`);
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.error || "Catalog alınamadı");
      }
      const data = await res.json();
      const connMap: Record<string, Connection> = {};
      (data.connections || []).forEach((c: any) => {
        connMap[c.integrationId] = c;
      });
      setCatalog(data.catalog || []);
      setConnections(connMap);
    } catch (e: any) {
      setError(e?.message || "Hata oluştu");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [clinicId]);

  const toggleConnection = async (item: CatalogItem, connect: boolean) => {
    setLoading(true);
    setError(null);
    try {
      const body: any = {
        clinicId,
        integrationSlug: item.slug,
        status: connect ? "connected" : "disconnected",
      };
      if (item.authType === "api_key" && connect) {
        body.settings = { apiKey: apiKeys[item.slug] || "" };
      }
      const res = await fetch("/api/integrations/connect", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.error || "Bağlantı güncellenemedi");
      }
      await load();
    } catch (e: any) {
      setError(e?.message || "Hata oluştu");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold">Integration Marketplace</h2>
          <p className="text-sm text-muted-foreground">Clinic: {clinicId}</p>
        </div>
        <Button variant="outline" size="sm" onClick={load} disabled={loading}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Yenile
        </Button>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-sm text-red-600">
          <AlertCircle className="h-4 w-4" /> {error}
        </div>
      )}

      {/* Search and Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Entegrasyon ara..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-3 py-2 border rounded-md"
            >
              <option value="all">Tüm Kategoriler</option>
              {Array.from(new Set(catalog.map(i => i.category))).map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border rounded-md"
            >
              <option value="all">Tüm Durumlar</option>
              <option value="connected">Bağlı</option>
              <option value="disconnected">Bağlı Değil</option>
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Filtered Catalog */}
      {(() => {
        const filtered = catalog.filter(item => {
          if (searchTerm) {
            const searchLower = searchTerm.toLowerCase();
            if (!item.name.toLowerCase().includes(searchLower) &&
                !item.description.toLowerCase().includes(searchLower) &&
                !item.category.toLowerCase().includes(searchLower)) {
              return false;
            }
          }
          if (filterCategory !== 'all' && item.category !== filterCategory) {
            return false;
          }
          if (filterStatus !== 'all') {
            const conn = connections[item.id] || connections[item.slug];
            const connected = conn?.status === "connected";
            if (filterStatus === 'connected' && !connected) return false;
            if (filterStatus === 'disconnected' && connected) return false;
          }
          return true;
        });

        return (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filtered.map((item) => {
          const conn = connections[item.id] || connections[item.slug];
          const connected = conn?.status === "connected";
          return (
            <Card key={item.slug} className="h-full flex flex-col">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {item.logoUrl ? (
                    <img src={item.logoUrl} alt={item.name} className="h-6 w-6 object-contain" />
                  ) : (
                    <Zap className="h-5 w-5 text-amber-500" />
                  )}
                  {item.name}
                </CardTitle>
                <CardDescription className="line-clamp-2">{item.description}</CardDescription>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col gap-3">
                <div className="flex items-center gap-2">
                  <Badge variant="outline">{item.category}</Badge>
                  <Badge variant="secondary">{item.authType}</Badge>
                  {connected ? (
                    <Badge variant="default" className="bg-emerald-600 text-white flex items-center gap-1">
                      <CheckCircle2 className="h-3 w-3" />
                      Connected
                    </Badge>
                  ) : (
                    <Badge variant="outline">Disconnected</Badge>
                  )}
                </div>
                {item.docsUrl && (
                  <a href={item.docsUrl} target="_blank" rel="noreferrer" className="text-xs text-blue-600 underline">
                    Dokümantasyon
                  </a>
                )}

                {item.authType === "api_key" && (
                  <div className="space-y-1">
                    <Label className="text-xs">API Key</Label>
                    <Input
                      value={apiKeys[item.slug] || ""}
                      onChange={(e) => setApiKeys((m) => ({ ...m, [item.slug]: e.target.value }))}
                      placeholder="API key girin"
                      type="password"
                    />
                  </div>
                )}

                <div className="mt-auto flex items-center gap-2">
                  <Button
                    size="sm"
                    variant={connected ? "outline" : "default"}
                    disabled={loading}
                    onClick={() => toggleConnection(item, !connected)}
                  >
                    {connected ? "Disconnect" : "Connect"}
                  </Button>
                  {conn?.healthStatus && (
                    <Badge variant="outline" className="text-xs">
                      Health: {conn.healthStatus}
                    </Badge>
                  )}
                  {conn?.errorMessage && (
                    <span className="text-[11px] text-red-500 truncate">{conn.errorMessage}</span>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
        {filtered.length === 0 && !loading && (
          <div className="text-sm text-muted-foreground col-span-full text-center py-8">
            {catalog.length === 0 ? 'Katalog boş' : 'Filtre kriterlerine uygun entegrasyon bulunamadı'}
          </div>
        )}
      </div>
      )})()}
    </div>
  );
}


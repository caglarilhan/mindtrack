"use client";

import { useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Checkbox } from "@/components/ui/checkbox";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import {
  AlertCircle,
  Check,
  Copy,
  Loader2,
  RefreshCcw,
  Shield,
  ShieldCheck,
  Trash2,
} from "lucide-react";

interface CaregiverTokenRecord {
  id: string;
  label: string;
  allowedRegions: string[];
  active: boolean;
  expiresAt: string | null;
  lastUsedAt: string | null;
  createdAt: string;
  updatedAt: string;
}

interface ApiTokenResponse {
  token: string;
  record: CaregiverTokenRecord;
}

const REGION_OPTIONS: { value: "us" | "eu"; label: string }[] = [
  { value: "us", label: "ABD" },
  { value: "eu", label: "Avrupa" },
];

export default function CaregiverTokensClient() {
  const [tokens, setTokens] = useState<CaregiverTokenRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [createOpen, setCreateOpen] = useState(false);
  const [label, setLabel] = useState("");
  const [expiresAt, setExpiresAt] = useState<string>("");
  const [regionState, setRegionState] = useState<Record<string, boolean>>({ us: true, eu: true });
  const [pendingAction, setPendingAction] = useState<string | null>(null);
  const [generatedToken, setGeneratedToken] = useState<string | null>(null);
  const [tokenDialogTitle, setTokenDialogTitle] = useState("Yeni Token");
  const [copied, setCopied] = useState(false);

  const allowedRegionValues = useMemo(() => {
    return REGION_OPTIONS.filter((opt) => regionState[opt.value]).map((opt) => opt.value);
  }, [regionState]);

  const resetForm = () => {
    setLabel("");
    setExpiresAt("");
    setRegionState({ us: true, eu: true });
  };

  const refreshTokens = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await fetch("/api/caregiver/tokens");
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || "Liste alınamadı");
      setTokens(data.tokens || []);
    } catch (err) {
      setError((err as Error).message || "Liste alınamadı");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshTokens();
  }, []);

  const handleCreate = async () => {
    try {
      setPendingAction("creating");
      const res = await fetch("/api/caregiver/tokens", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          label,
          allowedRegions: allowedRegionValues,
          expiresAt: expiresAt || null,
        }),
      });
      const data: ApiTokenResponse = await res.json();
      if (!res.ok) throw new Error((data as any)?.error || "Token oluşturulamadı");
      setGeneratedToken(data.token);
      setTokenDialogTitle(`${label} anahtarı`);
      setCreateOpen(false);
      resetForm();
      refreshTokens();
    } catch (err) {
      alert((err as Error).message || "Token oluşturulamadı");
    } finally {
      setPendingAction(null);
    }
  };

  const handleToggleActive = async (token: CaregiverTokenRecord, active: boolean) => {
    try {
      setPendingAction(`toggle-${token.id}`);
      const res = await fetch(`/api/caregiver/tokens/${token.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ active }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || "Durum güncellenemedi");
      setTokens((prev) => prev.map((item) => (item.id === token.id ? data.record : item)));
    } catch (err) {
      alert((err as Error).message || "Durum güncellenemedi");
    } finally {
      setPendingAction(null);
    }
  };

  const handleDelete = async (token: CaregiverTokenRecord) => {
    if (!confirm(`${token.label} tokenını silmek istediğine emin misin?`)) return;
    try {
      setPendingAction(`delete-${token.id}`);
      const res = await fetch(`/api/caregiver/tokens/${token.id}`, { method: "DELETE" });
      const data = await res.json();
      if (!res.ok) throw new Error(data?.error || "Token silinemedi");
      setTokens((prev) => prev.filter((item) => item.id !== token.id));
    } catch (err) {
      alert((err as Error).message || "Token silinemedi");
    } finally {
      setPendingAction(null);
    }
  };

  const handleRotate = async (token: CaregiverTokenRecord) => {
    try {
      setPendingAction(`rotate-${token.id}`);
      const res = await fetch(`/api/caregiver/tokens/${token.id}/rotate`, { method: "POST" });
      const data: ApiTokenResponse = await res.json();
      if (!res.ok) throw new Error((data as any)?.error || "Token yenilenemedi");
      setGeneratedToken(data.token);
      setTokenDialogTitle(`${token.label} · Yeni token`);
      setTokens((prev) => prev.map((item) => (item.id === token.id ? data.record : item)));
    } catch (err) {
      alert((err as Error).message || "Token yenilenemedi");
    } finally {
      setPendingAction(null);
    }
  };

  const activeCount = tokens.filter((t) => t.active).length;

  const renderTokenRow = (token: CaregiverTokenRecord) => {
    const status = token.active ? "Aktif" : "Pasif";
    const statusColor = token.active ? "bg-emerald-100 text-emerald-700" : "bg-slate-200 text-slate-600";
    const expires = token.expiresAt ? new Date(token.expiresAt).toLocaleString() : "Süresiz";
    const lastUsed = token.lastUsedAt ? new Date(token.lastUsedAt).toLocaleString() : "Kayıt yok";
    const pending = pendingAction?.includes(token.id);

    return (
      <Card key={token.id} className="border shadow-sm">
        <CardHeader className="flex flex-col gap-2 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <CardTitle className="text-lg flex items-center gap-2">
              <Shield size={18} className="text-emerald-500" />
              {token.label}
            </CardTitle>
            <CardDescription>
              Son kullanım: {lastUsed} · Oluşturulma: {new Date(token.createdAt).toLocaleString()}
            </CardDescription>
          </div>
          <div className="flex items-center gap-3">
            <Badge className={statusColor}>{status}</Badge>
            <div className="text-xs text-muted-foreground">Bitiş: {expires}</div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-2">
            {token.allowedRegions.map((region) => (
              <Badge key={region} variant="outline">
                {region === "us" ? "ABD" : "Avrupa"}
              </Badge>
            ))}
          </div>
          <div className="flex flex-wrap gap-3">
            <Button
              variant={token.active ? "default" : "outline"}
              size="sm"
              disabled={pending}
              onClick={() => handleToggleActive(token, !token.active)}
            >
              {pending && pendingAction === `toggle-${token.id}` ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : token.active ? (
                "Pasifleştir"
              ) : (
                "Aktifleştir"
              )}
            </Button>
            <Button
              variant="secondary"
              size="sm"
              disabled={pending}
              onClick={() => handleRotate(token)}
            >
              <RefreshCcw className="h-4 w-4 mr-2" />Yeniden Oluştur
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="text-red-600 hover:text-red-700"
              disabled={pending}
              onClick={() => handleDelete(token)}
            >
              <Trash2 className="h-4 w-4 mr-2" />Sil
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="space-y-6">
      <Card className="border border-emerald-100 bg-white shadow-sm">
        <CardHeader className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <CardTitle>Token Durumu</CardTitle>
            <CardDescription>
              Aktif anahtar: {activeCount} · Toplam giriş: {tokens.length} · Audit logları Supabase üzerinde saklanır.
            </CardDescription>
          </div>
          <div className="flex items-center gap-3">
            <Button onClick={() => setCreateOpen(true)}>Yeni Token Oluştur</Button>
            <Button variant="outline" onClick={refreshTokens} disabled={loading}>
              {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Yenile"}
            </Button>
          </div>
        </CardHeader>
      </Card>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Veri alınamadı</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {loading ? (
        <div className="flex items-center gap-3 text-muted-foreground">
          <Loader2 className="h-5 w-5 animate-spin" /> Veriler yükleniyor...
        </div>
      ) : tokens.length === 0 ? (
        <Card>
          <CardContent className="py-10 text-center space-y-3">
            <ShieldCheck className="h-10 w-10 text-emerald-500 mx-auto" />
            <p className="text-gray-600">Henüz tanımlı token yok. İlk anahtarı oluşturup caregiver API erişimini paylaşabilirsiniz.</p>
            <Button onClick={() => setCreateOpen(true)}>Token Oluştur</Button>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {tokens.map(renderTokenRow)}
        </div>
      )}

      <Dialog open={createOpen} onOpenChange={(open) => (open ? setCreateOpen(true) : setCreateOpen(false))}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Yeni Caregiver Token</DialogTitle>
            <DialogDescription>
              Token sadece bir kez gösterilir. Kopyalayıp güvenli şekilde paylaşmayı unutma.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Etiket</label>
              <Input value={label} onChange={(e) => setLabel(e.target.value)} placeholder="Örn. NYC CPS" />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Geçerlilik (opsiyonel)</label>
              <Input type="datetime-local" value={expiresAt} onChange={(e) => setExpiresAt(e.target.value)} />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">Bölge Yetkisi</label>
              <div className="flex gap-4">
                {REGION_OPTIONS.map((option) => (
                  <label key={option.value} className="flex items-center gap-2 text-sm">
                    <Checkbox
                      checked={regionState[option.value]}
                      onCheckedChange={(checked) =>
                        setRegionState((prev) => ({ ...prev, [option.value]: Boolean(checked) }))
                      }
                    />
                    {option.label}
                  </label>
                ))}
              </div>
            </div>
            <div className="flex items-center justify-end gap-3">
              <Button variant="outline" onClick={() => setCreateOpen(false)}>
                İptal
              </Button>
              <Button onClick={handleCreate} disabled={!label.trim() || pendingAction === "creating"}>
                {pendingAction === "creating" ? <Loader2 className="h-4 w-4 animate-spin" /> : "Oluştur"}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      <Dialog open={!!generatedToken} onOpenChange={(open) => (!open ? setGeneratedToken(null) : null)}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{tokenDialogTitle}</DialogTitle>
            <DialogDescription>Bu token sadece bir kez gösterilir. Güvenli yere kopyalayın.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <Alert>
              <AlertTitle>Erişim tokenı</AlertTitle>
              <AlertDescription className="break-all font-mono text-sm">{generatedToken}</AlertDescription>
            </Alert>
            <Button
              variant="secondary"
              className="w-full flex items-center justify-center gap-2"
              onClick={() => {
                if (!generatedToken) return;
                navigator.clipboard.writeText(generatedToken);
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
              }}
            >
              {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />} {copied ? "Kopyalandı" : "Kopyala"}
            </Button>
            <p className="text-xs text-muted-foreground">
              Tokenları Supabase CLI veya bu panelden gerektiğinde döndürebilirsin. Paylaştığın kişiden tokenı güvenli
              şekilde saklamasını iste.
            </p>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

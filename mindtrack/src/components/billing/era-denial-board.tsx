"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { AlertCircle, RefreshCw, ShieldAlert } from "lucide-react";
import { EraDenialActions } from "./era-denial-actions";

interface EraEvent {
  id: string;
  claim_number: string;
  code: string;
  description: string;
  amount: number;
  created_at: string;
}

interface ClaimItem {
  id: string;
  claim_number: string;
  patient_id: string;
  provider_id: string;
  status: string;
  updated_at: string;
  eraEvents?: EraEvent[];
}

export function EraDenialBoard() {
  const [items, setItems] = useState<ClaimItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/billing/era/denials");
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.error || "ERA denials alınamadı");
      }
      const data = await res.json();
      setItems(data?.claims || []);
    } catch (e: any) {
      setError(e?.message || "Hata oluştu");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <Card className="bg-white">
      <CardHeader className="flex flex-row items-center justify-between space-y-0">
        <div>
          <CardTitle className="text-lg">ERA Denial Board</CardTitle>
          <p className="text-sm text-muted-foreground">Denied / error durumundaki claim ve ERA event’leri</p>
        </div>
        <Button size="sm" variant="outline" onClick={load} disabled={loading}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Yenile
        </Button>
      </CardHeader>
      <CardContent>
        {error && (
          <div className="flex items-center gap-2 text-sm text-red-600 mb-3">
            <AlertCircle className="h-4 w-4" />
            {error}
          </div>
        )}
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Claim #</TableHead>
                <TableHead>Patient</TableHead>
                <TableHead>Provider</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Last Update</TableHead>
                <TableHead>ERA Events</TableHead>
                <TableHead>Aksiyon</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((c) => (
                <TableRow key={c.id}>
                  <TableCell className="font-mono text-xs">{c.claim_number}</TableCell>
                  <TableCell className="text-xs">{c.patient_id}</TableCell>
                  <TableCell className="text-xs">{c.provider_id}</TableCell>
                  <TableCell>
                    <Badge variant="destructive">{c.status}</Badge>
                  </TableCell>
                  <TableCell className="text-xs">{new Date(c.updated_at).toLocaleString()}</TableCell>
                  <TableCell className="text-xs">
                    <div className="space-y-1">
                      {(c.eraEvents || []).slice(0, 3).map((ev) => (
                        <div key={ev.id} className="flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">
                            {ev.code || "ERA"}
                          </Badge>
                          <span className="truncate">{ev.description}</span>
                          {ev.amount ? <span className="font-mono text-[11px] text-muted-foreground">${ev.amount}</span> : null}
                        </div>
                      ))}
                      {(c.eraEvents || []).length === 0 && <span className="text-muted-foreground">-</span>}
                    </div>
                  </TableCell>
                  <TableCell className="text-xs">
                    <EraDenialActions claimId={c.id} claimNumber={c.claim_number} onDone={load} />
                  </TableCell>
                </TableRow>
              ))}
              {items.length === 0 && !loading && (
                <TableRow>
                  <TableCell colSpan={7} className="text-center text-sm text-muted-foreground">
                    Kayıt yok
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}


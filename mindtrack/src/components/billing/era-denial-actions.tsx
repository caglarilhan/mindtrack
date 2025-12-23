"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { AlertCircle, Loader2, RotateCcw, Send } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface ActionProps {
  claimId: string;
  claimNumber: string;
  onDone?: () => void;
}

export function EraDenialActions({ claimId, claimNumber, onDone }: ActionProps) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState("");
  const [code, setCode] = useState("");
  const [description, setDescription] = useState("");

  const call = async (action: "resubmit" | "appeal") => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/api/billing/claims/${claimId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action, note, code, description }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err?.error || "İşlem başarısız");
      }
      if (onDone) onDone();
    } catch (e: any) {
      setError(e?.message || "Hata oluştu");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-2 border rounded-md p-3 bg-white">
      <div className="flex items-center gap-2">
        <Badge variant="outline" className="text-xs">Claim #{claimNumber}</Badge>
      </div>
      {error && (
        <div className="flex items-center gap-1 text-sm text-red-600">
          <AlertCircle className="h-4 w-4" /> {error}
        </div>
      )}
      <div className="grid grid-cols-2 gap-2">
        <Input
          placeholder="ERA/Appeal Code"
          value={code}
          onChange={(e) => setCode(e.target.value)}
        />
        <Input
          placeholder="Kısa açıklama"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>
      <Textarea
        placeholder="Not / gerekçe"
        value={note}
        onChange={(e) => setNote(e.target.value)}
        rows={3}
      />
      <div className="flex gap-2">
        <Button
          size="sm"
          variant="outline"
          disabled={loading}
          onClick={() => call("resubmit")}
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <RotateCcw className="h-4 w-4 mr-2" />}
          Resubmit
        </Button>
        <Button
          size="sm"
          disabled={loading}
          onClick={() => call("appeal")}
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Send className="h-4 w-4 mr-2" />}
          Appeal
        </Button>
      </div>
    </div>
  );
}










